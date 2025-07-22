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
import shutil
import tempfile
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, call, patch

import pytest

# Import the module under test
from installer import install
from installer.repository_manager import RepositoryManager
from util import Util


class TestInstallScript:
    """Test suite for the main installation script."""

    def setup_method(self) -> None:
        """Set up test environment before each test."""
        # Reset global variables before each test
        install.verbose = False
        install.skip_ensure_deps = False
        install.install_method = "binary"

        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.install_dir = Path(self.temp_dir) / "shepctl"
        self.install_dir.mkdir(exist_ok=True)

        # Mock environment variables
        self.env_patcher = patch.dict(
            os.environ,
            {
                "INSTALL_SHEPCTL_DIR": str(self.install_dir),
                "SYMLINK_DIR": str(Path(self.temp_dir) / "bin"),
                "VER": "1.0.0",
            },
        )
        self.env_patcher.start()

        # Update paths after environment variable changes
        install.install_shepctl_dir = Path(
            os.environ["INSTALL_SHEPCTL_DIR"]
        ).resolve()
        install.symlink_dir = Path(os.environ["SYMLINK_DIR"])

    def teardown_method(self) -> None:
        """Clean up after each test."""
        self.env_patcher.stop()
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_cli_help(self) -> None:
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(install.cli, ["--help"])
        assert result.exit_code == 0
        assert "Shepherd Control Tool Installer" in result.output

    def test_cli_install_command(self) -> None:
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(install.cli, ["install", "--help"])
        assert result.exit_code == 0
        assert "Install shepctl" in result.output

    def test_cli_uninstall_command(self) -> None:
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(install.cli, ["uninstall", "--help"])
        assert result.exit_code == 0
        assert "Uninstall shepctl" in result.output

    @patch("util.Util.is_root")
    def test_cli_install_not_root(self, mock_is_root: MagicMock) -> None:
        from click.testing import CliRunner

        mock_is_root.return_value = False  # Simulate not running as root

        runner = CliRunner()
        result = runner.invoke(install.cli, ["install"])

        # Should exit with code 1
        assert result.exit_code == 1

    @patch("shutil.rmtree")
    @patch("os.makedirs")
    @patch("util.Util.is_root")
    @patch("installer.install.install_shepctl")
    def test_cli_install_as_root(
        self,
        mock_install_shepctl: MagicMock,
        mock_is_root: MagicMock,
        mock_makedirs: MagicMock,
        mock_rmtree: MagicMock,
    ) -> None:
        from click.testing import CliRunner

        mock_is_root.return_value = True

        runner = CliRunner()
        result = runner.invoke(
            install.cli, ["-m", "source", "-v", "--skip-deps", "install"]
        )

        # Should succeed
        assert result.exit_code == 0

        # Check install_shepctl was called
        mock_install_shepctl.assert_called_once()

    @patch("shutil.rmtree")
    @patch("os.makedirs")
    @patch("util.Util.is_root")
    @patch("installer.install.uninstall_shepctl")
    def test_cli_uninstall_as_root(
        self,
        mock_uninstall_shepctl: MagicMock,
        mock_is_root: MagicMock,
        mock_makedirs: MagicMock,
        mock_rmtree: MagicMock,
    ) -> None:
        """Test uninstall command when running as root."""
        from click.testing import CliRunner

        mock_is_root.return_value = True

        runner = CliRunner()
        result = runner.invoke(install.cli, ["uninstall"])

        # Should succeed
        assert result.exit_code == 0

        # Check uninstall_shepctl was called
        mock_uninstall_shepctl.assert_called_once()

    @patch("installer.install.RepositoryManager.install_packages")
    @patch("util.Util.get_os_info")
    @patch("os.makedirs")
    @patch("shutil.rmtree")
    @patch("installer.install.install_binary")
    @patch("util.Util.run_command")  # Patch the static method directly
    def test_install_with_dependencies(
        self,
        mock_run_command: MagicMock,
        mock_install_binary: MagicMock,
        mock_rmtree: MagicMock,
        mock_makedirs: MagicMock,
        mock_get_os_info: MagicMock,
        mock_install_packages: MagicMock,
    ) -> None:
        """Test install function with dependency installation."""
        # Mock skip_ensure_deps
        install.skip_ensure_deps = False
        install.install_method = "binary"

        # Mock OS info
        mock_os_info = Util.OsInfo(
            system="linux",
            distro="ubuntu",
            codename="focal",
        )
        mock_get_os_info.return_value = mock_os_info

        # Mock install_shepctl_dir exists
        with patch("pathlib.Path.exists", return_value=True):
            install.install_shepctl()

        # Check dependencies were installed
        mock_get_os_info.assert_called_once()
        mock_install_packages.assert_called_once_with(
            mock_os_info.distro, mock_os_info.codename, False
        )

        # Check directory was recreated
        mock_rmtree.assert_called_once_with(install.install_shepctl_dir)
        mock_makedirs.assert_called_once_with(
            install.install_shepctl_dir, exist_ok=True
        )

        # Verify the binary installation was called
        mock_install_binary.assert_called_once()

    @patch("util.Util.get_os_info")
    @patch("installer.install.RepositoryManager.install_packages")
    @patch("os.makedirs")
    @patch("shutil.rmtree")
    @patch("installer.install.install_binary")
    def test_install_skip_dependencies(
        self,
        mock_install_binary: MagicMock,
        mock_rmtree: MagicMock,
        mock_makedirs: MagicMock,
        mock_get_os_info: MagicMock,
        mock_install_packages: MagicMock,
    ) -> None:
        """Test install function while skipping dependencies."""
        # Mock skip_ensure_deps
        install.skip_ensure_deps = True
        install.install_method = "binary"

        # Mock install_shepctl_dir exists
        with patch("pathlib.Path.exists", return_value=True):
            install.install_shepctl()

        # Check dependencies were not installed
        mock_get_os_info.assert_not_called()
        mock_install_packages.assert_not_called()

        # Check directory was recreated
        mock_rmtree.assert_called_once_with(install.install_shepctl_dir)
        mock_makedirs.assert_called_once_with(
            install.install_shepctl_dir, exist_ok=True
        )

        # Verify the binary installation was called
        mock_install_binary.assert_called_once()

    @patch("os.makedirs")
    @patch("shutil.rmtree")
    def test_install_unknown_method(
        self,
        mock_rmtree: MagicMock,
        mock_makedirs: MagicMock,
    ) -> None:
        """Test install function with unknown install method."""
        # Set unknown install method
        install.install_method = "unknown"
        install.skip_ensure_deps = True

        # Mock install_shepctl_dir exists
        with patch("pathlib.Path.exists", return_value=True):
            with pytest.raises(SystemExit):
                install.install_shepctl()

    @patch("shutil.rmtree")
    def test_uninstall(self, mock_rmtree: MagicMock) -> None:
        """Test uninstall function."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            install.uninstall_shepctl()

            # Check installation directory was removed
            mock_rmtree.assert_called_once_with(install.install_shepctl_dir)

            # Check symlink was removed
            mock_unlink.assert_called_once()

    @patch("util.Util.check_file_exists", return_value=False)
    @patch("util.Util.run_command")
    @patch(
        "installer.repository_manager.RepositoryManager."
        "check_package_installed"
    )
    @patch(
        "installer.repository_manager.RepositoryManager.add_docker_repository"
    )
    @patch(
        "installer.repository_manager.RepositoryManager."
        "install_missing_packages"
    )
    def test_install_docker_packages(
        self,
        mock_install_missing_packages: MagicMock,
        mock_add_docker_repository: MagicMock,
        mock_check_package_installed: MagicMock,
        mock_run_command: MagicMock,
        mock_check_file_exists: MagicMock,
    ) -> None:
        """Test the installation of Docker packages."""
        current_user = os.getenv("USER")

        # Simulate Docker not being installed
        mock_check_package_installed.return_value = False

        # Simulate successful command execution
        mock_run_command.return_value = MagicMock(
            stdout="Docker version 20.10.7"
        )

        # Call the function under test
        RepositoryManager.install_docker_packages("debian", "buster")

        # Verify that add_docker_repository was called with correct arguments
        mock_add_docker_repository.assert_called_once_with("debian", "buster")

        # Verify that install_missing_packages was called for Docker packages
        mock_install_missing_packages.assert_called()

        # Verify that the required commands were called
        expected_calls = [
            call(["docker", "--version"], check=False, capture_output=True),
            call(
                ["docker-compose", "--version"],
                check=False,
                capture_output=True,
            ),
            call(["sudo", "systemctl", "enable", "docker"], check=True),
            call(["sudo", "groupadd", "-f", "docker"], check=True),
            call(["usermod", "-aG", "docker", current_user], check=True),
        ]
        mock_run_command.assert_has_calls(expected_calls, any_order=True)

        # Verify that the package installation function was called
        mock_check_package_installed.assert_called_with("docker-compose-plugin")

    @patch("util.Util.run_command")
    def test_install_binary(self, mock_run_command: MagicMock) -> None:
        """Test binary installation method."""
        # Mock successful command execution
        mock_run_command.return_value = MagicMock(returncode=0)

        with patch.dict(os.environ, {"VER": "1.0.0"}):
            with (
                patch("os.chmod") as mock_chmod,
                patch("os.symlink") as mock_symlink,
            ):
                install.install_binary()

                expected_url = (
                    "https://github.com/LunaticFringers/shepherd/"
                    "releases/download/v1.0.0/shepctl-1.0.0.tar.gz"
                )

                # Verify the sequence of commands
                expected_calls = [
                    # First, the curl command
                    mock.call(
                        [
                            "curl",
                            "-fsSL",
                            expected_url,
                            "-o",
                            f"{self.install_dir}/shepctl-1.0.0.tar.gz",
                        ],
                        check=True,
                    ),
                    # Then, the tar command
                    mock.call(
                        [
                            "tar",
                            "-xzf",
                            f"{self.install_dir}/shepctl-1.0.0.tar.gz",
                            "-C",
                            str(self.install_dir),
                        ],
                        check=True,
                    ),
                ]
                mock_run_command.assert_has_calls(
                    expected_calls, any_order=False
                )  # Enforce the order of calls

                mock_chmod.assert_called_with(
                    f"{self.install_dir}/shepctl", 0o755
                )

                mock_symlink.assert_called_with(
                    f"{self.install_dir}/shepctl",
                    Path(f"{os.environ['SYMLINK_DIR']}/shepctl"),
                )


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
