#!/usr/bin/env bash
# =================================================================
# GeoPulse CLI — One-Step Automated Installer
# Supported OS: Linux, macOS, Termux, Debian/Ubuntu, Arch, Fedora
# =================================================================

set -e

CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "  _____            _____  dWdzc2Ug"
echo " / ____/__  ____  / __ \__  __/ ____/ / (_)"
echo "/ / __/ _ \/ __ \/ /_/ / / / / /   / / / / "
echo "/ /_/ /  __/ /_/ // ____/ / / / /___/ / / /  "
echo "\____/\___/\____//_/   /_/ /_/\____/_/_/_/   "
echo -e "${RESET}${GREEN} Installing GeoPulse CLI v2.0...${RESET}\n"

# Detect Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python3 not found. Attempting package installation...${RESET}"
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3 python3-pip
    elif command -v pkg &> /dev/null; then
        pkg install -y python3
    elif command -v brew &> /dev/null; then
        brew install python3
    else
        echo -e "${RED}Error: Python3 is required. Please install Python3 manually.${RESET}"
        exit 1
    fi
fi

INSTALL_DIR="/usr/local/bin"
BIN_NAME="geopulse"
ALIAS_NAME="ip-tracer"

if [ -w "$INSTALL_DIR" ]; then
    cp geopulse.py "$INSTALL_DIR/$BIN_NAME"
    chmod +x "$INSTALL_DIR/$BIN_NAME"
    ln -sf "$INSTALL_DIR/$BIN_NAME" "$INSTALL_DIR/$ALIAS_NAME"
else
    echo -e "${YELLOW}Installing to $INSTALL_DIR (requires elevated privileges)...${RESET}"
    sudo cp geopulse.py "$INSTALL_DIR/$BIN_NAME"
    sudo chmod +x "$INSTALL_DIR/$BIN_NAME"
    sudo ln -sf "$INSTALL_DIR/$BIN_NAME" "$INSTALL_DIR/$ALIAS_NAME"
fi

echo -e "\n${GREEN}${BOLD}✔ Installation Successful!${RESET}"
echo -e "${CYAN}Usage:${RESET}"
echo -e "  ${BOLD}geopulse${RESET}                 Launch interactive menu"
echo -e "  ${BOLD}geopulse -t 8.8.8.8${RESET}      Trace specific IP / Domain"
echo -e "  ${BOLD}geopulse -m${RESET}              Trace your own public IP"
echo -e "  ${BOLD}geopulse --json -t 8.8.8.8${RESET} Output JSON format\n"
