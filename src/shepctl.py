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


import functools
import logging
from typing import Any, Callable, Optional

import click

from completion import CompletionMng
from config import ConfigMng, EnvironmentCfg
from database import DatabaseMng
from environment import EnvironmentMng
from factory import ShpdEnvironmentFactory, ShpdServiceFactory
from service import ServiceMng
from util import Util, setup_logging


class ShepherdMng:
    def __init__(self, cli_flags: dict[str, bool] = {}):
        self.configMng = ConfigMng("~/.shpd.conf")
        self.cli_flags = cli_flags
        Util.ensure_dirs(self.configMng.constants)
        Util.ensure_config_file(self.configMng.constants)
        self.configMng.load()
        setup_logging(
            self.configMng.config.logging.file,
            self.configMng.config.logging.format,
            self.configMng.config.logging.level,
            self.configMng.config.logging.stdout,
        )
        logging.debug(
            "### shepctl version:%s started",
            self.configMng.constants.APP_VERSION,
        )
        self.completionMng = CompletionMng(self.cli_flags, self.configMng)
        self.svcFactory = ShpdServiceFactory(self.configMng)
        self.envFactory = ShpdEnvironmentFactory(
            self.configMng, self.svcFactory
        )
        self.environmentMng = EnvironmentMng(
            self.cli_flags, self.configMng, self.envFactory, self.svcFactory
        )
        self.serviceMng = ServiceMng(
            self.cli_flags, self.configMng, self.svcFactory
        )
        self.databaseMng = DatabaseMng(self.cli_flags, self.configMng)


def require_active_env(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(
        shepherd: ShepherdMng, *args: list[str], **kwargs: dict[str, str]
    ) -> Callable[..., Any]:
        envCfg = shepherd.configMng.get_active_environment()
        if not envCfg:
            raise click.UsageError("No active environment found.")
        return func(shepherd, envCfg, *args, **kwargs)

    return wrapper


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode.")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Automatic yes to prompts; run non-interactively.",
)
@click.option("-a", "--all", is_flag=True, help="Apply to all.")
@click.option("-f", "--follow", is_flag=True, help="Follow log output.")
@click.option(
    "-p", "--porcelain", is_flag=True, help="Produce machine-readable output."
)
@click.option("-k", "--keep", is_flag=True, help="Keep instead of drop.")
@click.option(
    "-r", "--replace", is_flag=True, help="Replace when already there."
)
@click.option(
    "-c",
    "--checkout",
    is_flag=True,
    help="Contextually checkout the environment.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    yes: bool,
    all: bool,
    follow: bool,
    porcelain: bool,
    keep: bool,
    replace: bool,
    checkout: bool,
):
    """Shepherd CLI:
    A tool to manage your environments, services, and databases.
    """
    cli_flags = {
        "verbose": verbose,
        "yes": yes,
        "all": all,
        "follow": follow,
        "porcelain": porcelain,
        "keep": keep,
        "replace": replace,
        "checkout": checkout,
    }

    if ctx.obj is None:
        ctx.obj = ShepherdMng(cli_flags)


@cli.command(name="test", hidden=True)
def empty():
    """Empty testing purpose stub"""
    pass


@cli.command(name="__complete", hidden=True)
@click.argument("args", nargs=-1)
@click.pass_obj
def complete(shepherd: ShepherdMng, args: list[str]):
    """
    Internal shell completion entrypoint.
    Usage: shepctl __complete <args...>
    """
    completions = shepherd.completionMng.get_completions(args)
    for c in completions:
        click.echo(c)


@cli.group()
def db():
    """Database related operations."""
    pass


@db.command(name="build")
@click.pass_obj
def db_build(shepherd: ShepherdMng):
    """Build database image."""
    shepherd.databaseMng.build_image_svc("")


@db.command(name="bootstrap")
@click.pass_obj
def db_bootstrap(shepherd: ShepherdMng):
    """Bootstrap database service."""
    shepherd.databaseMng.bootstrap_svc("")


@db.command(name="up")
@click.pass_obj
@require_active_env
def db_up(shepherd: ShepherdMng, envCfg: EnvironmentCfg):
    """Start database service."""
    shepherd.databaseMng.start_svc(envCfg.tag, "database")


@db.command(name="halt")
@click.pass_obj
@require_active_env
def db_halt(shepherd: ShepherdMng, envCfg: EnvironmentCfg):
    """Halt database service."""
    shepherd.databaseMng.halt_svc(envCfg.tag, "database")


@db.command(name="stdout")
@click.pass_obj
@require_active_env
def db_stdout(shepherd: ShepherdMng, envCfg: EnvironmentCfg):
    """Show database service stdout."""
    shepherd.databaseMng.stdout_svc(envCfg.tag, "db-id")


@db.command(name="shell")
@click.pass_obj
@require_active_env
def db_shell(shepherd: ShepherdMng, envCfg: EnvironmentCfg):
    """Get a shell session for the database service."""
    shepherd.databaseMng.shell_svc(envCfg.tag, "db-id")


@db.command(name="sql-shell")
@click.pass_obj
@require_active_env
def db_sql_shell(shepherd: ShepherdMng, envCfg: EnvironmentCfg):
    """Get a SQL session for the database service."""
    shepherd.databaseMng.sql_shell_svc(envCfg.tag, "db-id")


# Environment commands
@cli.group()
def env():
    """Environment related operations."""
    pass


@env.command(name="init")
@click.argument("env_type", required=True)
@click.argument("env_tag", required=True)
@click.pass_obj
def env_init(shepherd: ShepherdMng, env_type: str, env_tag: str):
    """Init an environment of type ENV_TYPE with tag ENV_TAG."""
    shepherd.environmentMng.init_env(env_type, env_tag)


