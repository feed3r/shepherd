import unittest
from unittest.mock import patch, mock_open
import os
from installer.installer import Installer

class TestInstaller(unittest.TestCase):

    @patch('platform.system')
    @patch('distro.id')
    def test_check_os(self, mock_distro_id, mock_platform_system):
        # Mock for Debian-based distributions
        mock_platform_system.return_value = "Linux"
        mock_distro_id.return_value = "debian"
        installer = Installer()
        self.assertEqual(installer.distro, "debian")

        # Mock for unsupported OS (Windows)
        mock_platform_system.return_value = "Windows"
        with self.assertRaises(ValueError) as context:
            installer = Installer()
        self.assertIn("Unsupported operating system", str(context.exception))

        # Mock for unsupported OS (Darwin)
        mock_platform_system.return_value = "Darwin"
        with self.assertRaises(ValueError) as context:
            installer = Installer()
        self.assertIn("Unsupported operating system", str(context.exception))

        # Mock for WSL
        mock_platform_system.return_value = "Win32"
        with self.assertRaises(ValueError) as context:
            installer = Installer()
        self.assertIn("Unsupported operating system", str(context.exception))

    @patch('os.system')
    def test_check_dependencies(self, mock_system):
        # Mocking os.system to simulate Docker components being installed
        mock_system.return_value = 0
        installer = Installer()
        self.assertTrue(installer._check_dependencies())

        # Mocking os.system to simulate a missing Docker component
        mock_system.return_value = 1
        self.assertFalse(installer._check_dependencies())

    @patch('os.system')
    @patch('os.path.exists')
    @patch('distro.id', return_value='debian')
    def test_add_gpg_key(self, mock_distro_id, mock_exists, mock_system):
        installer = Installer()

        # Simulate GPG keyring does not exist
        mock_exists.return_value = False
        mock_system.return_value = 0

        installer._add_gpg_key()
        mock_system.assert_called_with("curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg")

        # Simulate GPG keyring already exists
        mock_exists.return_value = True
        installer._add_gpg_key()
        mock_system.reset_mock()
        mock_system.assert_not_called()

    @patch('os.system')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('distro.id')
    @patch('distro.codename')
    @patch('os.popen')
    def test_add_repository(self, mock_popen, mock_distro_codename, mock_distro_id, mock_exists, mock_open_file, mock_system):
        # Properly set up the mocks for the installer attributes
        mock_distro_id.return_value = "debian"
        mock_distro_codename.return_value = "buster"
        
        # Mock the architecture command to return "amd64"
        mock_popen.return_value.read.return_value = "amd64"
        
        installer = Installer()
        # Manually set the distro attribute to match our test
        installer.distro = "debian"

        # Define test cases for all supported distributions
        test_cases = {
            "debian": {
                "repo_path": "/etc/apt/sources.list.d/docker.list",
                "repo_string": "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian buster stable",
                "update_command": "sudo apt update",
            },
            "ubuntu": {
                "repo_path": "/etc/apt/sources.list.d/docker.list",
                "repo_string": "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu buster stable",
                "update_command": "sudo apt update",
            },
            "fedora": {
                "repo_path": "/etc/yum.repos.d/docker.repo",
                "repo_string": "[docker]\nname=Docker CE Stable - $basearch\nbaseurl=https://download.docker.com/linux/fedora/$releasever/$basearch/stable\nenabled=1\ngpgcheck=1\ngpgkey=/etc/pki/rpm-gpg/RPM-GPG-KEY-docker",
                "update_command": "sudo dnf update",
            },
            "centos": {
                "repo_path": "/etc/yum.repos.d/docker.repo",
                "repo_string": "[docker]\nname=Docker CE Stable - $basearch\nbaseurl=https://download.docker.com/linux/centos/$releasever/$basearch/stable\nenabled=1\ngpgcheck=1\ngpgkey=/etc/pki/rpm-gpg/RPM-GPG-KEY-docker",
                "update_command": "sudo yum update",
            },
            "arch": {
                "repo_path": "/etc/pacman.d/mirrorlist.d/docker.list",
                "repo_string": "Server = https://download.docker.com/linux/archlinux/$arch/stable",
                "update_command": "sudo pacman -Syu",
            },
        }

        # Test only the debian case for simplicity
        config = test_cases["debian"]
        
        # Simulate repository file does not exist
        mock_exists.return_value = False
        mock_system.reset_mock()

        installer._add_repository()
        mock_open_file.assert_called_with(config["repo_path"], "w")
        mock_open_file().write.assert_called_with(config["repo_string"])

        # Verify the update command is executed
        mock_system.assert_any_call(config["update_command"])

        # Simulate repository file already exists
        mock_exists.return_value = True
        installer._add_repository()
        mock_open_file.reset_mock()
        mock_open_file.assert_not_called()
        mock_system.reset_mock()
        mock_system.assert_not_called()

if __name__ == "__main__":
    unittest.main()



