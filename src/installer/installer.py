import platform
import os
from dataclasses import dataclass
from installer.constants import *

@dataclass
class Installer:

    def _get_linux_distribution(self):
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.strip().split("=")[1].strip('"')
        except FileNotFoundError:
            return "unknown"
        return "unknown"

    def _check_os_type(self) -> str:
        self.system = platform.system().lower()
        if self.system in ("windows", "win32", "darwin"):
            raise ValueError(f"Unsupported operating system: {self.system}")
        elif self.system == "linux":
            self.distro = self._get_linux_distribution().lower()
            self.distribution = self._get_linux_distribution().lower()

    def _check_dependencies(self) -> bool:
        """Check if Docker and its components are installed on the system."""
        for program in REQUIRED_DOCKER_COMPONENTS:
            result = os.system(f"which {program} > /dev/null 2>&1")
            if result != 0:
                return False
        return True

    def _install_dependencies(self) -> None:
        """Install Docker and its components on the system, supporting multiple distributions."""
        if self.distribution not in INSTALL_COMMANDS:
            raise RuntimeError(f"Unsupported distribution: {self.distribution}")

        install_command = INSTALL_COMMANDS[self.distribution]

        for program in REQUIRED_DOCKER_COMPONENTS:
            result = os.system(f"{install_command} {program}")
            if result != 0:
                raise RuntimeError(f"Failed to install {program}. Please check your system configuration.")

    def _add_gpg_key(self) -> None:
        """Add the proper GPG key for the detected distribution."""
        if self.distribution not in GPG_KEYS:
            raise RuntimeError(f"Unsupported distribution: {self.distribution}")

        gpg_key_url = GPG_KEYS[self.distribution]
        keyring_path = "/usr/share/keyrings/docker-archive-keyring.gpg"

        if os.path.exists(keyring_path):
            return  # Exit early if the keyring already exists

        os.system(f"curl -fsSL {gpg_key_url} | sudo gpg --dearmor -o {keyring_path}")


    def _add_repository(self) -> None:
        """Add the proper repository for the detected distribution."""
        if self.distribution not in REPO_STRINGS:
            raise RuntimeError(f"Unsupported distribution: {self.distribution}")

        repo_string = REPO_STRINGS[self.distribution].format(release=self._get_linux_distribution())
        repo_path = REPO_PATHS[self.distribution]

        if os.path.exists(repo_path):
            return  # Exit early if the repository file already exists

        with open(repo_path, "w") as f:
            f.write(repo_string)

        update_command = UPDATE_COMMANDS[self.distribution]
        os.system(update_command)

    def __init__(self):
        self._check_os_type()

