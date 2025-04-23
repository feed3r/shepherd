#!/bin/bash

export RED='\033[0;31m'
export NC='\033[0m'
export YELLOW='\033[0;33m'
export GREEN='\033[0;32m'
export BLUE='\033[0;36m'

export verbose=false
export skip_ensure_deps=false
export SCRIPT_DIR=$(dirname "$(realpath "$0")")

export INSTALL_DIR=$(realpath ${INSTALL_DIR:-"/opt/sctl"})
export USERHOME=$(getent passwd $USER | cut -d: -f6)
export TMPDIR=${TMPDIR:-"/tmp"}
export LO_SHEPHERD_CFG_PATH=${LO_SHEPHERD_CFG_PATH:-"$HOME/.sctl.json"}
export HUB_LOGOBJECT_CH_REG=${HUB_LOGOBJECT_CH_REG:-"hub.logobject.ch/lointernal"}
export HUB_LOGOBJECT_CH_USR=${HUB_LOGOBJECT_CH_PSW:-"robot\$lointernal+k8s"}
export HUB_LOGOBJECT_CH_PSW=${HUB_LOGOBJECT_CH_PSW:-"vwNPq3zs0L8uidT5I9U3LogVmHM1hviG"}

export hlp_module_sh="hlp_module.sh"
export db_module_sh="db_module.sh"
export pg_module_sh="pg_module.sh"
export ora_module_sh="ora_module.sh"
export loas_module_sh="loas_module.sh"
export env_module_sh="env_module.sh"
export reg_module_sh="reg_module.sh"
export sys_module_sh="sys_module.sh"
export svc_module_sh="svc_module.sh"

usage(){
  cat << EOF
usage: sctl_installer [options]

  -v, --verbose             Enable verbose mode.
  -s, --skip                Skip ensure dependencies
  -h, --help                Show help.

commands:
  install                   Install sctl as system tool (root privileges are required).
  uninstall                 Uninstall sctl (root privileges are required).

environment variables:
  INSTALL_DIR               Specify the host's directory to install the tool in.
  LO_SHEPHERD_CFG_PATH      Specify sctl's config file (default: ~/.sctl.json).
EOF
}

#########
# INSTALL
#########

function get_linux_distribution() {
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "$ID"
  elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    echo "$DISTRIB_ID"
  else
    echo "unknown"
  fi
}

function get_lsb_release_codename() {
  if command -v lsb_release &> /dev/null; then
    codename=$(lsb_release -cs)
  elif [ -f /etc/os-release ]; then
    . /etc/os-release
    codename="$VERSION_CODENAME"
  else
    codename="unknown"
  fi

  # Handle specific case for Debian Trixie
  # where the repository should point to Bookworm
  # This is a workaround for the fact that Trixie is not yet released
  # and the Docker repository does not have a Trixie entry.
  # This should be removed once Trixie is officially released.
  if [ "$codename" == "trixie" ]; then
    echo "bookworm"
  else
    echo "$codename"
  fi
}

export LINUX_DISTRO=$(get_linux_distribution) #es. debian
export LINUX_RELEASE=$(get_lsb_release_codename) #es. bookworm

function ensure_deps() {
  echo "Ensuring dependencies for $LINUX_DISTRO $LINUX_RELEASE..."
  sudo apt-get update && \
  sudo apt-get -y install --no-install-recommends \
       bc \
       jq \
       curl \
       rsync \
       apt-transport-https \
       ca-certificates \
       software-properties-common

  KEYRING_PATH="/usr/share/keyrings/docker-archive-keyring.gpg"
  if [ ! -f "$KEYRING_PATH" ]; then
      echo "Adding Docker GPG key..."
      curl -fsSL https://download.docker.com/linux/$LINUX_DISTRO/gpg | sudo gpg --dearmor -o $KEYRING_PATH
  else
      echo "Docker GPG key already exists."
  fi

  # Use the codename from lsb_release or /etc/os-release
  echo "Using distribution: $LINUX_DISTRO"
  echo "Using release: $LINUX_RELEASE"

  REPO_STRING="deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$LINUX_DISTRO $LINUX_RELEASE stable"

  SOURCES_LIST="/etc/apt/sources.list.d/docker.list"
  if ! grep -Fxq "$REPO_STRING" $SOURCES_LIST 2>/dev/null; then
      echo "Adding Docker repository..."
      echo "$REPO_STRING" | sudo tee $SOURCES_LIST > /dev/null
  else
      echo "Docker repository already exists."
  fi

  sudo apt update

  if ! dpkg -l | grep -qw docker-ce; then
      sudo apt install docker-ce docker-ce-cli containerd.io -y
      DOCKER_INSTALLED="true"
  else
      echo "Docker is already installed."
      DOCKER_INSTALLED="false"
  fi

  sudo docker --version

  if ! command -v docker-compose &> /dev/null; then
      echo "Installing Docker Compose..."
      sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      sudo chmod +x /usr/local/bin/docker-compose
      echo "Docker Compose has been installed successfully."
  else
      echo "Docker Compose is already installed."
  fi

  docker-compose --version

  sudo systemctl enable docker

  if [ "$DOCKER_INSTALLED" == "true" ]; then
      sudo groupadd docker
      sudo usermod -aG docker $USER
      echo "Docker has been installed successfully."
      echo "Please log out and log back in to apply the necessary group changes."
  else
      echo "Docker installation was not required or it was already installed."
  fi

  echo "$HUB_LOGOBJECT_CH_PSW" | docker login $HUB_LOGOBJECT_CH_REG --username "$HUB_LOGOBJECT_CH_USR" --password-stdin
}

