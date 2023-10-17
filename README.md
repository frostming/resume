# Resume of Frost Ming

Requires: [PDM](https://pdm.fming.dev) and Python >= 3.10

## Usage

Install dependencies

```
pdm install
```

Build static files

```
pdm run build
```

Run development server

```
pdm dev
```

Data files are in `data/` directory, and templates are in `templates/` directory.

If you want to serve the resume page under a subpath, you can set the `BASE_URL` environment variable or run:

```
pdm run build --base-url /subpath
```

## Tech

- [Jinja2](https://pypi.org/project/jinja2)
- [TailwindCSS](https://tailwindcss.com)
