import subprocess
import platform

# MIT License
#
# Copyright (c) 2025 Lunatic Fringers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class SystemIdentifiers:
    class OS:
        LINUX_DEBIAN = "Debian derived Linux with apt available"
        OTHER_LINUX = "Other Linux"
        WINDOWS = "Windows"
        UNKNOWN_SYSTEM = "Unknown system"

    class Dependencies:
        KEYRING_PATH = "/usr/share/keyrings/docker-archive-keyring.gpg"

        @staticmethod
        def get_architecture():
            """
            Determines the architecture of the current machine and returns a standardized string representation.

            Returns:
                str: A string representing the architecture. Possible values are:
                    - 'amd64' for x86_64 architecture
                    - 'arm64' for aarch64 architecture
                    - 'armhf' for armv7l architecture
                    - The original architecture string for any other architecture
            """
            arch = platform.machine()
            if arch == 'x86_64':
                return 'amd64'
            elif arch == 'aarch64':
                return 'arm64'
            elif arch == 'armv7l':
                return 'armhf'
            else:
                return arch

        @staticmethod
        def get_repo_string():
            """
            Constructs the repository string for Docker based on the system architecture and keyring path.

            Returns:
                str: The repository string for Docker.
            """
            if SystemIdentifiers.get_os() == SystemIdentifiers.OS.LINUX_DEBIAN:
                return (
                    "deb [arch=" + SystemIdentifiers.Dependencies.get_architecture() + " signed-by="
                    + SystemIdentifiers.Dependencies.KEYRING_PATH
                    + "] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
                )
            else:
                return "Unsupported OS for Docker repository"

        DOCKER = "Docker"
        DOCKER_COMPOSE = "Docker Compose"

    @staticmethod
    def get_linux_distribution():
        try:
            with open("/etc/os-release") as f:
                lines = f.readlines()
            distro_info = {}
            for line in lines:
                key, value = line.strip().split("=", 1)
                distro_info[key] = value.strip('"')
            return distro_info.get("ID", "").lower()
        except FileNotFoundError:
            return "unknown"

    @staticmethod
    def get_os():
        system = platform.system()
        if system == "Linux":
            distro_id = SystemIdentifiers.get_linux_distribution()
            if distro_id in ["debian", "ubuntu", "mint", "kali"]:
                return SystemIdentifiers.OS.LINUX_DEBIAN
            else:
                return SystemIdentifiers.OS.OTHER_LINUX
        elif system == "Windows":
            return SystemIdentifiers.OS.WINDOWS
        else:
            return SystemIdentifiers.OS.UNKNOWN_SYSTEM
