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
from dataclasses import dataclass


@dataclass(frozen=True)
class Constants:
    """Constants for the application."""

    # Configuration and environment variables

    SHPD_CONFIG_VALUES_FILE: str
    SHPD_DIR: str

    @property
    def SHPD_CONFIG_FILE(self) -> str:
        return os.path.join(self.SHPD_DIR, ".shpd.json")

    @property
    def SHPD_ENVS_DIR(self) -> str:
        return os.path.join(self.SHPD_DIR, "envs")

    @property
    def SHPD_ENV_IMGS_DIR(self) -> str:
        return os.path.join(self.SHPD_DIR, ".env_imgs")

    @property
    def SHPD_CERTS_DIR(self) -> str:
        return os.path.join(self.SHPD_DIR, ".certs")

    @property
    def SHPD_SSH_DIR(self) -> str:
        return os.path.join(self.SHPD_DIR, ".ssh")

    @property
    def SHPD_SSHD_DIR(self) -> str:
        return os.path.join(self.SHPD_DIR, ".sshd")

    # Application metadata

    APP_NAME: str = "shepctl"
    APP_VERSION: str = "0.0.0"
    APP_AUTHOR: str = "Lunatic Fringers"
    APP_LICENSE: str = "MIT"
    APP_URL: str = "https://github.com/LunaticFringers/shepherd"

    # Environment types

    ENV_TYPE_DOCKER_COMPOSE: str = "docker-compose"

    # Service types

    SVC_TYPE_DOCKER: str = "docker"


# Installer and system constants

# List of required system packages for Shepherd installation
REQUIRED_PKGS: list[str] = [
    "bc",
    "jq",
    "curl",
    "rsync",
    "apt-transport-https",
    "ca-certificates",
    "software-properties-common",
    "gnupg",
    "lsb-release",
]

# List of required Python packages for Shepherd
REQUIRED_PYTHON_PKGS: list[str] = ["python3-venv", "python3-pip"]

# List of required Docker-related packages
REQUIRED_DOCKER_PKGS: list[str] = [
    "docker.io",
    "docker-ce",
    "docker-ce-cli",
    "containerd.io",
    "docker-compose",
    "docker-compose-plugin",
]

# Mapping of distro names to install commands for system packages
INSTALL_COMMANDS: dict[str, list[str]] = {
    "debian": ["sudo", "apt-get", "install", "-y"],
    "ubuntu": ["sudo", "apt-get", "install", "-y"],
}

# Mapping of distro names to update commands for package lists
UPDATE_COMMANDS: dict[str, str] = {
    "debian": "sudo apt update",
    "ubuntu": "sudo apt update",
}

# Mapping of distro names to Docker GPG key URLs
GPG_KEYS: dict[str, str] = {
    "debian": "https://download.docker.com/linux/debian/gpg",
    "ubuntu": "https://download.docker.com/linux/ubuntu/gpg",
}

# Mapping of distro names to Docker repository file paths
REPO_PATHS: dict[str, str] = {
    "debian": "/etc/apt/sources.list.d/docker.list",
    "ubuntu": "/etc/apt/sources.list.d/docker.list",
}

# Mapping of distro names to Docker repository configuration strings
REPO_STRINGS: dict[str, str] = {
    "debian": (
        "deb [arch={architecture} signed-by=/usr/share/keyrings/"
        "docker-archive-keyring.gpg] "
        "https://download.docker.com/linux/debian "
        "{release} stable"
    ),
    "ubuntu": (
        "deb [arch={architecture} signed-by=/usr/share/keyrings/"
        "docker-archive-keyring.gpg] "
        "https://download.docker.com/linux/ubuntu "
        "{release} stable"
    ),
}

# Path to Docker's keyring file
KEYRING_PATH: str = "/usr/share/keyrings/docker-archive-keyring.gpg"

# Mapping of (architecture, linkage) to Docker architecture strings
ARCH_MAPPING: dict[tuple[str, str], str] = {
    ("32bit", "ELF"): "i386",
    ("64bit", "ELF"): "amd64",
    ("32bit", "WindowsPE"): "i386",
    ("64bit", "WindowsPE"): "amd64",
    ("64bit", "Mach-O"): "amd64",
    ("arm", ""): "arm64",
    ("aarch64", ""): "arm64",
}

# URL template for downloading shepctl source tarballs
SHEPCTL_SOURCE_URL: str = (
    "https://github.com/LunaticFringers/shepherd/archive/refs/tags/v"
    "{version}.tar.gz"
)

# URL template for downloading shepctl source tarballs
SHEPCTL_BINARY_URL: str = (
    "https://github.com/LunaticFringers/shepherd/releases/download/"
    "v{version}/shepctl-{version}.tar.gz"
)
