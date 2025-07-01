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
from typing import Any, Dict


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

    # Default configuration values

    @property
    def DEFAULT_CONFIG(self) -> Dict[Any, Any]:
        return {
            "logging": {
                "file": "${log_file}",
                "level": "${log_level}",
                "stdout": "${log_stdout}",
                "format": "${log_format}",
            },
            "service_types": [
                {
                    "type": "docker",
                    "image": "",
                    "ingress": False,
                    "envvars": {},
                    "ports": {},
                    "properties": {},
                    "subject_alternative_name": None,
                },
            ],
            "shpd_registry": {
                "ftp_server": "${shpd_registry}",
                "ftp_user": "${shpd_registry_ftp_usr}",
                "ftp_psw": "${shpd_registry_ftp_psw}",
                "ftp_shpd_path": "${shpd_registry_ftp_shpd_path}",
                "ftp_env_imgs_path": "${shpd_registry_ftp_imgs_path}",
            },
            "host_inet_ip": "${host_inet_ip}",
            "domain": "${domain}",
            "dns_type": "${dns_type}",
            "ca": {
                "country": "${ca_country}",
                "state": "${ca_state}",
                "locality": "${ca_locality}",
                "organization": "${ca_org}",
                "organizational_unit": "${ca_org_unit}",
                "common_name": "${ca_cn}",
                "email": "${ca_email}",
                "passphrase": "${ca_passphrase}",
            },
            "cert": {
                "country": "${cert_country}",
                "state": "${cert_state}",
                "locality": "${cert_locality}",
                "organization": "${cert_org}",
                "organizational_unit": "${cert_org_unit}",
                "common_name": "${cert_cn}",
                "email": "${cert_email}",
                "subject_alternative_names": [],
            },
            "envs": [],
        }
