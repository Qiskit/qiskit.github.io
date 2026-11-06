# qiskit.github.io

This repository allows us to set up client-side redirects in GitHub Pages for repositories that were renamed within the Qiskit organization.

The redirects live in this organization-level site rather than in a repository named after the project, so that they are served once no repository claims `qiskit.github.io/<old-name>`.

## How to add a renamed project

```bash
./generate-redirects.py qiskit-addon-sqd qiskit-sqd
```

This writes one `meta refresh` page per page of the new site, so the redirects do not depend on JavaScript. It requires the `gh` CLI, since the page list comes from the new site's most recent `github-pages` artifact. This script assumes that only the repository name changed, so a page dropped by the rename gets no redirect.
