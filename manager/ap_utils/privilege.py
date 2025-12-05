import os
import sys
import subprocess
import tempfile
import shutil
from functools import wraps
from typing import List


class PrivilegeManager:
    """
    Handle privilege escalation for network operations.
    Works with or without sudo, adapting to the environment.
    """

    def __init__(self):
        self.is_root = os.geteuid() == 0
        self.sudo_available = self._check_sudo()
        self.pkexec_available = self._check_pkexec()
        self.required_commands = ['iw', 'ip', 'hostapd', 'dnsmasq']
        self.check_commands()

    def _check_sudo(self) -> bool:
        """Check if sudo is available and configured for current user."""
        try:
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _check_pkexec(self) -> bool:
        """Check if pkexec (PolicyKit) is available."""
        return shutil.which('pkexec') is not None

    def check_commands(self) -> dict:
        """Check availability of required commands with/without sudo."""
        results = {}
        for cmd in self.required_commands:
            cmd_path = shutil.which(cmd)
            results[cmd] = {
                'available': cmd_path is not None,
                'path': cmd_path,
                'needs_root': self._check_command_needs_root(cmd)
            }
        return results

    def _check_command_needs_root(self, cmd: str) -> bool:
        """Test if command requires root privileges."""
        test_commands = {
            'iw': ['iw', 'dev'],
            'ip': ['ip', 'link', 'show'],
            'hostapd': ['hostapd', '--version'],
            'dnsmasq': ['dnsmasq', '--version']
        }

        if cmd not in test_commands:
            return True  # Assume needs root if unknown

        try:
            # Try without sudo
            result = subprocess.run(
                test_commands[cmd],
                capture_output=True,
                timeout=2
            )
            # If it fails, try with sudo to see if that fixes it
            if result.returncode != 0:
                sudo_result = subprocess.run(
                    ['sudo'] + test_commands[cmd],
                    capture_output=True,
                    timeout=2
                )
                return sudo_result.returncode == 0
            return False
        except Exception:
            return True

    def elevate_if_needed(self) -> bool:
        """
        Elevate privileges if needed. Returns True if elevated or already root.
        """
        if self.is_root:
            return True

        if not any(self.check_commands().values()):
            print("No network management commands available")
            return False

        # Check if we can run commands without elevation
        can_run_without_root = all(
            not info['needs_root']
            for info in self.check_commands().values()
            if info['available']
        )

        if can_run_without_root:
            return True

        # Need to elevate
        return self._request_elevation()

    def _request_elevation(self) -> bool:
        """Request privilege elevation from user."""
        if self.sudo_available:
            return self._elevate_with_sudo()
        elif self.pkexec_available:
            return self._elevate_with_pkexec()
        else:
            print("No privilege escalation method available")
            print("Please run as root or configure sudo/pkexec")
            return False

    def _elevate_with_sudo(self) -> bool:
        """Re-run script with sudo."""
        print("Network operations require root privileges")
        print("Attempting to elevate with sudo...")

        # Get current environment with PYTHONPATH preserved
        env = self.python_environment

        # Preserve important Python-related environment variables
        preserve_vars = [
            'PYTHONPATH',
            'PYTHONHOME',
            'VIRTUAL_ENV',
            'CONDA_PREFIX',
            'PATH'
        ]
        # Re-execute with sudo preserving environment timeout
        sudo_args = ['sudo', '-E']

        for var in preserve_vars:
            var_path = env.get(var, '')
            if var_path:
                sudo_args.extend(['env', f'{var}={var_path}'])

        # Re-execute with sudo
        os.execvp('sudo', sudo_args + [sys.executable] + sys.argv)
        return False  # execvp only returns on error

    @property
    def python_environment(self):
        return os.environ.copy()

    def _elevate_with_pkexec(self) -> bool:
        """Use PolicyKit for elevation with full environment preservation."""
        print("Using PolicyKit for privilege escalation...")

        # Get complete Python environment
        env = self.python_environment

        # Add POLKIT_ACTION for our custom policy
        action_file = self._create_polkit_action()
        env['POLKIT_ACTION'] = action_file

        # Get script path and arguments
        script_path = os.path.abspath(sys.argv[0])
        script_args = sys.argv[1:] if len(sys.argv) > 1 else []

        # Check if we're running as a module
        if script_path.endswith('.py') or os.path.isfile(script_path):
            # Running as script file
            cmd = [sys.executable, script_path] + script_args
        elif sys.argv[0] == '-m':
            # Running as Python module (-m flag)
            module_name = sys.argv[1] if len(sys.argv) > 1 else ''
            cmd = [sys.executable, '-m', module_name] + sys.argv[2:]
        else:
            # Could be a console script entry point
            cmd = [script_path] + script_args

        # Prepare environment variables for pkexec
        # pkexec doesn't preserve all env vars by default
        env_vars_to_preserve = [
            ('PYTHONPATH', env.get('PYTHONPATH', '')),
            ('PATH', env.get('PATH', '')),
            # ('VIRTUAL_ENV', env.get('VIRTUAL_ENV', '')),
            # ('CONDA_PREFIX', env.get('CONDA_PREFIX', '')),
            # ('HOME', env.get('HOME', '')),  # Important for user configs
            # ('USER', env.get('USER', '')),
            # ('LOGNAME', env.get('LOGNAME', '')),
            # ('XDG_RUNTIME_DIR', env.get('XDG_RUNTIME_DIR', '')),  # For DBus
            # ('DBUS_SESSION_BUS_ADDRESS', env.get('DBUS_SESSION_BUS_ADDRESS', '')),
        ]

        # Build pkexec command with preserved environment
        pkexec_cmd = ['pkexec']

        # Add environment preservation
        for var_name, var_value in env_vars_to_preserve:
            if var_value:
                pkexec_cmd.extend(['env', f'{var_name}={var_value}'])

        # Add the actual command
        pkexec_cmd.extend(cmd)

        try:
            print(f"Executing: {' '.join(pkexec_cmd[:5])}...")  # Don't print full cmd for security
            result = subprocess.run(
                pkexec_cmd,
                env=env,  # Pass the full environment
                capture_output=True,
                text=True
            )
            print(result.stdout)

            if result.returncode != 0:
                print(f"pkexec failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr[:500]}")  # Limit error output
            sys.exit(1)
            return result.returncode == 0

        except FileNotFoundError:
            print("pkexec not found. Please install policykit-1 package.")
            return False
        except Exception as e:
            print(f"Error using pkexec: {e}")
            return False
        finally:
            if os.path.exists(action_file):
                os.remove(action_file)

    def _create_polkit_action(self) -> str:
        """Create a temporary PolicyKit action file."""
        action_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>
  <action id="org.apmanager.network">
    <description>Manage WiFi access points</description>
    <message>Authentication is required to manage WiFi access points</message>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>auth_admin</allow_active>
    </defaults>
    <annotate key="org.freedesktop.policykit.exec.path">{sys.executable}</annotate>
    <annotate key="org.freedesktop.policykit.exec.argv1">{sys.argv[0]}</annotate>
  </action>
