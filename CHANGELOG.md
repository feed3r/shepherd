# Changelog
All notable changes to this project will be documented in this file.
	## [unreleased]


### <!-- 0 -->Features

- 

Add default commit template


### <!-- 1 -->Bug Fixes

- *(config)* 

Replace 'key' with 'tag' in config model


### <!-- 2 -->Refactor

- *(config)* 

Introduce Resolvable for dynamic placeholder resolution


### <!-- 3 -->Documentation

- 

Remove duplicated sentence

- 

Add documentation change to PR template

- 

Improve contribution guidelines

- 

Add ADR to propose a changelog generator


### <!-- 7 -->Miscellaneous Tasks

- *(pre-commit)* 

Update pre-commit hooks and fix pyright issues

- *(changelog)* 

Create draft git-cliff configuration


### <!-- 9 -->Other

- 

Add Linux install script




- 

Define Environment/Service/Database Interfaces

- Define Environment/Service/Database Interfaces
- Remove src/conf
- Rename Config classes
- Merge Database config into Service config
- Adjust tests






- 

Add Config memory to file related functionalities

- Provide Memory-Config to JSON serialization.
- Save Memory-Config to config file.




- 

Make config's model service-type agnostic

- Add ServiceTypeCfg config model class.
- Drop Oracle and Postgres config classes.




- 

Make generic service's upstream concept

- Drop DBUpstreamCfg
- Add UpstreamCfg
- Add Documentation for Config classes




- 

Add ShepherdMng main class

- Add ShepherdMng class holding global program's status
- Adjust Environment/Service/DatabaseService classes
- Adjust Managers code, comments and documentation



- 

Initialize program's status on start

- Ensure required resources (directories, files etc)
- Load program's status by reading the configuration




- 

Add codecov.yml

Add Codecov configuration file.




- 

Add ADR for changing Shepherd Core Stack Licence




- 

Change Shepherd Core Stack Licence from MIT to AGPL




- 

Bind Database/Environment/Service managers to CLI commands

- Bind Database/Environment/Service managers to CLI commands.
- Test command bindings
- Test CLI Flags




- 

Implement Docker-Compose environment




- 

Rename shpdctl to shepctl




- 

Provide installer with an option for installing sources




- 

Manage missing Python dependencies

Ensure that all python dependencies (python3, pip and python-venv) are installed independently.




- 

Implement Docker-Compose environment

- Enrich ConfigMng
- Enrich Environment, DockerComposeEnv
- Drop init parameter: db_type
- Add environment tests



- 

Add/Remove services to/from environments




- 

Remove old Oracle/PostgreSQL code and documentation

Specific service plugins will be developed outside of the shepherd's
core repository.



- 

Add/Remove services to/from environments

- Add tests for adding services to environemnts




- 

Ensure key uniqueness in config

- Fix ConfigMng.original_placeholders not initialized in constructor
- Add ConfigMng.get_list_item_key to get unique identifiers for list elements




- 

Change 'start' commands to 'up'



- 

Add shell completion infrastructure

- Add shepctl_completion.sh (bash)
- Add completion/completion.py (centralized completion generation module)
- Add completion tests




- 

Remove noactive command from env scope

Remove old and inconsistent command.




- 

Add logging feature




- 

Change default service type name

Default service type name changed from 'docker' to 'image'.



- 

Add properties to ServiceTypeCfg and ServiceCfg

Added the following properties to both ServiceTypeCfg and ServiceCfg:

- hostname
- container_name
- labels
- workdir
- volumes
- networks
- extra_hosts

Previosly Dict fields have been changed to List:

- environment
- ports

Clean code and refactor.

Related to:#60


- 

Add Service render method

Added a render method for translating the Service's representation into
the target config format.
Initial Docker-Compose render has been added.




- 

Add service render command to CLI

- Add render CLI command for services for getting the rendered output for the
  target orchestrator engine
- Add require_active_env validation tag to CLI entrypoints requiring an
  active environment to be set
- Refactor/Clean code
- Fix tests




- 

Installer python implementation

Implement the installer managing dependencies (both for OS and python
packages) and providing options for installing bynaries and sources.
Implemented options are:

-m, --install-method: choose between binary and soures installation

-v, --verbose: enable verbose mode

-s, --skip-deps: don't automatically install dependencies

-f --force-source-download: download sources even if already present.

Tests are included in this commit.





- 

Add service-class concept to services

A service class is a concept for grouping related services inside an
environment.




- 

Design completion structure

- Split completion managers for categories
- Add completion service stubs
- Add completion database stubs
- Add completion environment
- Adjust tests