function ensure_deps_ubuntu_2404() {
  ensure_deps_ubuntu_2204
}

function ensure_deps_ubuntu_2204() {
  sudo apt-get update && \
  sudo apt-get -y install --no-install-recommends \
       bc \
       jq \
       curl \
       rsync \
       apt-transport-https \
       ca-certificates \
       software-properties-common

  KEYRING_PATH="/usr/share/keyrings/docker-archive-keyring.gpg"
  if [ ! -f "$KEYRING_PATH" ]; then
      echo "Adding Docker GPG key..."
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o $KEYRING_PATH
  else
      echo "Docker GPG key already exists."
  fi

  REPO_STRING="deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  SOURCES_LIST="/etc/apt/sources.list.d/docker.list"
  if ! grep -Fxq "$REPO_STRING" $SOURCES_LIST 2>/dev/null; then
      echo "Adding Docker repository..."
      echo "$REPO_STRING" | sudo tee $SOURCES_LIST > /dev/null
  else
      echo "Docker repository already exists."
  fi

  sudo apt update

  if ! dpkg -l | grep -qw docker-ce; then
      sudo apt install docker-ce docker-ce-cli containerd.io -y
      DOCKER_INSTALLED="true"
  else
      echo "Docker is already installed."
      DOCKER_INSTALLED="false"
  fi

  sudo docker --version

  if ! command -v docker-compose &> /dev/null; then
      echo "Installing Docker Compose..."
      sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      sudo chmod +x /usr/local/bin/docker-compose
      echo "Docker Compose has been installed successfully."
  else
      echo "Docker Compose is already installed."
  fi

  docker-compose --version

  sudo systemctl enable docker

  if [ "$DOCKER_INSTALLED" == "true" ]; then
      sudo groupadd docker
      sudo usermod -aG docker $USER
      echo "Docker has been installed successfully."
      echo "Please log out and log back in to apply the necessary group changes."
  else
      echo "Docker installation was not required or it was already installed."
  fi

  echo "$HUB_LOGOBJECT_CH_PSW" | docker login $HUB_LOGOBJECT_CH_REG --username "$HUB_LOGOBJECT_CH_USR" --password-stdin
}

function ensure_deps_ubuntu_2404() {
  ensure_deps_ubuntu_2204
}

get_system_type(){
  local env=$(uname -r)
  if [[ "$env" == *"WSL"* ]] || [[ "$env" == *"microsoft"* ]]; then
    echo "WSL"
  else
    echo "LINUX"
  fi
}

