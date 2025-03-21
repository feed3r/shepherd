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

import json
import os
import sys
from typing import Any, Dict

from rich.console import Console

from .constants import Constants


class Util:
    console = Console()

    @staticmethod
    def create_dir(dir_path: str, desc: str):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except OSError as e:
            Util.print_error_and_die(
                f"[{desc}] Failed to create directory: {dir_path}\nError: {e}"
            )

    @staticmethod
    def print_error_and_die(message: str):
        Util.console.print(
            f"[bold red]ERROR:[/bold red] {message}", style="bold red"
        )
        sys.exit(1)

    @staticmethod
    def ensure_dirs(constants: Constants):
        dirs = {
            "SHPD_ENVS_DIR": constants.SHPD_ENVS_DIR,
            "SHPD_ENV_IMGS_DIR": constants.SHPD_ENV_IMGS_DIR,
            "SHPD_CERTS_DIR": constants.SHPD_CERTS_DIR,
            "SHPD_SSH_DIR": constants.SHPD_SSH_DIR,
            "SHPD_SSHD_DIR": constants.SHPD_SSHD_DIR,
        }

        for desc, dir_path in dirs.items():
            resolved_path = os.path.realpath(dir_path)
            if not os.path.exists(resolved_path) or not os.path.isdir(
                resolved_path
            ):
                Util.create_dir(resolved_path, desc)

    @staticmethod
    def ensure_config_file(constants: Constants):
        config_file_path = constants.SHPD_CONFIG_FILE
        if os.path.exists(config_file_path):
            try:
                with open(config_file_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                Util.print_error_and_die(
                    f"Invalid config file: {config_file_path}\nError: {e}"
                )
            return

        default_config: Dict[Any, Any] = {
            "service_types": [
                {
                    "type": "oracle",
                    "image": "${ora_image}",
                    "empty_env": "${ora_empty_env}",
                    "ingress": False,
                    "envvars": {},
                    "ports": {"net_listener_port": "${ora_listener_port}"},
                    "properties": {
                        "pump_dir_name": "${ora_pump_dir}",
                        "root_db_name": "${ora_root_db_name}",
                        "plug_db_name": "${ora_plug_db_name}",
                        "sys_user": "${db_sys_usr}",
                        "sys_psw": "${db_sys_psw}",
                        "user": "${db_usr}",
                        "psw": "${db_psw}",
                    },
                    "subject_alternative_name": None,
                },
                {
                    "type": "postgres",
                    "image": "${pg_image}",
                    "empty_env": "${pg_empty_env}",
                    "ingress": False,
                    "envvars": {},
                    "ports": {"net_listener_port": "${pg_listener_port}"},
                    "properties": {
                        "sys_user": "${db_sys_usr}",
                        "sys_psw": "${db_sys_psw}",
                        "user": "${db_usr}",
                        "psw": "${db_psw}",
                    },
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
        try:
            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
        except OSError as e:
            Util.print_error_and_die(
                f"Failed to create config file: {config_file_path}\nError: {e}"
            )
