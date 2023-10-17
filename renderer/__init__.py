from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def build(__filename: Any = None, *, minify: bool = False, path: str = "") -> None:
    from renderer._core import ResumeRenderer

    renderer = ResumeRenderer(minify=minify, path=path)
    renderer.render()
    if minify:
        subprocess.run(
            [
                "tailwindcss",
                "-m",
                "-i",
                "public/css/style.css",
                "-o",
                "output/css/style.css",
            ]
        )


def copy_assets(filenames: str | None = None) -> None:
    for filename in filenames or []:
        if filename == "public/css/style.css":
            continue
        print(f"\x1b[32mCopying\x1b[0m {filename} ...")
        target_file = Path("output") / Path(filename).relative_to("public")
        target_file.parent.mkdir(exist_ok=True, parents=True)
        target_file.write_bytes(Path(filename).read_bytes())


def livereload() -> None:
    build()
    try:
        import livereload
    except ModuleNotFoundError:
        print("\x1b[31mError\x1b[0m: livereload is not installed.", file=sys.stderr)
        return
    server = livereload.Server()
    server.watch("templates/**/*.html", func=build)
    server.watch("data/**/*.yaml", func=build)
    server.watch("public/**/*", func=copy_assets)
    tw_proc = subprocess.Popen(
        [
            "tailwindcss",
            "-w",
            "-i",
            "public/css/style.css",
            "-o",
            "output/css/style.css",
        ]
    )
    try:
        server.serve(root="output/")
    except KeyboardInterrupt:
        tw_proc.terminate()
        tw_proc.wait()
        raise