@env.command(name="clone")
@click.argument("src_env_tag", required=True)
@click.argument("dst_env_tag", required=True)
@click.pass_obj
def env_clone(shepherd: ShepherdMng, src_env_tag: str, dst_env_tag: str):
    """Clone an environment."""
    shepherd.environmentMng.clone_env(src_env_tag, dst_env_tag)


@env.command(name="rename")
@click.argument("src_env_tag", required=True)
@click.argument("dst_env_tag", required=True)
@click.pass_obj
def env_rename(shepherd: ShepherdMng, src_env_tag: str, dst_env_tag: str):
    """Rename an environment."""
    shepherd.environmentMng.rename_env(src_env_tag, dst_env_tag)


@env.command(name="checkout")
@click.argument("env_tag", required=True)
@click.pass_obj
def env_checkout(shepherd: ShepherdMng, env_tag: str):
    """Checkout an environment."""
    shepherd.environmentMng.checkout_env(env_tag)


@env.command(name="delete")
@click.argument("env_tag", required=True)
@click.pass_obj
def env_delete(shepherd: ShepherdMng, env_tag: str):
    """Delete an environment."""
    shepherd.environmentMng.delete_env(env_tag)


@env.command(name="list")
@click.pass_obj
def env_list(shepherd: ShepherdMng):
    """List all available environments."""
    shepherd.environmentMng.list_envs()


@env.command(name="up")
@click.pass_obj
def env_up(shepherd: ShepherdMng):
    """Start environment."""
    shepherd.environmentMng.start_env()


@env.command(name="halt")
@click.pass_obj
def env_halt(shepherd: ShepherdMng):
    """Halt environment."""
    shepherd.environmentMng.halt_env()


@env.command(name="reload")
@click.pass_obj
def env_reload(shepherd: ShepherdMng):
    """Reload environment."""
    shepherd.environmentMng.reload_env()


@env.command(name="status")
@click.pass_obj
def env_status(shepherd: ShepherdMng):
    """Print environment's status."""
    shepherd.environmentMng.status_env()


@env.command(name="add-resource")
@click.argument("resource_type", required=True)
@click.argument("resource_name", required=True)
@click.argument("resource_class", required=False)
@click.argument("resource_template", required=False)
@click.pass_obj
@require_active_env
def env_add_resource(
    shepherd: ShepherdMng,
    envCfg: EnvironmentCfg,
    resource_type: str,
    resource_name: str,
    resource_class: Optional[str] = None,
    resource_template: Optional[str] = None,
):
    """Add a resource to the current environment.

    RESOURCE_TYPE: The type of resource to add (e.g., svc).
    RESOURCE_NAME: The name of the resource (e.g., svc-name).
    RESOURCE_CLASS: Optional class of the resource (e.g., svc-class).
    RESOURCE_TEMPLATE: Optional template for the resource.
    """
    if resource_type == shepherd.configMng.constants.RESOURCE_TYPE_SVC:
        shepherd.environmentMng.add_service(
            envCfg.tag, resource_name, resource_class, resource_template
        )
    else:
        raise click.UsageError(f"Unsupported resource type: {resource_type}")


@cli.group()
def svc():
    """Service related operations."""
    pass


@svc.command(name="build")
@click.argument("service_template", type=str, required=True)
@click.pass_obj
def srv_build(shepherd: ShepherdMng, service_template: str):
    """Build service image."""
    shepherd.serviceMng.build_image_svc(service_template)


@svc.command(name="bootstrap")
@click.argument("service_template", type=str, required=True)
@click.pass_obj
def srv_bootstrap(shepherd: ShepherdMng, service_template: str):
    """Bootstrap service."""
    shepherd.serviceMng.bootstrap_svc(service_template)


@svc.command(name="up")
@click.argument("service_template", type=str, required=True)
@click.pass_obj
@require_active_env
def srv_up(
    shepherd: ShepherdMng, envCfg: EnvironmentCfg, service_template: str
):
    """Start service."""
    shepherd.serviceMng.start_svc(envCfg.tag, service_template)


@svc.command(name="halt")
@click.argument("service_template", type=str, required=True)
@click.pass_obj
@require_active_env
def srv_halt(
    shepherd: ShepherdMng, envCfg: EnvironmentCfg, service_template: str
):
    """Halt service."""
    shepherd.serviceMng.halt_svc(envCfg.tag, service_template)


@svc.command(name="reload")
@click.argument("service_template", type=str, required=True)
@click.pass_obj
@require_active_env
def srv_reload(
    shepherd: ShepherdMng, envCfg: EnvironmentCfg, service_template: str
):
    """Reload service."""
    shepherd.serviceMng.reload_svc(envCfg.tag, service_template)


@svc.command(name="render")
@click.argument("service_tag", type=str, required=True)
@click.pass_obj
@require_active_env
def srv_render(shepherd: ShepherdMng, envCfg: EnvironmentCfg, service_tag: str):
    """Render service configuration."""
    click.echo(shepherd.serviceMng.render_svc(envCfg.tag, service_tag))


@svc.command(name="stdout")
@click.argument("service_tag", type=str, required=True)
@click.pass_obj
@require_active_env
def srv_stdout(shepherd: ShepherdMng, envCfg: EnvironmentCfg, service_tag: str):
    """Show service stdout."""
    shepherd.serviceMng.stdout_svc(envCfg.tag, service_tag)


@svc.command(name="shell")
@click.argument("service_tag", type=str, required=True)
@click.pass_obj
@require_active_env
def srv_shell(shepherd: ShepherdMng, envCfg: EnvironmentCfg, service_tag: str):
    """Get a shell session for the service."""
    shepherd.serviceMng.shell_svc(envCfg.tag, service_tag)


if __name__ == "__main__":
    cli(obj=None)
