#!/usr/bin/env python3

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
import subprocess
import platform
import distro
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from constants import *

# Color constants (ANSI color codes)
RED = '\033[0;31m'
NC = '\033[0m'  # No Color
YELLOW = '\033[0;33m'
GREEN = '\033[0;32m'
BLUE = '\033[0;36m'


def print_color(message, color=NC):
    """Print a message with color."""
    print(f"{color}{message}{NC}")


def is_root():
    """Check if the script is running with root privileges."""
    return os.geteuid() == 0


def run_command(cmd, check=True, shell=False, capture_output=False):
    """Run a shell command and return the result.
    
    Args:
        cmd: Command to run (list or string)
        check: Whether to raise an exception on failure
        shell: Whether to run through shell
        capture_output: Whether to capture stdout/stderr
    
    Returns:
        CompletedProcess instance
    """
    if isinstance(cmd, str) and not shell:
        cmd = cmd.split()
    
    try:
        result = subprocess.run(
            cmd, 
            check=check, 
            shell=shell,
            text=True,
            capture_output=capture_output
        )
        return result
    except subprocess.CalledProcessError as e:
        print_color(f"Command failed: {e}", RED)
        if check:
            sys.exit(1)
        return e


def get_current_user():
    """Get the actual user, even when running with sudo."""
    return os.environ.get("SUDO_USER", os.getlogin())


def check_file_exists(path):
    """Check if a file exists and is accessible."""
    return os.path.isfile(path) and os.access(path, os.R_OK)


def check_package_installed(pkg_name):
    """Check if a Debian package is installed."""
    try:
        result = run_command(["dpkg", "-s", pkg_name], check=False, capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

def install_missing_packages(distro, missing_packages):
    cmd_list = INSTALL_COMMANDS[distro].copy()  # Create a copy of the list
    cmd_list.extend(missing_packages)  # Modify the copy
    run_command(cmd_list, check=True)  # Pass the modified list
    
def install_packages(distro):
    missing_packages = []
    for pkg in REQUIRED_PKGS:
        print(f"Checking for package: {pkg}")
        if not check_package_installed(pkg):
            print_color(f"Package {pkg} is missing.", YELLOW)
            missing_packages.append(pkg)
        else:
            print_color(f"Package {pkg} is already installed.", GREEN)

    if missing_packages:
        print_color(f"Missing packages: {', '.join(missing_packages)}", YELLOW)
        print_color("Installing missing packages...", BLUE)
        install_missing_packages(distro, missing_packages)
    else: 
        print_color("All required packages are already installed.", GREEN)
        
    missing_python_packages = []
    for pkg in REQUIRED_PYTHON_PKGS:
        print(f"Checking for Python package: {pkg}")
        if not check_package_installed(pkg):
            print_color(f"Python package {pkg} is missing.", YELLOW)
            missing_python_packages.append(pkg)
        else:
            print_color(f"Python package {pkg} is already installed.", GREEN)
    if missing_python_packages:
        print_color(f"Missing Python packages: {', '.join(missing_python_packages)}", YELLOW)
        print_color("Installing missing Python packages...", BLUE)
        install_missing_packages(distro, missing_python_packages)
    else:
        print_color("All required Python packages are already installed.", GREEN)    
        
        
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
