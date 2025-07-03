import getpass
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, List, Optional, Union

import distro

from util import Util, constants


def is_root() -> bool:
    """Check if the script is running with root privileges."""
    return os.geteuid() == 0


def run_command(
    cmd: Union[List[str], str],
    check: bool = True,
    shell: bool = False,
    capture_output: bool = False,
) -> Union[subprocess.CompletedProcess[Any], subprocess.CalledProcessError]:
    """Run a shell command and return the result.

    Args:
        cmd: Command to run (list or string)
        check: Whether to raise an exception on failure
        shell: Whether to run through shell
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess instance or CalledProcessError
    """
    if isinstance(cmd, str) and not shell:
        cmd = cmd.split()

    try:
        result = subprocess.run(
            cmd,
            check=check,
            shell=shell,
            text=True,
            capture_output=capture_output,
        )
        return result
    except subprocess.CalledProcessError as e:
        Util.console.print(f"Command failed: {e}", style="red")
        if check:
            sys.exit(1)
        return e


def get_current_user() -> str:
    """Get the actual user, even when running with sudo."""
    return os.environ.get("SUDO_USER") or _get_user_fallback()


def _get_user_fallback() -> str:
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()


def check_file_exists(path: str) -> bool:
    """Check if a file exists and is readable at the given path."""
    return os.path.isfile(path) and os.access(path, os.R_OK)


def install_missing_packages(
    distro: str, missing_packages: List[str], check: bool = True
) -> None:
    """Install missing packages using the appropriate package manager.

    Args:
        distro: The Linux distribution
        missing_packages: List of packages to install
        check: Whether to raise an exception on failure
    """
    if not missing_packages:
        Util.console.print("No packages to install", style="yellow")
        return

    cmd_list = constants.INSTALL_COMMANDS[distro].copy()
    cmd_list.extend(missing_packages)
    run_command(cmd_list, check=check)


def add_docker_repository(distro: str, codename: str) -> None:
    """Add the proper repository for the detected distribution."""
    if distro not in constants.REPO_STRINGS:
        raise RuntimeError(f"Unsupported distribution: {distro}")

    architecture = get_architecture()

    repo_string = constants.REPO_STRINGS[distro].format(
        architecture=architecture, release=codename
    )
    repo_path = constants.REPO_PATHS[distro]

    if os.path.exists(repo_path):
        return  # Exit early if the repository file already exists

    with open(repo_path, "w") as f:
        f.write(repo_string)

    update_command = constants.UPDATE_COMMANDS[distro].split()
    run_command(update_command, check=True)  # Update the package list
    Util.console.print("Repository added successfully.", style="green")


def install_docker_packages(distro: str, codename: str) -> None:
    """Install Docker packages using the appropriate package manager.

    Args:
        distro: The Linux distribution
        codename: The codename of the Linux distribution
    """
    if any(
        check_package_installed(pkg) for pkg in constants.REQUIRED_DOCKER_PKGS
    ):
        Util.console.print("Docker is already installed.", style="green")
        new_docker = False
    else:
        Util.console.print(
            "Docker is not installed. Installing...", style="yellow"
        )
        new_docker = True
        if not check_file_exists(constants.KEYRING_PATH):
            Util.console.print(
                "Docker keyring file is missing. Installing...", style="yellow"
            )
            run_command(
                [
                    "curl",
                    "-fsSL",
                    constants.GPG_KEYS[distro],
                    "| gpg --dearmor -o ",
                    constants.KEYRING_PATH,
                ],
                check=True,
            )
        else:
            Util.console.print(
                "Docker keyring file is already installed.", style="green"
            )

        if not check_file_exists(constants.REPO_PATHS[distro]):
            Util.console.print(
                "Docker repository is missing. Adding...", style="yellow"
            )
            add_docker_repository(distro, codename)
        else:
            Util.console.print(
                "Docker repository already exists.", style="green"
            )

        missing_packages: List[str] = []
        for pkg in constants.REQUIRED_DOCKER_PKGS:
            Util.console.print(
                f"Checking for package: {pkg}", style="blue"
            )  # Debug print
            if not check_package_installed(pkg):
                Util.console.print(f"Package {pkg} is missing.", style="yellow")
                missing_packages.append(pkg)
            else:
                Util.console.print(
                    f"Package {pkg} is already installed.", style="green"
                )

        Util.console.print(
            f"Missing packages: {missing_packages}"
        )  # Debug print

        if missing_packages:
            Util.console.print(
                f"Installing missing packages: {', '.join(missing_packages)}",
                style="blue",
            )
            install_missing_packages(distro, missing_packages, check=False)
        else:
            Util.console.print(
                "All required packages are already installed.", style="green"
            )

        docker_version = run_command(
            ["docker", "--version"], check=False, capture_output=True
        )
        Util.console.print(
            f"Docker version: {docker_version.stdout}", style="green"
        )
        docker_compose_version = run_command(
            ["docker-compose", "--version"], check=False, capture_output=True
        )
        Util.console.print(
            f"Docker Compose version: {docker_compose_version.stdout}",
            style="green",
        )
        if new_docker:
            run_command(["sudo", "systemctl", "enable", "docker"], check=True)
            run_command(["sudo", "groupadd", "-f", "docker"], check=True)
            running_user = get_current_user()
            run_command(["usermod", "-aG", "docker", running_user], check=True)
            print(
                f"Docker installed and user {running_user} "
                "added to docker group."
            )
            Util.console.print(
                "Please log out and back in for group membership to apply."
            )

        Util.console.print("Docker installation complete!", style="green")


