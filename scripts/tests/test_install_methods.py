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
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import tarfile
import io
import shutil

# Add the scripts directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The functions we'll be testing - these will be implemented in install.py
from install import install_binary, install_source

class TestInstallMethods:
    """Test suite for the installation methods."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.install_dir = Path(self.temp_dir) / "shepctl"
        self.install_dir.mkdir(exist_ok=True)
        
        # Set environment variables for testing
        self.env_patcher = patch.dict(os.environ, {
            "INSTALL_SHEPCTL_DIR": str(self.install_dir),
            "SYMLINK_DIR": str(Path(self.temp_dir) / "bin"),
            "VER": "1.0.0"
        })
        self.env_patcher.start()
        
        # Create symlink directory
        symlink_dir = Path(os.environ["SYMLINK_DIR"])
        symlink_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Clean up after each test."""
        self.env_patcher.stop()
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    @patch('install.run_command')
    @patch('install.print_color')
    def test_install_binary(self, mock_print, mock_run_command):
        """Test binary installation method."""
        # Mock successful command execution
        mock_run_command.return_value = MagicMock(returncode=0)
        
        # Create a temporary URL for testing
        url = f"https://github.com/LunaticFringers/shepherd/releases/download/v1.0.0/shepctl-1.0.0.tar.gz"
        
        with patch('install.url', url), \
             patch('os.chmod') as mock_chmod, \
             patch('os.symlink') as mock_symlink:
            
            install_binary()
            
            # Check curl command was executed with the correct URL
            mock_run_command.assert_any_call(
                ['curl', '-fsSL', url, '-o', f"{self.install_dir}/shepctl-1.0.0.tar.gz"],
                check=True
            )
            
            # Check tar command was executed
            mock_run_command.assert_any_call(
                ['tar', '-xzf', f"{self.install_dir}/shepctl-1.0.0.tar.gz", '-C', str(self.install_dir)],
                check=True
            )
            
            # Check executable permissions were set
            mock_chmod.assert_called_with(f"{self.install_dir}/shepctl", 0o755)
            
            # Check symlink was created
            mock_symlink.assert_called_with(
                f"{self.install_dir}/shepctl",
                f"{os.environ['SYMLINK_DIR']}/shepctl"
            )
    
    @patch('install.run_command')
    @patch('install.print_color')
    def test_install_source(self, mock_print, mock_run_command):
        """Test source installation method."""
        # Mock successful command execution
        mock_run_command.return_value = MagicMock(returncode=0)
        
        # Set up source repository URL
        repo_url = "https://github.com/LunaticFringers/shepherd.git"
        
        with patch('install.py_src_dir', Path(self.temp_dir) / "src"), \
             patch('os.chmod') as mock_chmod, \
             patch('os.symlink') as mock_symlink, \
             patch('os.chdir') as mock_chdir, \
             patch('shutil.which', return_value="/usr/bin/python3"):
            
            # Create mock src directory
            src_dir = Path(self.temp_dir) / "src"
            src_dir.mkdir(exist_ok=True)
            
            install_source()
            
            # Check git clone command was executed
            mock_run_command.assert_any_call(
                ['git', 'clone', repo_url, str(self.install_dir)],
                check=True
            )
            
            # Check pip install was executed
            mock_run_command.assert_any_call(
                [sys.executable, '-m', 'pip', 'install', '-e', f"{self.install_dir}"],
                check=True
            )
            
            # Check symlink was created
            mock_symlink.assert_called_with(
                f"{self.install_dir}/bin/shepctl",
                f"{os.environ['SYMLINK_DIR']}/shepctl"
            )

if __name__ == '__main__':
    pytest.main(['-xvs', __file__])
