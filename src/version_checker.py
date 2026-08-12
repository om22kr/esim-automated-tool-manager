import os
import subprocess
import re
import json
from pathlib import Path


# ============================================================
# RESOLVE COMMAND
# ============================================================

def resolve_command(command, executable_path=None):
    """
    Resolve the executable path for a tool.
    """

    if executable_path:
        path = os.path.expandvars(executable_path)

        if os.path.isfile(path):
            return path

    return command


# ============================================================
# GET CONFIGURATION FILE
# ============================================================

def get_config_path():
    """
    Return the path to tools.json.
    """

    return (
        Path(__file__).parent.parent
        / "config"
        / "tools.json"
    )


# ============================================================
# LOAD CONFIGURATION
# ============================================================

def load_configuration():
    """
    Load tools.json.
    """

    config_path = get_config_path()

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# SAVE CONFIGURATION
# ============================================================

def save_configuration(data):
    """
    Save configuration to tools.json.
    """

    config_path = get_config_path()

    with open(
        config_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4
        )

        file.write("\n")


# ============================================================
# GET STORED TOOL VERSION
# ============================================================

def get_stored_version(command):
    """
    Read installed_version from tools.json.
    """

    try:
        data = load_configuration()

        tools = data.get(
            "tools",
            {}
        )

        for tool in tools.values():

            if tool.get("command") == command:
                return tool.get(
                    "installed_version"
                )

        return None

    except Exception:
        return None


# ============================================================
# SAVE INSTALLED TOOL VERSION
# ============================================================

def save_installed_version(command, version):
    """
    Save the installed version of a tool
    to tools.json.

    Returns True if successful.
    """

    try:
        data = load_configuration()

        tools = data.get(
            "tools",
            {}
        )

        for tool in tools.values():

            if tool.get("command") == command:

                tool["installed_version"] = str(
                    version
                )

                save_configuration(data)

                return True

        return False

    except Exception:
        return False


# ============================================================
# CHECK TOOL VERSION
# ============================================================

def check_tool_version(
    command,
    executable_path=None
):
    """
    Check whether a tool is installed
    and retrieve its version.

    Git and KiCad:
        Version is obtained using --version.

    Ngspice:
        Version is obtained from tools.json because
        the Windows Ngspice executable does not
        reliably return version information through
        --version.
    """

    executable = resolve_command(
        command,
        executable_path
    )

    try:

        # ----------------------------------------------------
        # CHECK CONFIGURED EXECUTABLE
        # ----------------------------------------------------

        if executable_path:

            resolved_path = os.path.expandvars(
                executable_path
            )

            if not os.path.isfile(
                resolved_path
            ):
                return {
                    "installed": False,
                    "version": None,
                    "message": (
                        "Configured executable not found"
                    )
                }

            executable = resolved_path

        # ----------------------------------------------------
        # NGSPICE
        # ----------------------------------------------------

        if (
            command.lower() == "ngspice"
            or "ngspice" in executable.lower()
        ):

            if not os.path.isfile(
                executable
            ):
                return {
                    "installed": False,
                    "version": None,
                    "message": (
                        "Ngspice executable not found"
                    )
                }

            stored_version = get_stored_version(
                "ngspice"
            )

            if stored_version is not None:

                return {
                    "installed": True,
                    "version": str(
                        stored_version
                    ),
                    "message": (
                        "Ngspice executable detected "
                        "successfully."
                    )
                }

            return {
                "installed": True,
                "version": None,
                "message": (
                    "Ngspice executable detected, "
                    "but version is unknown."
                )
            }

        # ----------------------------------------------------
        # NORMAL VERSION CHECK
        # ----------------------------------------------------

        result = subprocess.run(
            [
                executable,
                "--version"
            ],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt"
                else 0
            )
        )

        output = (
            result.stdout
            + result.stderr
        ).strip()

        if output:

            match = re.search(
                r"\d+(?:\.\d+)+",
                output
            )

            if match:

                return {
                    "installed": True,
                    "version": match.group(0),
                    "message": output
                }

        return {
            "installed": False,
            "version": None,
            "message": (
                "No version information returned"
            )
        }

    # --------------------------------------------------------
    # FILE NOT FOUND
    # --------------------------------------------------------

    except FileNotFoundError:

        return {
            "installed": False,
            "version": None,
            "message": (
                "Tool is not installed or not available"
            )
        }

    # --------------------------------------------------------
    # TIMEOUT
    # --------------------------------------------------------

    except subprocess.TimeoutExpired:

        return {
            "installed": False,
            "version": None,
            "message": "Command timed out"
        }

    # --------------------------------------------------------
    # OTHER ERROR
    # --------------------------------------------------------

    except Exception as error:

        return {
            "installed": False,
            "version": None,
            "message": str(error)
        }


# ============================================================
# COMPARE VERSIONS
# ============================================================

def compare_versions(
    installed_version,
    required_version
):
    """
    Compare installed and required software versions.

    Supports:
        Standard versions:
            2.54.0

        Debian/Ubuntu versions:
            1:2.53.0-1ubuntu1

        Returns:
            compatible
            update_required
            newer
            unknown
    """

    if (
        not installed_version
        or not required_version
    ):
        return "unknown"

    def normalize_version(version):
        """
        Normalize common package-manager version
        formats into a comparable numeric tuple.
        """

        version = str(version).strip()

        if not version:
            return None

        # ----------------------------------------------------
        # Remove Debian epoch
        #
        # Example:
        # 1:2.53.0-1ubuntu1
        # becomes:
        # 2.53.0-1ubuntu1
        # ----------------------------------------------------

        if ":" in version:
            version = version.split(
                ":",
                1
            )[1]

        # ----------------------------------------------------
        # Extract the main numeric version.
        #
        # Examples:
        # 2.54.0
        # 2.53.0-1ubuntu1
        # 10.0.5
        # ----------------------------------------------------

        match = re.search(
            r"\d+(?:\.\d+)+",
            version
        )

        if not match:

            # Handle a simple integer version.
            match = re.search(
                r"\d+",
                version
            )

            if not match:
                return None

        numeric_version = match.group(0)

        try:

            return tuple(
                int(part)
                for part
                in numeric_version.split(".")
            )

        except ValueError:

            return None

    installed = normalize_version(
        installed_version
    )

    required = normalize_version(
        required_version
    )

    if (
        installed is None
        or required is None
    ):
        return "unknown"

    # --------------------------------------------------------
    # Normalize tuple lengths
    # --------------------------------------------------------

    max_length = max(
        len(installed),
        len(required)
    )

    installed += (
        0,
    ) * (
        max_length
        - len(installed)
    )

    required += (
        0,
    ) * (
        max_length
        - len(required)
    )

    # --------------------------------------------------------
    # Compare
    # --------------------------------------------------------

    if installed == required:

        return "compatible"

    if installed < required:

        return "update_required"

    return "newer"