- 

Refactor Environment and Service to use directly their configurations

Environment and Service classes now use their respective configuration
objects directly without copy them.



- 

Change service-type to service-template

service-type concept has been changed to the more consistent
service-template concept.



- 

Remove unused .flake8 file



- 

Redesign env add CLI command

- Change 'add-resource' to 'add'
- Reorder arguments
- Fix completion




- 

Remove bootstrap CLI command

Removed inconsistent bootstrap command.




- 

Remove service's CLI commands from database CLI

Change db CLI behavior: service's CLI commands are now
available only via svc CLI.




- 

Refactor Environment/Service managers to get an EnvironmentCfg argument

Certain manager's (Env/Svc) methods have changed to accept an
EnvironmentCfg argument directly. This avoid to make an useless EnvironmentCfg lookup.




- 

Fix service/database CLI commands for taking a service-tag

Implement related completion as well.




- 

Improve test coverage



- 

Disable Click’s option parsing for __complete command

Do not parse options as Click options for special __complete command.
Skip validation/parsing of options and forward them.

Clean ServiceMng.get_service() guard.



- 

Add 'factory' property to ServiceTemplateCfg and ServiceCfg

Using 'template' key for choosing the service factory was logically
wrong; a 'factory' key is needed for this.
Change 'template' key in ServiceTemplateCfg to 'tag'.




- 

Add Environment Template

Add support for an environment template configuration, to optionally use when creating new environments.




- 

Add NetworkCfg to EnvironmentTemplateCfg and EnvironmentCfg

Added configuration for the environment's network.




- 

Add ServiceTemplateRefCfg to EnvironmentTemplateCfg

- Add references to service templates in environment templates.
- Refactor entity from_* methods in config.py.




- 

Implement InstallCompletion feature

Install the completion script into the system.

Script is installed by default into /etc/bash_completion.d/





- 

Add CLI env render command

Implemented the render() method for DockerComposeEnv to produce a
complete docker-compose YAML configuration, aggregating all
services defined in the environment. Output is compatible with
'docker compose up/down' commands.




- 

Increase coverage for test_svc_render_compose_service



- 

Rename organization's name

Rename all occurrences of LunaticFringers to MoonyFringers




- 

Polish and refine documentation

- 

Add networks render in DockerComposeEnv

Added rendering of networks for docker-compose environments.
Added additional and advanced docker configuration fields for networks.




- 

Add volumes to EnvironmentTemplateCfg and EnvironmentCfg

Added VolumeCfg for defining volumes for environment templates / environments.




- 

Allow .shpd.conf values to reference other variables

In .shpd.conf allow configuration values to reference other
variables using the ${VAR} syntax.

Example:

  base_dir=/opt/data
  log_dir=${base_dir}/logs
  cache_dir=${base_dir}/cache




- 

Add locally generated configuration files and index files for mkdocs, a
tool to locally render and navigate Markdown files present in the
repository



	## [0.0.0] - 2025-03-07


### <!-- 9 -->Other

- 

Initial commit

- 

Setup project



- 

Setup project sources structure

- Add shpdctl.conf & shpdctl.json
- Add requirements.txt
- Add modules
- Add shpdctl.py
- Add setup instructions in README.md



- 

Define CLI json model and provide python mapping




- 

Configure pyproject.toml & related CI




- 

Define sources structure




- 

Add tests for config parsing

- Add config/tests/test_config_parser.py
- Adjust Config model




- 

Fix lint workflow



- 

Add Unit Test workflow




- 

Bump codecov-action to v5




- 

Configure pytest to use codecov & Fix CI




- 

Add flake checks




- 

Adjust Config Json Model

- registry -> image (for docker images)




- 

Add load_user_values func to config.py

- Add a support function to loads a file holding
  the user's values in key=value format into a dictionary.




- 

Add Codecov badge to README



- 

Add load_config func to config.py

- Add load_config function to load shpdctl.json alongside with
  shpdctl.conf (merge user's values with the config).




- 

Add pull request template




- 

Add Markdown Architectural Decision Records




- 

Add PyInstaller Build Automation Script

Add the src/build.py script to automate the process of building shpdctl.




- 

Make venv consistent with workflows

Having venv stored into .venv directory (same level of src)
simplifies workflows management.

- Move Python virtual environment into .venv directory
- Update documentation
- Adjust github workflows




- 

Add build/release workflows




- 

Add build/release workflows: fix uploads




- 

Fix release workflow




- 

Remove cp command from release.yaml




<!-- generated by git-cliff -->
