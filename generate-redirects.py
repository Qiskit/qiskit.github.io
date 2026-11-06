#!/usr/bin/env python3

"""Generates client-side redirects for a renamed Qiskit repository.

Why one file per page, rather than a single catch-all:

- GitHub Pages serves a custom 404 only from the root of the site, so an
  `<old-name>/404.html` would never be reached.
- A root `404.html` would be reached, but one page is shared by every rename,
  so it could only recover the requested path from `location.pathname` in
  JavaScript. A `meta refresh` there has a URL fixed at authoring time and
  cannot carry the path.

Mirroring the old site's paths keeps each URL fixed at generation time, so the
redirects work with JavaScript disabled. The cost is needing a list of pages;
see `find_page_paths`.
"""

from argparse import ArgumentParser
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from textwrap import dedent

BASE_URL = "https://qiskit.github.io"


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=(
            "Generate client-side redirects from a renamed Qiskit repository's "
            "old documentation URLs to its new ones."
        )
    )
    parser.add_argument("old_name", help="e.g. `qiskit-addon-sqd`")
    parser.add_argument("new_name", help="e.g. `qiskit-sqd`")
    return parser


def main() -> None:
    args = create_parser().parse_args()
    pages = find_page_paths(args.new_name)
    for page in pages:
        write_redirect_page(
            page=page, old_name=args.old_name, new_name=args.new_name
        )
    print(f"Wrote {len(pages)} redirects to {args.old_name}/")


def find_page_paths(new_name: str) -> list[Path]:
    """Lists every page of the new site, e.g. `apidocs/index.html`.

    The pages come from the `github-pages` artifact of the most recent
    successful docs build, which is the built site itself. Sphinx's
    `objects.inv` is not a substitute: it omits the `autosummary` stub pages,
    which are a third of the site.

    The old site cannot be the source here, because GitHub Pages serves
    nothing for a renamed repository and keeps no history of what it served.
    So a page that the rename dropped gets no redirect and keeps pointing at
    the old URL.
    """
    with TemporaryDirectory() as tmpdir:
        run(
            [
                "gh", "run", "download",
                "--repo", f"Qiskit/{new_name}",
                "--name", "github-pages",
                "--dir", tmpdir,
            ],
            check=True,
        )
        site = Path(tmpdir, "site")
        site.mkdir()
        run(["tar", "-xf", Path(tmpdir, "artifact.tar"), "-C", site], check=True)
        return sorted(p.relative_to(site) for p in site.rglob("*.html"))


def write_redirect_page(*, page: Path, old_name: str, new_name: str) -> None:
    """Writes one redirect page, mirroring the old site's path for it."""
    # This Sphinx build serves `.html` files rather than extensionless URLs, so
    # the path carries over as-is. Only a directory index is shortened, since
    # the new site resolves a bare directory to it.
    if page.name != "index.html":
        target = str(page)
    elif page.parent == Path("."):
        target = ""
    else:
        target = f"{page.parent}/"
    redirect_url = f"{BASE_URL}/{new_name}/{target}"

    # `meta refresh` keeps this working without JavaScript, so the URL has to
    # be fixed at generation time rather than derived from `location`.
    html = dedent(
        f"""\
        <!DOCTYPE HTML>
        <html lang="en-US">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="0; url={redirect_url}">
                <link rel="canonical" href="{redirect_url}">
                <title>Redirecting to {new_name}</title>
            </head>
            <body>
                <p><code>{old_name}</code> is now <code>{new_name}</code>.</p>
                <p>
                    If you are not redirected automatically, go to
                    <a href="{redirect_url}">{redirect_url}</a>.
                </p>
            </body>
        </html>
        """
    )
    dest = Path(old_name, page)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)


if __name__ == "__main__":
    main()