function install_shepherd() {
  if [ $skip_ensure_deps == false ]; then
    echo -e "${BLUE}Ensuring dependencies...${NC}"
    if grep -q "Ubuntu" /etc/os-release && grep -q "22.04" /etc/os-release; then
        ensure_deps_ubuntu_2204
    elif grep -q "Ubuntu" /etc/os-release && grep -q "24.04" /etc/os-release; then
        ensure_deps_ubuntu_2404
    elif grep -q "Debian" /etc/os-release; then
        ensure_deps
    else
      echo "Unrecognized distribution, you have to ensure all dependencies manually."
    fi
  fi

  echo -e "${BLUE}Installing sctl...${NC}"
  if [[ -d $INSTALL_DIR ]]; then
      old_version=$(cat $INSTALL_DIR/version)
      new_version=$(cat $SCRIPT_DIR/version)
      echo -e "${YELLOW}### Upgrading ${old_version} -> ${new_version} ###${NC}"
      sudo rm -rf $INSTALL_DIR
  fi
  sudo mkdir -p $INSTALL_DIR
  sudo cp $SCRIPT_DIR/version \
          $SCRIPT_DIR/sctl.sh \
          $SCRIPT_DIR/sctl_installer.sh \
          $SCRIPT_DIR/sctl.json \
          $SCRIPT_DIR/$hlp_module_sh \
          $SCRIPT_DIR/$db_module_sh \
          $SCRIPT_DIR/$pg_module_sh \
          $SCRIPT_DIR/$ora_module_sh \
          $SCRIPT_DIR/$loas_module_sh \
          $SCRIPT_DIR/$env_module_sh \
          $SCRIPT_DIR/$reg_module_sh \
          $SCRIPT_DIR/$sys_module_sh \
          $SCRIPT_DIR/$svc_module_sh \
          $INSTALL_DIR

  sudo cp -R $SCRIPT_DIR/db $INSTALL_DIR
  sudo cp -R $SCRIPT_DIR/docker $INSTALL_DIR
  sudo cp -R $SCRIPT_DIR/provision $INSTALL_DIR
  sudo chown -R $USER:$USER $INSTALL_DIR
  sudo chmod 750 $INSTALL_DIR/*
  sudo ln -s $INSTALL_DIR/sctl.sh /usr/bin/sctl > /dev/null 2>&1
  sudo ln -s $INSTALL_DIR/sctl_installer.sh /usr/bin/sctl_installer > /dev/null 2>&1
  sudo cp $SCRIPT_DIR/sctl_completion.sh /etc/bash_completion.d/
  sudo chmod 755 /etc/bash_completion.d/sctl_completion.sh

  # Backup existing sctl.json if it exists
  USERHOME=$(getent passwd $USER | cut -d: -f6)
  if [ -f "$USERHOME/.sctl.json" ]; then
    echo -e "${BLUE}### Backing up existing ~/.sctl.json ###${NC}"
    sudo cp -a "$USERHOME/.sctl.json" "$USERHOME/.sctl.json.bak"
  fi

  if [ -f "$USERHOME/._sctl.json" ]; then
    sudo mv $USERHOME/._sctl.json $USERHOME/.sctl.json
  fi

  if [ -f "$USERHOME/.sctl.json" ]; then
    echo -e "${BLUE}Upgrading ~/.sctl.json...${NC}"
    user_envs=$(jq '.envs' "$USERHOME/.sctl.json")
    jq --argjson user_envs "$user_envs" '.envs = $user_envs' $SCRIPT_DIR/sctl.json | sudo tee "$TMPDIR/sctl.json" > /dev/null
  else
    sudo cp $SCRIPT_DIR/sctl.json "$TMPDIR/sctl.json"
  fi
  system=$(get_system_type)
  sudo jq --arg value "$system" '.system = $value' "$TMPDIR/sctl.json" | sudo tee "$TMPDIR/sctl_new.json" > /dev/null
  sudo cp "$TMPDIR/sctl_new.json" "$USERHOME/.sctl.json"
  sudo chown $USER:$USER "$USERHOME/.sctl.json"
  sudo rm "$TMPDIR/sctl.json" "$TMPDIR/sctl_new.json"

  echo "sctl installed."
}

function install(){
  install_shepherd
}

function uninstall(){
  echo -e "${BLUE}Uninstalling sctl...${NC}"

  echo -e "${BLUE}Cleaning up containers and images...${NC}"
  imageIds=$(docker images | sed 1d | grep "hub.logobject.ch/lointernal" |awk '{print $3}')

  echo $imageIds | while read -d ' ' -r imageId; do
      docker ps -q --filter ancestor=$imageId | xargs -r docker stop
      docker ps -q --filter ancestor=$imageId | xargs -r docker rm
      docker rmi $imageIds
  done;

  sudo mv $USERHOME/.sctl.json $USERHOME/._sctl.json

  sudo rm -rf $INSTALL_DIR
  sudo rm -rf /etc/bash_completion.d/sctl_completion.sh
  sudo rm -rf /usr/bin/sctl
  echo "sctl uninstalled"
}

############
# ENTRYPOINT
############

OPTIONS=vsh
LONGOPTIONS=verbose,skip,help
PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTIONS --name "$0" -- "$@")

if [[ $? -ne 0 ]]; then
  exit 2
fi

eval set -- "$PARSED"

while true; do
  case "$1" in
    -v|--verbose)
      export verbose=true
      shift
      ;;
    -s|--skip)
      export skip_ensure_deps=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unexpected option: $1"
      exit 3
      ;;
  esac
done

usage_err=false

case ${1} in
  install)
    install || exit 1
  ;;
  uninstall)
    uninstall || exit 1
  ;;
  *)
    usage_err=true
  ;;
esac

if [[ $usage_err == true ]]; then
  usage
  exit 1
fi
