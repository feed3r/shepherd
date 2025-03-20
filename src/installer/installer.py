import platform
from dataclasses import dataclass

@dataclass
class Installer:
    os_type: str = ""

    def __post_init__(self):
        self.os_type = self.detect_os_type()

    def detect_os_type(self) -> str:
        system = platform.system()
        if system == "Windows":
            return "WINDOWS"
        elif system == "Linux":
            distro = platform.linux_distribution()[0].lower()
            if "debian" in distro or "ubuntu" in distro:
                return "LINUX DEBIAN DERIVED"
            else:
                return "OTHER LINUX"
        else:
            return "UNKNOWN"

    def install_dependencies(self) -> None:
        if self.os_type == "LINUX DEBIAN DERIVED":
            self.install_debian_dependencies()
        else:
            raise NotImplementedError(f"Installation for {self.os_type} is not supported yet.")

    def install_debian_dependencies(self) -> None:
        # Placeholder for actual installation logic using apt
        print("Installing dependencies using apt...")

