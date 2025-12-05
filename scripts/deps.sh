install_dependencies() {
    echo -e "${YELLOW}Installing dependencies...${NC}"

    # Check if ap_manager is already installed
    if pip show ap_manager &> /dev/null; then
        echo -e "${GREEN}ap_manager is already installed${NC}"
        return 0
    fi

    if command -v apt &> /dev/null; then
        # Debian/Ubuntu
        apt update
        apt install -y network-manager hostapd dnsmasq iptables python3 python3-pip
    elif command -v dnf &> /dev/null; then
        # Fedora
        dnf install -y NetworkManager hostapd dnsmasq iptables python3 python3-pip
    elif command -v pacman &> /dev/null; then
        # Arch
        pacman -S --noconfirm networkmanager hostapd dnsmasq iptables python python-pip
    else
        echo -e "${RED}Unsupported package manager${NC}"
        return 1
    fi

    # Install ap_manager if not already installed
    if ! pip show ap_manager &> /dev/null; then
        pip install ap_manager
    fi

    echo -e "${GREEN}Dependencies installed successfully${NC}"
}