</policyconfig>"""

        fd, path = tempfile.mkstemp(prefix='ap_manager_polkit_', suffix='.policy')
        with os.fdopen(fd, 'w') as f:
            f.write(action_content)
        return path

    def run_command(
        self,
        cmd: List[str],
        *args,
        capture_output: bool = True,
        check: bool = True,
        text: bool = True,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        Run command with appropriate privilege escalation.
        """
        # Check if command needs root
        base_cmd = cmd[0]
        needs_root = self._check_command_needs_root(base_cmd)

        # Prepare command
        full_cmd = cmd + list(args)

        # Add privilege escalation if needed and not root
        if needs_root and not self.is_root:
            if self.sudo_available:
                full_cmd = ['sudo'] + full_cmd
            elif self.pkexec_available:
                full_cmd = ['pkexec'] + full_cmd
            else:
                raise PermissionError(
                    f"Command '{base_cmd}' requires root privileges but "
                    "no escalation method is available"
                )

        # Run the command
        try:
            return subprocess.run(
                full_cmd,
                capture_output=capture_output,
                check=check,
                text=text,
                **kwargs
            )
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {' '.join(full_cmd)}")
            print(f"Error: {e.stderr.decode() if e.stderr else str(e)}")
            raise


# Decorator for functions that need network privileges
def require_network_privileges(func):
    """Decorator to ensure network privileges are available."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        priv_mgr = PrivilegeManager()
        if not priv_mgr.elevate_if_needed():
            raise PermissionError(
                "Insufficient privileges for network operations"
            )
        return func(*args, **kwargs)
    return wrapper


# Context manager for temporary privilege escalation
class NetworkPrivileges:
    """Context manager for network operations requiring privileges."""

    def __init__(self, auto_elevate: bool = True):
        self.priv_mgr = PrivilegeManager()
        self.auto_elevate = auto_elevate
        self.was_elevated = False

    def __enter__(self):
        if self.auto_elevate:
            self.was_elevated = self.priv_mgr.elevate_if_needed()
        return self.priv_mgr

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass


# Convenience functions for common operations
def create_virtual_interface(interface: str, virt_interface: str) -> bool:
    """Create a virtual WiFi interface."""
    with NetworkPrivileges() as priv:
        result = priv.run_command(
            ['iw', 'dev', interface, 'interface', 'add', virt_interface, 'type', '__ap']
        )
        return result.returncode == 0


def setup_ap_interface(interface: str, ip: str = "192.168.4.1") -> bool:
    """Setup access point interface."""
    with NetworkPrivileges() as priv:
        # Bring interface down
        priv.run_command(['ip', 'link', 'set', interface, 'down'])

        # Set MAC address (optional, helps with some drivers)
        priv.run_command(['ip', 'link', 'set', interface, 'address', '02:00:00:00:00:01'])

        # Bring interface up
        priv.run_command(['ip', 'link', 'set', interface, 'up'])

        # Assign IP address
        priv.run_command(['ip', 'addr', 'add', f'{ip}/24', 'dev', interface])

        return True


# Main entry point with auto-elevation
def main():
    """Main function with automatic privilege handling."""
    print("AP Manager - Automatic Privilege Handling")

    # Check and elevate if needed
    priv_mgr = PrivilegeManager()

    if not priv_mgr.elevate_if_needed():
        sys.exit(1)

    print("✓ Privileges available for network operations")

    # Now you can run your AP management code
    # Example:
    try:
        # Create virtual interface
        if create_virtual_interface('wlan0', 'xap0'):
            print("✓ Virtual interface created")

        # Setup AP
        if setup_ap_interface('xap0'):
            print("✓ AP interface configured")

        # Continue with your AP setup...

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
