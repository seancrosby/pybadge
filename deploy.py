"""Copy pybadge files and user programs to an eBadge with mpremote.

Examples::

    python deploy.py --port COM3 --install-library examples/01_button_led.py
    python deploy.py --port COM3 examples/03_button_tone.py
    python deploy.py --port COM3 --asset byui-cse_badge.bmp examples/04_display_logo.py
"""

import argparse
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent


def build_command(port, install_library=False, program=None, assets=()):
    """Build the mpremote command that copies the requested files."""
    operations = []
    if install_library:
        operations.append([
            "fs",
            "cp",
            str(PROJECT_ROOT / "pybadge.py"),
            ":pybadge.py",
        ])
        operations.append([
            "fs",
            "cp",
            "-r",
            str(PROJECT_ROOT / "backends"),
            ":",
        ])

    if program is not None:
        operations.append(["fs", "cp", str(program), ":main.py"])

    if assets:
        operations.append([
            "fs",
            "cp",
            *[str(asset) for asset in assets],
            ":",
        ])

    command = [sys.executable, "-m", "mpremote", "connect", port]
    for index, operation in enumerate(operations):
        if index:
            command.append("+")
        command.extend(operation)
    return command


def _existing_file(parser, path, description):
    """Resolve a local file path and report a useful CLI error if missing."""
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        parser.error("{} does not exist or is not a file: {}".format(description, path))
    return resolved


def main():
    """Parse deployment options and run mpremote."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "program",
        nargs="?",
        type=Path,
        help="program to copy to the badge as /main.py",
    )
    parser.add_argument(
        "--port",
        default="auto",
        help="badge serial port (default: mpremote auto-detection)",
    )
    parser.add_argument(
        "--install-library",
        action="store_true",
        help="copy pybadge.py and the backends directory to the badge",
    )
    parser.add_argument(
        "--asset",
        action="append",
        default=[],
        type=Path,
        metavar="FILE",
        help="also copy a resource file to the badge root; repeat as needed",
    )
    args = parser.parse_args()

    if not args.install_library and args.program is None and not args.asset:
        parser.error("provide a program, an asset, or --install-library")

    program = None
    if args.program is not None:
        program = _existing_file(parser, args.program, "program")
    assets = [
        _existing_file(parser, asset, "asset")
        for asset in args.asset
    ]

    if args.install_library:
        for required in (PROJECT_ROOT / "pybadge.py", PROJECT_ROOT / "backends"):
            if not required.exists():
                parser.error("required library path is missing: {}".format(required))

    command = build_command(
        args.port,
        install_library=args.install_library,
        program=program,
        assets=assets,
    )
    try:
        result = subprocess.run(command, check=False)
    except KeyboardInterrupt:
        return 130
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
