import platform
import subprocess

def get_os_info() -> str:
    """Detect OS and Linux distribution."""
    os_name = platform.system()
    if os_name == "Linux":
        try:
            # Try to get Linux distribution info using lsb_release
            result = subprocess.run(
                ["lsb_release", "-ds"],
                capture_output=True,
                text=True,
                check=True
            )
            distro_info = result.stdout.strip().strip('"')
            if distro_info:
                return distro_info
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Fallback: Try reading /etc/os-release for distribution info
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        distro_info = line.split("=")[1].strip().strip('"')
                        return distro_info
        except Exception:
            pass

        # Final fallback to generic Linux info
        return "Linux (Unknown Distribution)"
    return os_name

def get_os_type() -> str:
    """Get OS type (Windows, Linux, macOS)."""
    return platform.system()