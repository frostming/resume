import argparse
import os


def main():
    from . import build, livereload

    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", ""))
    args = parser.parse_args()

    if args.dev:
        livereload()
    else:
        build(path=args.base_url, minify=True)


if __name__ == "__main__":
    main()
