"""Render local template parts without exposing their complete text to the agent."""

import argparse
import re
import sys
from pathlib import Path

INCLUDE = re.compile(r"(?m)^<!-- HS_TEMPLATE_INCLUDE: ([^\r\n]+) -->\n?")


def render_template(path, root=None, active=()):
    path = Path(path).resolve()
    root = Path(root).resolve() if root else path.parent
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError("Template include escapes template directory: " + str(path))
    if path in active:
        raise ValueError("Template include cycle: " + str(path))
    content = path.read_text(encoding="utf-8")

    def include(match):
        return render_template(path.parent / match.group(1), root, active + (path,))

    return INCLUDE.sub(include, content)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True)
    parser.add_argument("--output", required=True, help="New output file; existing files are not overwritten")
    args = parser.parse_args(argv)
    try:
        content = render_template(args.path)
        with Path(args.output).open("x", encoding="utf-8") as output:
            output.write(content)
        print("Rendered template: " + str(Path(args.output).resolve()))
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
