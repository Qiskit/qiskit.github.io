# qiskit.github.io

This repository allows us to set up client-side redirects in GitHub Pages for repositories that were renamed within the Qiskit organization.

The redirects live in this organization-level site rather than in a repository named after the project, so that they are served once no repository claims `qiskit.github.io/<old-name>`.

## How to add a renamed project

Add the old and new names to the `RENAMES` table in [`404.html`](404.html). This covers a whole documentation site per entry, but depends on JavaScript.

## Per-page redirects

```bash
./generate-redirects.py qiskit-addon-sqd qiskit-sqd
```

This writes one `meta refresh` page per page of the new site, so it does not depend on JavaScript, and it takes precedence over the `RENAMES` table. It requires the `gh` CLI.

Both methods assume that only the repository name changed.
