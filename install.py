#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Colors for output


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_colored(message, color):
    print(f"{color}{message}{Colors.NC}")


def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        print_colored("This script must be run as root", Colors.RED)
        sys.exit(1)


def create_directories():
    """Create necessary installation directories"""
    install_dir = Path("/opt/ap_manager")
    base_dir = Path("/etc/ap_manager")

    # Create directories
    (install_dir / "scripts").mkdir(parents=True, exist_ok=True)
    # (install_dir / "manager" / "core").mkdir(parents=True, exist_ok=True)
    # (install_dir / "manager" / "ap_utils").mkdir(parents=True, exist_ok=True)
    # (install_dir / "manager" / "ui").mkdir(parents=True, exist_ok=True)
    # (install_dir / "manager" / "config").mkdir(parents=True, exist_ok=True)
    (base_dir / "proc").mkdir(parents=True, exist_ok=True)

    # Set permissions
    shutil.chown(str(base_dir), user='root', group='root')
    os.chmod(str(base_dir), 0o777)


def copy_files():
    """Copy installation files to their destinations"""
    install_dir = Path("/opt/ap_manager")

    # Copy scripts
    for script in Path("scripts").glob("*.sh"):
        shutil.copy(script, install_dir / "scripts")

    # Make scripts executable
    for script in (install_dir / "scripts").glob("*.sh"):
        script.chmod(777)

    # Copy manager files (commented out)
    # shutil.copytree("manager", install_dir / "manager")


def create_symlink():
    """Create symlink in /usr/local/bin for easy access"""
    try:
        os.symlink("/home/skye/.local/bin/ap_manager", "/usr/local/bin/ap_manager")
    except FileExistsError:
        # If symlink already exists, remove it first
        os.remove("/usr/local/bin/ap_manager")
        os.symlink("/home/skye/.local/bin/ap_manager", "/usr/local/bin/ap_manager")


def setup_sudoers():
    """Setup sudoers configuration"""
    print_colored("Setting up sudoers...", Colors.YELLOW)
    sudoers_script = Path("/opt/ap_manager/scripts/sudors_edit.sh")

    if sudoers_script.exists():
        try:
            # Use shell=True to properly execute the shell script
            subprocess.run([str(sudoers_script)], shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print_colored(f"Failed to execute sudoers script: {e}", Colors.RED)
            sys.exit(1)


def install_dependencies():
    """Install dependencies"""
    print_colored("Installing dependencies...", Colors.YELLOW)
    deps_script = Path("/opt/ap_manager/scripts/deps.sh")
    if deps_script.exists():
        subprocess.run([str(deps_script)], check=True, shell=True)


def setup_systemd():
    """Create and enable systemd service"""
    service_path = Path("/etc/systemd/system/ap_manager.service")
    shutil.copy("scripts/ap_manager.service", service_path)
    subprocess.run(["systemctl", "daemon-reload"], check=True)


def main():
    print_colored("Installing ap_manager Manager...", Colors.GREEN)
    check_root()

    create_directories()
    copy_files()
    create_symlink()
    setup_sudoers()
    install_dependencies()
    setup_systemd()

    print_colored("\nInstallation completed successfully!", Colors.GREEN)
    print()
    print("Usage examples:")
    print("  ap_manager start          # Start hotspot")
    print("  ap_manager configure      # Interactive configuration")
    print("  ap_manager status         # Check status")
    print("  ap_manager stop           # Stop hotspot")
    print()
    print("To enable automatic startup:")
    print(f"  systemctl enable {Colors.BLUE}ap_manager.service{Colors.NC}")


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script must be run as root")
        sys.exit(1)

    main()
