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


from typing import override

from completion.completion_svc import CompletionSvcMng
from config import ConfigMng


class CompletionDbMng(CompletionSvcMng):

    COMMANDS_DB = CompletionSvcMng.COMMANDS_SVC + ["sql-shell"]

    def __init__(self, cli_flags: dict[str, bool], configMng: ConfigMng):
        self.cli_flags = cli_flags
        self.configMng = configMng

    def is_command_chosen(self, args: list[str]) -> bool:
        """
        Checks if the second argument is a valid command
        for the chosen category.
        """
        if not args or len(args) < 1:
            return False
        command = args[0]
        return command in self.COMMANDS_DB

    @override
    def get_completions(self, args: list[str]) -> list[str]:
        if not self.is_command_chosen(args):
            return self.COMMANDS_DB

        command = args[0]
        match command:
            case "sql-shell":
                return self.get_sql_shell_completions(args[1:])
            case _:
                return []

    def get_sql_shell_completions(self, args: list[str]) -> list[str]:
        return []
