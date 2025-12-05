import os
import subprocess


def run_as_root(cmd, *args):
    """Run a command with sudo if not root"""
    full_cmd = [cmd] + list(args)

    if os.geteuid() != 0:
        full_cmd = ['sudo'] + full_cmd

    try:
        result = subprocess.run(
            full_cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return None
