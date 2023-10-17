import os
from functools import cached_property, lru_cache
from pathlib import Path

import marko
import requests
import yaml
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from markupsafe import Markup


def format_size(size: int) -> str:
    """Get the human-readable file size."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / 1024 ** 2:.2f} MB"


@lru_cache(None)
def get_github_stars(repository: str) -> str:
    url = repository.replace("https://github.com", "https://api.github.com/repos")
    resp = requests.get(url)
    stars_count = resp.json()["stargazers_count"]
    if stars_count > 1000:
        return f"{stars_count / 1000:.1f}k"
    return str(stars_count)


class ResumeRenderer:
    def __init__(self, minify: bool = False, path: str = "") -> None:
        self.root = Path(__file__).absolute().parent.parent
        self.data = self.root / "data"
        self.output_dir = self.root / "output"
        self.minify = minify
        self.path = path

    def get_url(self, path: str) -> str:
        if path.startswith("/"):
            return self.path + path
        return path

    def render_markdown(self, text: str) -> str:
        markdown = marko.Markdown(extensions=["gfm"])
        return Markup(markdown.convert(text))

    @cached_property
    def jinja_env(self) -> Environment:
        env = Environment(loader=FileSystemLoader(self.root / "templates"))
        env.filters["markdown"] = self.render_markdown
        env.globals["github_stars"] = get_github_stars
        env.globals["get_url"] = self.get_url
        return env

    def render(self, template_name: str = "main.html") -> None:
        self.output_dir.mkdir(exist_ok=True)
        self.copy_assets()

        for locale in self.data.iterdir():
            self._render_locale(locale, template_name)

    def copy_assets(self) -> None:
        assets_dir = self.root / "public"
        for dirpath, _, filenames in os.walk(assets_dir):
            for filename in filenames:
                file = Path(dirpath, filename)
                if file == assets_dir / "css/style.css":
                    continue
                output_file = self.output_dir / file.relative_to(assets_dir)
                output_file.parent.mkdir(exist_ok=True, parents=True)
                print(f"\x1b[32mCopying\x1b[0m {file.relative_to(assets_dir)} ...")
                output_file.write_bytes(file.read_bytes())

    def _render_locale(self, locale: Path, template_name: str) -> None:
        print(f"\x1b[32mBuilding\x1b[0m /{locale.name}/index.html ...")

        with open(locale / "main.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        template = self.jinja_env.get_template(template_name)
        output_html = self.output_dir / locale.name / "index.html"
        output_html.parent.mkdir(exist_ok=True, parents=True)
        locales = sorted(p.name for p in self.data.iterdir() if p.name != locale.name)

        with open(output_html, "w", encoding="utf-8") as f:
            f.write(template.render(data, other_locales=locales, lang=locale.name))

        # Get the file size of output html
        size = output_html.stat().st_size
        print(f" ↘ \x1b[32mSuccessful\x1b[0m, size: {format_size(size)}")
