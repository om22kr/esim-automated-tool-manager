import platform
import shutil
import subprocess



# PACKAGE MANAGER BASE CLASS


class PackageManager:
    

    name = "Unknown"

    def is_available(self):
        

        return False

    def install(self, package_id):
        

        raise NotImplementedError

    def update(self, package_id):
        

        raise NotImplementedError

    def uninstall(self, package_id):
        

        raise NotImplementedError

    def get_version(self, package_id):
        

        raise NotImplementedError



# COMMAND RUNNER


def run_command(command):
    

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120
        )

        return result

    except FileNotFoundError:

        return None

    except subprocess.TimeoutExpired:

        return None

    except Exception:

        return None



# WINGET


class WingetManager(PackageManager):

    name = "Winget"

    def is_available(self):
        """
        Check whether Winget is installed.
        """

        return shutil.which("winget") is not None

    def install(self, package_id):
        

        if not self.is_available():

            return False, (
                "Winget is not available."
            )

        command = [
            "winget",
            "install",
            "--id",
            package_id,
            "--exact",
            "--accept-source-agreements",
            "--accept-package-agreements"
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Winget."
            )

        if result.returncode == 0:

            return True, (
                "Installation completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Winget exited with code "
            f"{result.returncode}."
        )

    def update(self, package_id):
        """
        Update a package using Winget.
        """

        if not self.is_available():

            return False, (
                "Winget is not available."
            )

        command = [
            "winget",
            "upgrade",
            "--id",
            package_id,
            "--exact",
            "--accept-source-agreements",
            "--accept-package-agreements"
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Winget."
            )

        if result.returncode == 0:

            return True, (
                "Update completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Winget exited with code "
            f"{result.returncode}."
        )

    def uninstall(self, package_id):
        

        if not self.is_available():

            return False, (
                "Winget is not available."
            )

        command = [
            "winget",
            "uninstall",
            "--id",
            package_id,
            "--exact"
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Winget."
            )

        if result.returncode == 0:

            return True, (
                "Uninstallation completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Winget exited with code "
            f"{result.returncode}."
        )

    def get_version(self, package_id):
        

        if not self.is_available():

            return None

        command = [
            "winget",
            "list",
            "--id",
            package_id,
            "--exact"
        ]

        result = run_command(command)

        if result is None:
            return None

        if result.returncode != 0:
            return None

        return result.stdout.strip()



# APT


class AptManager(PackageManager):

    name = "APT"

    def is_available(self):
        """
        Check whether APT is available.
        """

        return (
            shutil.which("apt-get") is not None
        )

    def install(self, package_id):
        

        if not self.is_available():

            return False, (
                "APT is not available."
            )

        command = [
            "sudo",
            "apt-get",
            "install",
            "-y",
            package_id
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute APT."
            )

        if result.returncode == 0:

            return True, (
                "Installation completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"APT exited with code "
            f"{result.returncode}."
        )

    def update(self, package_id):
        

        if not self.is_available():

            return False, (
                "APT is not available."
            )

        command = [
            "sudo",
            "apt-get",
            "install",
            "--only-upgrade",
            "-y",
            package_id
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute APT."
            )

        if result.returncode == 0:

            return True, (
                "Update completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"APT exited with code "
            f"{result.returncode}."
        )

    def uninstall(self, package_id):
        

        if not self.is_available():

            return False, (
                "APT is not available."
            )

        command = [
            "sudo",
            "apt-get",
            "remove",
            "-y",
            package_id
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute APT."
            )

        if result.returncode == 0:

            return True, (
                "Uninstallation completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"APT exited with code "
            f"{result.returncode}."
        )

    def get_version(self, package_id):
        

        if shutil.which("dpkg-query") is None:

            return None

        command = [
            "dpkg-query",
            "-W",
            "-f=${Version}",
            package_id
        ]

        result = run_command(command)

        if result is None:
            return None

        if result.returncode != 0:
            return None

        version = result.stdout.strip()

        if version:
            return version

        return None



# HOMEBREW


