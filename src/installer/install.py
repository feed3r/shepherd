# Copyright (c) 2025 Lunatic Fringers
#
# This file is part of Shepherd Core Stack
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from pathlib import Path
from typing import Any

import click

from installer.install_utils import (
    download_package,
    extract_package,
    get_os_info,
    install_packages,
    is_root,
    run_command,
)
from util import Util, constants

# Global variables to store command line options
verbose = False
skip_ensure_deps = False
install_method = "binary"
force_source_download = False

# Configuration variables
script_dir = Path(__file__).parent.resolve()
py_src_dir = (script_dir.parent / "src").resolve()

# Get environment variables with defaults
install_shepctl_dir = os.environ.get("INSTALL_SHEPCTL_DIR", "/opt/shepctl")
install_shepctl_dir = Path(install_shepctl_dir).resolve()
symlink_dir = os.environ.get("SYMLINK_DIR", "/usr/local/bin")
symlink_dir = Path(symlink_dir)


####################################################
# Parse command line options and define the context
@click.group()
@click.option(
    "-m",
    "--install-method",
    type=click.Choice(["binary", "source"]),
    default="binary",
    help="Specify the installation method (binary or source).",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode.")
@click.option(
    "-s",
    "--skip-deps",
    is_flag=True,
    help="Skip ensuring dependencies.",
)
@click.option(
    "-f",
    "--force-source-download",
    is_flag=True,
    help="Force source download during source installation.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    install_method: str,
    verbose: bool,
    skip_deps: bool,
    force_source_download: bool,
) -> None:
    """Shepherd Control Tool Installer"""
    if ctx.obj is None:
        ctx.obj = {}

    # Store options in context for subcommands
    ctx.obj["install_method"] = install_method
    ctx.obj["verbose"] = verbose
    ctx.obj["skip_deps"] = skip_deps
    ctx.obj["force_source_download"] = force_source_download


# Main install entrypoint
@cli.command()
@click.pass_context
def install(ctx: click.Context) -> None:
    """Install shepctl."""
    # Installer needs to run as root
    # to install system-wide
    if not is_root():
        Util.print_error_and_die("This script must be run as root")

    global verbose, skip_ensure_deps, install_method
    verbose = ctx.obj["verbose"]
    skip_ensure_deps = ctx.obj["skip_deps"]
    install_method = ctx.obj["install_method"]

    install_shepctl()


# Main uninstall entrypoint
@cli.command()
@click.pass_context
def uninstall(ctx: click.Context) -> None:
    """Uninstall shepctl."""
    if not is_root():
        Util.print_error_and_die("This script must be run as root")

    # Get options from context
    global verbose, skip_ensure_deps, install_method
    verbose = ctx.obj["verbose"]
    skip_ensure_deps = ctx.obj["skip_deps"]
    install_method = ctx.obj["install_method"]

    uninstall_shepctl()


def install_binary() -> None:
    """Install shepctl from binary release."""
    install_shepctl_dir: str = os.environ.get(
        "INSTALL_SHEPCTL_DIR", "/opt/shepctl"
    )

    version = os.environ.get("VER", "latest")
    url = constants.SHEPCTL_BINARY_URL.format(version=version)

    # Download the binary package
    Util.console.print(
        f"[bold blue]Downloading shepctl binary from {url}...[/bold blue]"
    )
    download_package(url, f"{install_shepctl_dir}/shepctl-{version}.tar.gz")

    Util.console.print("[bold blue]Extracting...[/bold blue]")
    extract_package(
        f"{install_shepctl_dir}/shepctl-{version}.tar.gz",
        str(install_shepctl_dir),
    )

    # Make the binary executable
    Util.console.print("[bold blue]Setting permissions...[/bold blue]")
    os.chmod(f"{install_shepctl_dir}/shepctl", 0o755)

    # Create symlink if it doesn't exist
    symlink_dir = Path(
        os.environ.get("SYMLINK_DIR", "/usr/local/bin")
    ).resolve()
    symlink_path = symlink_dir / "shepctl"
    if not symlink_path.exists():
        Util.console.print(
            f"[bold blue]Creating symlink in {symlink_dir}...[/bold blue]"
        )
        os.symlink(f"{install_shepctl_dir}/shepctl", symlink_path)


# OS packages dependency manager
def manage_dependencies() -> None:
    Util.console.print("Ensuring dependencies...", style="blue")

    os_info: Any = get_os_info()

    # Manage dependencies based on OS
    install_packages(
        os_info.distro,
        os_info.codename,
        install_method == "source",
    )


def manage_python_dependencies() -> None:
    # Install Python dependencies
    Util.console.print("Installing Python dependencies...", style="blue")

    # Save current directory
    original_dir = os.getcwd()
    os.chdir(install_shepctl_dir)

    try:
        # Use pip to install
        python_path = sys.executable
        run_command(
            [
                python_path,
                "-m",
                "pip",
                "install",
                "-e",
                f"{install_shepctl_dir}",
            ],
            check=True,
        )
    finally:
        # Restore original directory
        os.chdir(original_dir)


def should_download_sources(install_shepctl_dir: str) -> bool:
    """Check if sources should be downloaded."""
    if force_source_download:
        Util.console.print(
            "Forcing source download as per user request.",
            style="blue",
        )
        return True
    elif (
        not Path(install_shepctl_dir).exists()
        or not any(Path(install_shepctl_dir).iterdir())
        # The directory does not exist or is empty
    ):
        Util.console.print(
            f"Directory {install_shepctl_dir} does not exist or is empty. "
            "Downloading sources...",
            style="blue",
        )
        return True
    else:
        # The directory exists and is not empty, should not download again
        Util.console.print(
            f"Directory {install_shepctl_dir} already exists and is not empty."
            "Assuming existing installation.",
            style="red",
        )
        return False


def download_sources(install_shepctl_dir: str, version: str) -> None:
    Util.console.print(
        "Downloading and extracting source package", style="blue"
    )
    download_package(
        constants.SHEPCTL_SOURCE_URL.format(version=version),
        f"{install_shepctl_dir}/shepctl-{version}.tar.gz",
    )

    extract_package(
        f"{install_shepctl_dir}/shepctl-{version}.tar.gz",
        install_shepctl_dir,
    )


# Symbolic links management for source files
# (set to /usr/local/bin by default)
def manage_source_symlinks() -> None:
    bin_path: Path = Path(install_shepctl_dir) / "bin" / "shepctl"
    symlink_dir: Path = Path(
        os.environ.get("SYMLINK_DIR", "/usr/local/bin")
    ).resolve()
    symlink_path = symlink_dir / "shepctl"

    if symlink_path.exists():
        symlink_path.unlink()

    Util.console.print(f"Creating symlink in {symlink_dir}...", style="blue")
    os.symlink(str(bin_path), symlink_path)


# Shepherd source files installer (for development purposes)
def install_source() -> None:
    """Install shepctl from source."""
    install_shepctl_dir: str = os.environ.get(
        "INSTALL_SHEPCTL_DIR", "/opt/shepctl"
    )

    version = os.environ.get("VER", "latest")

    # Determine if sources should be downloaded.
    # This is done if explicitly asked from user
    # through a flag to forcefully download the
    # sources or if the sources directory does not
    # exist or is empty.
    if should_download_sources(install_shepctl_dir):
        download_sources(install_shepctl_dir, version)

    Util.console.print("Installing shepctl from source...", style="blue")

    if not skip_ensure_deps:
        manage_python_dependencies()

    # Create symlink if it doesn't exist
    manage_source_symlinks()
    Util.console.print("Source installation complete!", style="green")


def install_shepctl() -> None:
    """Install shepctl."""
    Util.console.print("Installing shepctl...", style="blue")

    if not skip_ensure_deps:
        manage_dependencies()

    # Clean existing installation if it exists
    if Path(install_shepctl_dir).exists():
        import shutil

        shutil.rmtree(Path(install_shepctl_dir))
    os.makedirs(Path(install_shepctl_dir), exist_ok=True)

    if install_method == "binary":
        install_binary()
    elif install_method == "source":
        install_source()
    else:
        Util.console.print(
            f"Error: Unknown install method '{install_method}'", style="red"
        )
        sys.exit(1)


def uninstall_shepctl() -> None:
    """Uninstall shepctl."""
    Util.console.print("Uninstalling shepctl...", style="blue")

    # Remove installation directory
    if Path(install_shepctl_dir).exists():
        import shutil

        shutil.rmtree(install_shepctl_dir)
        Util.print(f"Removed {install_shepctl_dir}")

    # Remove symlink
    symlink_path: Path = Path(symlink_dir) / "shepctl"
    if symlink_path.exists():
        symlink_path.unlink()
        Util.print(f"Removed symlink {symlink_path}")

    Util.print("shepctl uninstalled successfully")


if __name__ == "__main__":

    # Run the CLI
    cli()
