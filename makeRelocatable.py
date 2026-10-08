#!/usr/bin/env python3
"""Make an installed Orca build relocatable.

meson writes the absolute install prefix into some generated files, such as
bin/orca, orca_platform.py and orca_i18n.py. The asset is extracted wherever
@guidepup/setup installs it (a location the user can change), so a hard-coded
prefix points at a directory that doesn't exist, and Python silently falls
back to the system's Orca package.

This replaces each quoted occurrence of the prefix with one resolved at
runtime from the file's own location, so the build works from any directory.

usage: makeRelocatable.py <install dir> [<build prefix>]

<build prefix> is the --prefix the files were built with, and defaults to
<install dir>.
"""

import re
import sys
from pathlib import Path

PREFIX_VARIABLE = "_GUIDEPUP_ORCA_PREFIX"


def prefix_definition(depth: int) -> str:
    """Python that resolves the install prefix from the current file's location."""

    parents = ", ".join(['".."'] * depth)

    return (
        f"import os as _guidepup_os\n"
        f"{PREFIX_VARIABLE} = _guidepup_os.path.realpath(\n"
        f"    _guidepup_os.path.join(\n"
        f"        _guidepup_os.path.dirname(_guidepup_os.path.realpath(__file__)), {parents}\n"
        f"    )\n"
        f")\n"
    )


def is_python(path: Path, text: str) -> bool:
    return path.suffix == ".py" or (text.startswith("#!") and "python" in text.splitlines()[0])


def make_relocatable(install_dir: Path, build_prefix: str) -> list[Path]:
    literal = re.compile(r"""(['"])""" + re.escape(build_prefix) + r"""(/[^'"\n]*)?\1""")
    changed = []

    for path in sorted(install_dir.rglob("*")):
        if not path.is_file() or path.is_symlink() or "__pycache__" in path.parts:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if build_prefix not in text:
            continue

        if not is_python(path, text):
            sys.exit(f"error: build prefix in a non-Python file: {path}")

        def replace(match: re.Match) -> str:
            rest = match.group(2)

            if not rest:
                return PREFIX_VARIABLE

            return f'_guidepup_os.path.join({PREFIX_VARIABLE}, "{rest.lstrip("/")}")'

        lines = text.splitlines(keepends=True)
        first = next(index for index, line in enumerate(lines) if literal.search(line))

        if lines[first][:1].isspace():
            sys.exit(f"error: build prefix is not at module level in {path}:{first + 1}")

        depth = len(path.parent.relative_to(install_dir).parts)
        lines.insert(first, prefix_definition(depth))
        text = literal.sub(replace, "".join(lines))

        if build_prefix in text:
            sys.exit(f"error: build prefix still in {path} after replacing quoted occurrences")

        path.write_text(text, encoding="utf-8")
        changed.append(path)

        # Bytecode compiled from the old source would no longer match it.
        if path.suffix == ".py":
            for compiled in (path.parent / "__pycache__").glob(f"{path.stem}.*.pyc"):
                compiled.unlink()

    return changed


def main() -> None:
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)

    install_dir = Path(sys.argv[1]).resolve()
    build_prefix = sys.argv[2] if len(sys.argv) == 3 else str(install_dir)

    for path in make_relocatable(install_dir, build_prefix):
        print(f"made relocatable: {path.relative_to(install_dir)}")


if __name__ == "__main__":
    main()
