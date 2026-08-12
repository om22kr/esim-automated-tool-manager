import platform
import subprocess
import os
import urllib.request
import tempfile
import shutil
import re
import hashlib
from pathlib import Path

import py7zr

from version_checker import save_installed_version
from package_managers import (
    get_package_manager,
    get_current_platform
)


# Platform Package Manager

def get_tool_package_manager(tool):
    """
    Get the package manager configured for the
    current operating system.
    """

    current_platform = get_current_platform()

    package_managers = tool.get(
        "package_managers",
        {}
    )

    manager_name = package_managers.get(
        current_platform
    )

    # Backward compatibility
    if not manager_name:
        manager_name = tool.get(
            "package_manager"
        )

    return get_package_manager(
        manager_name
    )


# Generic installation

def install_tool(tool):
    """
    Install a tool using the package manager
    configured for the current platform.
    """

    current_platform = get_current_platform()

    if current_platform not in tool.get(
        "platforms",
        []
    ):
        return False, (
            f"{tool['name']} does not support "
            f"the current platform: "
            f"{current_platform}"
        )

    package_managers = tool.get(
        "package_managers",
        {}
    )

    manager_name = package_managers.get(
        current_platform
    )

    # Backward compatibility
    if not manager_name:
        manager_name = tool.get(
            "package_manager"
        )

    # --------------------------------------------------------
    # SOURCEFORGE SPECIAL CASE
    # --------------------------------------------------------

    if manager_name == "sourceforge":

        return install_from_sourceforge(
            tool
        )

    # --------------------------------------------------------
    # PACKAGE MANAGER
    # --------------------------------------------------------

    manager = get_package_manager(
        manager_name
    )

    if manager is None:

        return False, (
            f"Package manager '{manager_name}' "
            f"is not supported."
        )

    if not manager.is_available():

        return False, (
            f"{manager.name} is not available "
            f"on this system."
        )

    package_ids = tool.get(
        "package_id"
    )

    if isinstance(
        package_ids,
        dict
    ):

        package_id = package_ids.get(
            current_platform
        )

    else:

        package_id = package_ids

    if not package_id:

        return False, (
            f"No package ID configured for "
            f"{tool['name']} on "
            f"{current_platform}."
        )

    return manager.install(
        package_id
    )


# Generic update

# Generic Update

def update_tool(tool):
    """
    Update a tool using the package manager
    configured for the current platform.
    """

    current_platform = get_current_platform()

    if current_platform not in tool.get(
        "platforms",
        []
    ):
        return False, (
            f"{tool['name']} does not support "
            f"the current platform: "
            f"{current_platform}"
        )

    package_managers = tool.get(
        "package_managers",
        {}
    )

    manager_name = package_managers.get(
        current_platform
    )

    # Backward compatibility
    if not manager_name:
        manager_name = tool.get(
            "package_manager"
        )

    # --------------------------------------------------------
    # SOURCEFORGE SPECIAL CASE
    # --------------------------------------------------------

    if manager_name == "sourceforge":

        return update_from_sourceforge(
            tool
        )

    # --------------------------------------------------------
    # PACKAGE MANAGER
    # --------------------------------------------------------

    manager = get_package_manager(
        manager_name
    )

    if manager is None:

        return False, (
            f"Package manager '{manager_name}' "
            f"is not supported."
        )

    if not manager.is_available():

        return False, (
            f"{manager.name} is not available "
            f"on this system."
        )

    package_ids = tool.get(
        "package_id"
    )

    if isinstance(
        package_ids,
        dict
    ):

        package_id = package_ids.get(
            current_platform
        )

    else:

        package_id = package_ids

    if not package_id:

        return False, (
            f"No package ID configured for "
            f"{tool['name']} on "
            f"{current_platform}."
        )

    return manager.update(
        package_id
    )


# Sha-256

