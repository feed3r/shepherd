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

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from config import ConfigMng, EnvironmentCfg, ServiceCfg


class Service(ABC):

    type: str
    tag: str
    image: str
    name: str
    hostname: str
    container_name: str
    labels: list[str]
    workdir: str
    volumes: list[str]
    ingress: bool
    empty_env: str
    environment: list[str]
    ports: list[str]
    properties: dict[str, str]
    networks: list[str]
    extra_hosts: list[str]
    subject_alternative_name: Optional[str]

    def __init__(
        self, configMng: ConfigMng, envCfg: EnvironmentCfg, svcCfg: ServiceCfg
    ):
        self.configMng = configMng
        self.envCfg = envCfg
        self.type = svcCfg.type
        self.tag = svcCfg.tag
        self.image = svcCfg.image
        self.name = self.canonical_name()
        self.hostname = (
            svcCfg.hostname if svcCfg.hostname else self.canonical_name()
        )
        self.container_name = (
            svcCfg.container_name
            if svcCfg.container_name
            else self.canonical_name()
        )
        self.labels = svcCfg.labels if svcCfg.labels else []
        self.workdir = svcCfg.workdir if svcCfg.workdir else ""
        self.volumes = svcCfg.volumes if svcCfg.volumes else []
        self.ingress = svcCfg.ingress if svcCfg.ingress else False
        self.empty_env = svcCfg.empty_env if svcCfg.empty_env else ""
        self.environment = svcCfg.environment if svcCfg.environment else []
        self.ports = svcCfg.ports if svcCfg.ports else []
        self.properties = svcCfg.properties if svcCfg.properties else {}
        self.networks = svcCfg.networks if svcCfg.networks else []
        self.extra_hosts = svcCfg.extra_hosts if svcCfg.extra_hosts else []
        self.subject_alternative_name = svcCfg.subject_alternative_name

    def canonical_name(self) -> str:
        """
        Get the canonical name of the service.
        """
        return f"{self.tag}-{self.envCfg.tag}"

    @abstractmethod
    def clone(self, dst_svc_tag: str) -> Service:
        """Clone a service."""
        pass

    @abstractmethod
    def render(self) -> str:
        """
        Render the service configuration.
        """
        pass

    @abstractmethod
    def build(self):
        """Build the service."""
        pass

    @abstractmethod
    def bootstrap(self):
        """Bootstrap the service."""
        pass

    @abstractmethod
    def start(self):
        """Start the service."""
        pass

    @abstractmethod
    def halt(self):
        """Stop the service."""
        pass

    @abstractmethod
    def reload(self):
        """Reload the service."""
        pass

    @abstractmethod
    def show_stdout(self):
        """Show the service stdout."""
        pass

    @abstractmethod
    def get_shell(self):
        """Get a shell session for the service."""
        pass

    def to_config(self) -> ServiceCfg:
        return ServiceCfg(
            type=self.type,
            tag=self.tag,
            image=self.image,
            hostname=self.hostname,
            container_name=self.container_name,
            labels=self.labels,
            workdir=self.workdir,
            volumes=self.volumes,
            ingress=self.ingress,
            empty_env=self.empty_env,
            environment=self.environment,
            ports=self.ports,
            properties=self.properties,
            networks=self.networks,
            extra_hosts=self.extra_hosts,
            subject_alternative_name=self.subject_alternative_name,
        )


class ServiceFactory(ABC):
    """
    Factory class for services.
    """

    def __init__(self, config: ConfigMng):
        self.config = config

    @abstractmethod
    def new_service_from_cfg(
        self, envCfg: EnvironmentCfg, svcCfg: ServiceCfg
    ) -> Service:
        """
        Create a new service.
        """
        pass


class ServiceMng:

    def __init__(self, cli_flags: dict[str, bool], configMng: ConfigMng):
        self.cli_flags = cli_flags
        self.configMng = configMng
        pass

    def build_image_svc(self, service_type: str):
        pass

    def bootstrap_svc(self, service_type: str):
        """Bootstrap a service."""
        pass

    def start_svc(self, service_type: str):
        """Start a service."""
        pass

    def halt_svc(self, service_type: str):
        """Halt a service."""
        pass

    def reload_svc(self, service_type: str):
        """Reload a service."""
        pass

    def stdout_svc(self, service_id: str):
        """Get service stdout."""
        pass

    def shell_svc(self, service_id: str):
        """Get a shell session for a service."""
        pass
