"""Tag and publish a DelftDashboard release on GitHub.

Reads the version from ``src/delftdashboard/__init__.py`` (the single source
of truth) and then runs:

    git tag v<version>
    git push origin v<version>
    gh release create v<version> installer/dist_innosetup/DelftDashboard_Setup_<version>.exe
        --title "DelftDashboard <version>" --generate-notes

Usage (or use release_ddb.bat):
    python release_delftdashboard.py            # asks for confirmation
    python release_delftdashboard.py --yes      # no confirmation prompt
    python release_delftdashboard.py --dry-run  # show what would run, run nothing

Preflight checks (all must pass):
    * installer for this exact version exists in dist_innosetup
    * tag v<version> does not already exist (locally or on origin)
    * gh CLI is available and authenticated
    * warns when the working tree has uncommitted changes
"""

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
INIT_PY = REPO / "src" / "delftdashboard" / "__init__.py"


def read_version() -> str:
    """Return ``__version__`` from the package source."""
    match = re.search(
        r"^__version__\s*=\s*[\"']([^\"']+)[\"']", INIT_PY.read_text(), re.M
    )
    if not match:
        sys.exit(f"ERROR: __version__ not found in {INIT_PY}")
    return match.group(1)


def run(cmd: list, dry_run: bool = False, capture: bool = False, check: bool = True):
    """Run a command (in the repo root), echoing it first."""
    print(f"  > {' '.join(cmd)}")
    if dry_run:
        return None
    return subprocess.run(
        cmd, cwd=REPO, check=check, capture_output=capture, text=True
    )


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    assume_yes = "--yes" in sys.argv

    version = read_version()
    tag = f"v{version}"
    installer = HERE / "dist_innosetup" / f"DelftDashboard_Setup_{version}.exe"

    print(f"Version   : {version}   (from {INIT_PY.relative_to(REPO)})")
    print(f"Tag       : {tag}")
    print(f"Installer : {installer}")

    # --- Preflight checks ----------------------------------------------------
    errors = []

    if not installer.exists():
        errors.append(
            f"Installer not found: {installer}\n"
            "  Run build_ddb.bat and package_ddb.bat first (and check that the\n"
            "  packaged version matches __init__.py)."
        )
    else:
        size_mb = installer.stat().st_size / 1e6
        print(f"            ({size_mb:.0f} MB)")

    # Tag must not exist locally ...
    r = subprocess.run(
        ["git", "tag", "--list", tag], cwd=REPO, capture_output=True, text=True
    )
    if r.stdout.strip():
        errors.append(
            f"Tag {tag} already exists locally. Bump __version__ first, or delete\n"
            f"  the tag (git tag -d {tag}) if it was a mistake."
        )
    # ... nor on origin.
    r = subprocess.run(
        ["git", "ls-remote", "--tags", "origin", tag],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if r.returncode == 0 and r.stdout.strip():
        errors.append(f"Tag {tag} already exists on origin - bump __version__ first.")
    elif r.returncode != 0:
        errors.append("Could not reach origin (git ls-remote failed). Check network/VPN.")

    # gh CLI present and authenticated.
    r = subprocess.run(
        ["gh", "auth", "status"], cwd=REPO, capture_output=True, text=True
    )
    if r.returncode != 0:
        errors.append(
            "GitHub CLI not available or not logged in. Run: gh auth login"
        )

    if errors:
        print("\nPreflight FAILED:")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)

    # Uncommitted changes are allowed (the tag applies to HEAD), but warn.
    r = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True
    )
    if r.stdout.strip():
        print(
            "\nWARNING: the working tree has uncommitted changes. The tag will\n"
            "point at the last COMMIT - make sure the build you are releasing\n"
            "was made from committed code."
        )

    # --- Confirm ---------------------------------------------------------------
    if not assume_yes and not dry_run:
        answer = input(f"\nTag, push and publish release {tag}? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)

    # --- Do it -------------------------------------------------------------
    print()
    run(["git", "tag", tag], dry_run)
    run(["git", "push", "origin", tag], dry_run)
    # --generate-notes: without notes gh would prompt interactively.
    run(
        [
            "gh",
            "release",
            "create",
            tag,
            str(installer),
            "--title",
            f"DelftDashboard {version}",
            "--generate-notes",
        ],
        dry_run,
    )

    if dry_run:
        print("\nDry run - nothing was executed.")
    else:
        print(f"\nRelease {tag} published:")
        print(f"https://github.com/Deltares-research/DelftDashboard/releases/tag/{tag}")


if __name__ == "__main__":
    main()