class HomebrewManager(PackageManager):

    name = "Homebrew"

    def is_available(self):
        

        return shutil.which("brew") is not None

    def install(self, package_id):
        

        if not self.is_available():

            return False, (
                "Homebrew is not available."
            )

        command = [
            "brew",
            "install",
            package_id
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Homebrew."
            )

        if result.returncode == 0:

            return True, (
                "Installation completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Homebrew exited with code "
            f"{result.returncode}."
        )

    def update(self, package_id):
        

        if not self.is_available():

            return False, (
                "Homebrew is not available."
            )

        command = [
            "brew",
            "upgrade",
            package_id
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Homebrew."
            )

        if result.returncode == 0:

            return True, (
                "Update completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Homebrew exited with code "
            f"{result.returncode}."
        )

    def uninstall(self, package_id):
        

        if not self.is_available():

            return False, (
                "Homebrew is not available."
            )

        command = [
            "brew",
            "uninstall",
            package_id
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Homebrew."
            )

        if result.returncode == 0:

            return True, (
                "Uninstallation completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Homebrew exited with code "
            f"{result.returncode}."
        )

    def get_version(self, package_id):
        

        if not self.is_available():

            return None

        command = [
            "brew",
            "list",
            "--versions",
            package_id
        ]

        result = run_command(command)

        if result is None:
            return None

        if result.returncode != 0:
            return None

        output = result.stdout.strip()

        if not output:
            return None

        parts = output.split()

        if len(parts) >= 2:
            return parts[-1]

        return None



# CHOCOLATEY


class ChocolateyManager(PackageManager):

    name = "Chocolatey"

    def is_available(self):
        

        return shutil.which("choco") is not None

    def install(self, package_id):
        

        if not self.is_available():

            return False, (
                "Chocolatey is not available."
            )

        command = [
            "choco",
            "install",
            package_id,
            "-y"
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Chocolatey."
            )

        if result.returncode == 0:

            return True, (
                "Installation completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Chocolatey exited with code "
            f"{result.returncode}."
        )

    def update(self, package_id):
        

        if not self.is_available():

            return False, (
                "Chocolatey is not available."
            )

        command = [
            "choco",
            "upgrade",
            package_id,
            "-y"
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Chocolatey."
            )

        if result.returncode == 0:

            return True, (
                "Update completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Chocolatey exited with code "
            f"{result.returncode}."
        )

    def uninstall(self, package_id):
        

        if not self.is_available():

            return False, (
                "Chocolatey is not available."
            )

        command = [
            "choco",
            "uninstall",
            package_id,
            "-y"
        ]

        result = run_command(command)

        if result is None:

            return False, (
                "Failed to execute Chocolatey."
            )

        if result.returncode == 0:

            return True, (
                "Uninstallation completed successfully."
            )

        return False, (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Chocolatey exited with code "
            f"{result.returncode}."
        )

    def get_version(self, package_id):
        

        if not self.is_available():

            return None

        command = [
            "choco",
            "list",
            "--local-only",
            "--exact",
            package_id
        ]

        result = run_command(command)

        if result is None:
            return None

        if result.returncode != 0:
            return None

        output = result.stdout.strip()

        if not output:
            return None

        match = output.split()

        if len(match) >= 2:
            return match[-1]

        return None



# PACKAGE MANAGER REGISTRY


PACKAGE_MANAGERS = {
    "winget": WingetManager(),
    "apt": AptManager(),
    "homebrew": HomebrewManager(),
    "chocolatey": ChocolateyManager()
}



# GET PACKAGE MANAGER


def get_package_manager(name):
    

    if not name:
        return None

    return PACKAGE_MANAGERS.get(
        name.lower()
    )



# DETECT AVAILABLE PACKAGE MANAGERS


def get_available_package_managers():
    

    available = []

    for name, manager in PACKAGE_MANAGERS.items():

        if manager.is_available():
            available.append(name)

    return available



# DETECT CURRENT PLATFORM


def get_current_platform():
    

    system = platform.system().lower()

    if system == "windows":
        return "windows"

    if system == "linux":
        return "linux"

    if system == "darwin":
        return "macos"

    return "unknown"