def get_architecture() -> str:
    bits, linkage = platform.architecture()
    machine = platform.machine().lower()

    # First try the combination of bits and linkage
    if (bits, linkage) in constants.ARCH_MAPPING:
        return constants.ARCH_MAPPING[(bits, linkage)]

    # Fall back to machine type for ARM architectures
    if "arm" in machine or "aarch" in machine:
        return "arm64"

    # Default to amd64 for 64-bit systems, i386 for others
    return "amd64" if "64" in bits else "i386"


def install_required_packages(distro: str) -> None:
    """Install required packages for the detected distribution.

    Args:
        distro: The Linux distribution
    """
    missing_packages: List[str] = []
    for pkg in constants.REQUIRED_PKGS:
        if not check_package_installed(pkg):
            Util.console.print(f"Package {pkg} is missing.", style="yellow")
            missing_packages.append(pkg)
        else:
            Util.console.print(
                f"Package {pkg} is already installed.", style="green"
            )

    if missing_packages:
        Util.console.print(
            f"Installing missing packages: {', '.join(missing_packages)}",
            style="blue",
        )
        install_missing_packages(distro, missing_packages)
    else:
        Util.console.print(
            "All required packages are already installed.", style="green"
        )


def install_python_packages(distro: str) -> None:
    """Install Python packages using the appropriate package manager.

    Args:
        distro: The Linux distribution
    """
    # Ensure Python >= 3.12 is installed
    executed_python_version = run_command(
        ["python3", "--version"], check=False, capture_output=True
    )
    python_version = executed_python_version.stdout.split()[1]
    major, minor, _ = map(int, python_version.split("."))
    if major < 3 or (major == 3 and minor < 12):
        Util.console.print(
            "Python version is less than 3.12. Going to update", style="yellow"
        )
        install_missing_packages(distro, ["python3"])
    else:
        Util.console.print(
            "Python version is 3.12 or greater. No need to update",
            style="green",
        )

    missing_python_packages: List[str] = []
    for pkg in constants.REQUIRED_PYTHON_PKGS:
        if not check_package_installed(pkg):
            Util.console.print(
                f"Python package {pkg} is missing.", style="yellow"
            )
            missing_python_packages.append(pkg)
        else:
            Util.console.print(
                f"Python package {pkg} is already installed.", style="green"
            )

    if missing_python_packages:
        Util.console.print(
            (
                "Installing missing Python packages: "
                f"{', '.join(missing_python_packages)}"
            ),
            style="blue",
        )
        install_missing_packages(distro, missing_python_packages)
    else:
        Util.console.print(
            "All required Python packages are already installed.", style="green"
        )


def install_packages(distro: str, codename: str, install_source: bool) -> None:
    install_required_packages(distro)
    if install_source:
        install_python_packages(distro)
    install_docker_packages(distro, codename)


@dataclass
class OsInfo:
    """Structured information about the operating system."""

    system: str
    distro: Optional[str] = None
    codename: Optional[str] = None


def get_os_info() -> OsInfo:
    """
    Identifies the operating system type, distribution, and codename.

    Returns:
        OsInfo: A dataclass containing system type, distribution, and codename

    Raises:
        ValueError: If the operating system is not supported
    """
    system = platform.system().lower()

    if system in ("windows", "win32", "darwin"):
        raise ValueError(f"Unsupported operating system: {system}")

    elif system == "linux":
        dist_id = distro.id().lower()
        code_name = distro.codename().lower()
        return OsInfo(system=system, distro=dist_id, codename=code_name)

    # Fallback for other systems
    return OsInfo(system=system)


def check_package_installed(pkg: str) -> bool:
    """Check if a package is installed using dpkg."""
    try:
        result = run_command(
            ["dpkg", "-s", pkg],
            check=False,
            capture_output=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def download_package(url: str, dest: str) -> None:
    """Download a package from a URL to a destination path."""
    run_command(["curl", "-fsSL", url, "-o", dest], check=True)
    Util.console.print(f"Package downloaded to {dest}", style="green")


def extract_package(package_path: str, extract_to: str) -> None:
    """Extract a tar.gz package to a specified directory."""
    run_command(["tar", "-xzf", package_path, "-C", extract_to], check=True)
    Util.console.print(f"Package extracted to {extract_to}", style="green")