def calculate_sha256(file_path):
    """
    Calculate SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb"
    ) as file:

        while True:

            data = file.read(
                1024 * 1024
            )

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


# Download File

def download_file(url, destination):
    """
    Download a file from a URL.
    """

    try:

        print(
            f"Downloading: {url}"
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "eSim-Automated-Tool-Manager/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            with open(
                destination,
                "wb"
            ) as output_file:

                shutil.copyfileobj(
                    response,
                    output_file
                )

        return True, (
            "Download completed successfully."
        )

    except Exception as error:

        return False, (
            f"Download failed: {error}"
        )


# Find Executable

def find_executable(
    directory,
    executable_name
):
    """
    Search recursively for an executable.
    """

    directory = Path(
        directory
    )

    for path in directory.rglob(
        executable_name
    ):

        if path.is_file():
            return str(path)

    return None


# Sourceforge Installation

def install_from_sourceforge(tool):
    """
    Install Ngspice from a SourceForge archive.
    """

    download_url = tool.get(
        "download_url"
    )

    if not download_url:
        return False, (
            "No download URL configured."
        )

    try:

        install_directory = Path(
            os.path.expandvars(
                r"%LOCALAPPDATA%"
                r"\eSimToolManager\ngspice"
            )
        )

        install_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        archive_path = (
            install_directory
            / "ngspice_package.7z"
        )

        print(
            f"Downloading {tool['name']}..."
        )

        success, message = download_file(
            download_url,
            str(archive_path)
        )

        if not success:
            return False, message

        print(
            "Extracting archive..."
        )

        with py7zr.SevenZipFile(
            str(archive_path),
            mode="r"
        ) as archive:

            archive.extractall(
                path=str(install_directory)
            )

        print(
            "Searching for executable..."
        )

        executable_name = (
            "ngspice.exe"
            if platform.system().lower()
            == "windows"
            else "ngspice"
        )

        executable_path = find_executable(
            install_directory,
            executable_name
        )

        if not executable_path:

            return False, (
                f"Could not find "
                f"{executable_name} "
                "inside the downloaded archive."
            )

        try:
            archive_path.unlink()
        except OSError:
            pass

        return True, executable_path

    except Exception as error:

        return False, (
            f"Installation failed: {error}"
        )


# Sourceforge Latest Version

def get_sourceforge_latest_version(tool):
    """
    Find the latest Ngspice version on SourceForge.
    """

    url = (
        "https://sourceforge.net/projects/"
        "ngspice/files/ng-spice-rework/"
    )

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "eSim-Automated-Tool-Manager/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            page = response.read().decode(
                "utf-8",
                errors="ignore"
            )

        archive_pattern = re.compile(
            r"ngspice-"
            r"(\d+(?:\.\d+)*)"
            r"_64\.7z",
            re.IGNORECASE
        )

        matches = archive_pattern.findall(
            page
        )

        if not matches:

            directory_pattern = re.compile(
                r"/ng-spice-rework/"
                r"(\d+(?:\.\d+)*)/",
                re.IGNORECASE
            )

            matches = directory_pattern.findall(
                page
            )

        if not matches:

            return False, None, (
                "Could not determine the latest "
                "Ngspice version from SourceForge."
            )

        matches = list(
            set(matches)
        )

        def version_key(version):

            return tuple(
                int(part)
                for part in version.split(".")
            )

        latest_version = max(
            matches,
            key=version_key
        )

        return True, latest_version, (
            "Latest SourceForge version detected."
        )

    except Exception as error:

        return False, None, (
            f"Failed to check SourceForge: "
            f"{error}"
        )


# Installed Ngspice Version

def get_installed_ngspice_version(tool):
    """
    Get the currently installed Ngspice version.
    """

    executable_path = tool.get(
        "executable_path"
    )

    if executable_path:

        executable_path = os.path.expandvars(
            executable_path
        )

        if not os.path.isfile(
            executable_path
        ):
            return None

    stored_version = tool.get(
        "installed_version"
    )

    if stored_version:
        return str(
            stored_version
        )

    return str(
        tool.get(
            "required_version",
            "0"
        )
    )


# Sourceforge Update

def update_from_sourceforge(tool):
    """
    Update Ngspice from SourceForge.

    Performs:
        Download
        Extraction
        Backup
        Installation
        SHA-256 verification
        File-size verification
        Version persistence
    """

    current_version = (
        get_installed_ngspice_version(
            tool
        )
    )

    if not current_version:

        return False, (
            "Could not determine the "
            "currently installed Ngspice version."
        )

    print(
        f"Current installed version: "
        f"{current_version}"
    )

    success, latest_version, message = (
        get_sourceforge_latest_version(
            tool
        )
    )

    if not success:
        return False, message

    print(
        f"Latest SourceForge version: "
        f"{latest_version}"
    )

    def version_tuple(version):

        return tuple(
            int(part)
            for part in str(version).split(".")
        )

    try:

        installed_tuple = version_tuple(
            current_version
        )

        latest_tuple = version_tuple(
            latest_version
        )

    except ValueError:

        return False, (
            "Unable to compare Ngspice versions."
        )

    if latest_tuple <= installed_tuple:

        return True, (
            f"{tool['name']} is already "
            "up to date."
        )

    print(
        f"New Ngspice version available: "
        f"{latest_version}"
    )

    download_url = (
        "https://sourceforge.net/projects/"
        "ngspice/files/ng-spice-rework/"
        f"{latest_version}/"
        f"ngspice-{latest_version}_64.7z/download"
    )

    temp_directory = Path(
        tempfile.mkdtemp(
            prefix="ngspice_update_"
        )
    )

    archive_path = (
        temp_directory
        / f"ngspice-{latest_version}_64.7z"
    )

    extract_directory = (
        temp_directory
        / "extracted"
    )

    install_directory = Path(
        os.path.expandvars(
            r"%LOCALAPPDATA%"
            r"\eSimToolManager\ngspice"
        )
    )

    old_spice64 = (
        install_directory
        / "Spice64"
    )

    backup_directory = (
        install_directory.parent
        / "ngspice_backup"
    )

    try:

        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        print(
            f"Downloading Ngspice "
            f"{latest_version}..."
        )

        success, message = download_file(
            download_url,
            str(archive_path)
        )

        if not success:
            return False, message

        if not archive_path.is_file():

            return False, (
                "Downloaded archive was not found."
            )

        archive_size = (
            archive_path.stat().st_size
        )

        print(
            f"Downloaded archive size: "
            f"{archive_size:,} bytes"
        )

        if archive_size <= 0:

            return False, (
                "Downloaded archive is empty."
            )

        # ----------------------------------------------------
        # EXTRACT
        # ----------------------------------------------------

        print(
            "Extracting new Ngspice archive..."
        )

        extract_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        with py7zr.SevenZipFile(
            str(archive_path),
            mode="r"
        ) as archive:

            archive.extractall(
                path=str(extract_directory)
            )

        # ----------------------------------------------------
        # FIND NEW EXECUTABLE
        # ----------------------------------------------------

        print(
            "Searching for new executable..."
        )

        new_executable = find_executable(
            extract_directory,
            "ngspice.exe"
        )

        if not new_executable:

            return False, (
                "Could not find ngspice.exe "
                "inside the new archive."
            )

        new_executable = Path(
            new_executable
        )

        print(
            "New executable found:"
        )

        print(
            new_executable
        )

        # ----------------------------------------------------
        # HASH NEW EXECUTABLE
        # ----------------------------------------------------

        print(
            "Calculating SHA-256 of new executable..."
        )

        new_hash = calculate_sha256(
            new_executable
        )

        new_size = (
            new_executable.stat().st_size
        )

        print(
            f"New executable size: "
            f"{new_size:,} bytes"
        )

        print(
            f"New executable SHA-256: "
            f"{new_hash}"
        )

        # ----------------------------------------------------
        # FIND SPICE64
        # ----------------------------------------------------

        new_spice64 = None

        for parent in new_executable.parents:

            if parent.name.lower() == "spice64":

                new_spice64 = parent
                break

        if new_spice64 is None:

            return False, (
                "Could not locate the Spice64 "
                "directory in the new archive."
            )

        print(
            "New Ngspice files found at:"
        )

        print(
            new_spice64
        )

        # ----------------------------------------------------
        # PREPARE INSTALL DIRECTORY
        # ----------------------------------------------------

        install_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------------------
        # REMOVE OLD BACKUP
        # ----------------------------------------------------

        if backup_directory.exists():

            shutil.rmtree(
                backup_directory
            )

        # ----------------------------------------------------
        # BACKUP EXISTING VERSION
        # ----------------------------------------------------

        if old_spice64.exists():

            print(
                "Backing up existing Ngspice..."
            )

            shutil.move(
                str(old_spice64),
                str(backup_directory)
            )

        # ----------------------------------------------------
        # INSTALL NEW VERSION
        # ----------------------------------------------------

        print(
            "Installing new Ngspice files..."
        )

        try:

            shutil.copytree(
                str(new_spice64),
                str(old_spice64)
            )

        except Exception as error:

            print(
                "Copy operation failed."
            )

            if old_spice64.exists():

                shutil.rmtree(
                    old_spice64
                )

            if backup_directory.exists():

                shutil.move(
                    str(backup_directory),
                    str(old_spice64)
                )

            return False, (
                f"Could not copy new Ngspice: "
                f"{error}"
            )

        # ----------------------------------------------------
        # LOCATE INSTALLED EXECUTABLE
        # ----------------------------------------------------

        installed_executable = (
            old_spice64
            / "bin"
            / "ngspice.exe"
        )

        if not installed_executable.is_file():

            print(
                "Verification failed: "
                "installed executable missing."
            )

            if old_spice64.exists():

                shutil.rmtree(
                    old_spice64
                )

            if backup_directory.exists():

                shutil.move(
                    str(backup_directory),
                    str(old_spice64)
                )

            return False, (
                "Ngspice update failed verification."
            )

        # ----------------------------------------------------
        # VERIFY INSTALLED EXECUTABLE
        # ----------------------------------------------------

        print(
            "Verifying installed executable..."
        )

        installed_hash = calculate_sha256(
            installed_executable
        )

        installed_size = (
            installed_executable.stat().st_size
        )

        print(
            f"Installed executable size: "
            f"{installed_size:,} bytes"
        )

        print(
            f"Installed executable SHA-256: "
            f"{installed_hash}"
        )

        # ----------------------------------------------------
        # HASH VERIFICATION
        # ----------------------------------------------------

        if new_hash != installed_hash:

            print(
                "SHA-256 verification FAILED."
            )

            if old_spice64.exists():

                shutil.rmtree(
                    old_spice64
                )

            if backup_directory.exists():

                shutil.move(
                    str(backup_directory),
                    str(old_spice64)
                )

            return False, (
                "Ngspice update failed: "
                "SHA-256 verification failed."
            )

        print(
            "SHA-256 verification passed."
        )

        # ----------------------------------------------------
        # FILE SIZE VERIFICATION
        # ----------------------------------------------------

        if new_size != installed_size:

            print(
                "File-size verification FAILED."
            )

            if old_spice64.exists():

                shutil.rmtree(
                    old_spice64
                )

            if backup_directory.exists():

                shutil.move(
                    str(backup_directory),
                    str(old_spice64)
                )

            return False, (
                "Ngspice update failed: "
                "installed executable size differs."
            )

        print(
            "File-size verification passed."
        )

        # ----------------------------------------------------
        # SAVE INSTALLED VERSION
        # ----------------------------------------------------

        version_saved = save_installed_version(
            "ngspice",
            latest_version
        )

        if version_saved:

            print(
                f"Installed version recorded as "
                f"{latest_version}."
            )

        else:

            print(
                "Warning: Could not save "
                "installed version to tools.json."
            )

        # ----------------------------------------------------
        # REMOVE BACKUP AFTER SUCCESS
        # ----------------------------------------------------

        if backup_directory.exists():

            shutil.rmtree(
                backup_directory
            )

        print(
            f"Ngspice {latest_version} "
            "installed successfully."
        )

        return True, (
            f"Ngspice updated successfully "
            f"to version {latest_version}."
        )

    except Exception as error:

        # ----------------------------------------------------
        # ROLLBACK
        # ----------------------------------------------------

        try:

            if old_spice64.exists():

                shutil.rmtree(
                    old_spice64
                )

            if backup_directory.exists():

                shutil.move(
                    str(backup_directory),
                    str(old_spice64)
                )

        except Exception:

            pass

        return False, (
            f"Ngspice update failed: "
            f"{error}"
        )

    finally:

        # ----------------------------------------------------
        # CLEAN TEMPORARY FILES
        # ----------------------------------------------------

        try:

            shutil.rmtree(
                temp_directory
            )

        except OSError:

            pass