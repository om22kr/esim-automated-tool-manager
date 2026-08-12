import platform
import shutil
import subprocess

from version_checker import check_tool_version


# ============================================================
# CHECK COMMAND
# ============================================================

def check_command(command):
    """
    Check whether a command is available on the system.
    """

    return shutil.which(command) is not None


# ============================================================
# GET COMMAND VERSION
# ============================================================

def get_command_version(command, args=None):
    """
    Get the version information for a command.
    """

    if args is None:
        args = ["--version"]

    try:

        result = subprocess.run(
            [command] + args,
            capture_output=True,
            text=True,
            timeout=10
        )

        output = (
            result.stdout
            + result.stderr
        ).strip()

        if output:
            return output

        return None

    except (
        FileNotFoundError,
        subprocess.TimeoutExpired,
        OSError
    ):
        return None

    except Exception:
        return None


# ============================================================
# PYTHON VERSION
# ============================================================

def get_python_version():
    """
    Get the installed Python version.
    """

    # Try the same Python executable running
    # the tool manager first.

    try:

        result = subprocess.run(
            [
                "python",
                "--version"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = (
            result.stdout
            + result.stderr
        ).strip()

        if output:
            return output

    except Exception:
        pass

    # Fallback to the Python executable
    # currently running this program.

    try:

        import sys

        result = subprocess.run(
            [
                sys.executable,
                "--version"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = (
            result.stdout
            + result.stderr
        ).strip()

        if output:
            return output

    except Exception:
        pass

    return None


# ============================================================
# GIT VERSION
# ============================================================

def get_git_version():
    """
    Get the installed Git version.
    """

    return get_command_version(
        "git"
    )


# ============================================================
# WINGET VERSION
# ============================================================

def get_winget_version():
    """
    Get the installed Windows Package Manager version.
    """

    return get_command_version(
        "winget"
    )


# ============================================================
# SYSTEM DEPENDENCIES
# ============================================================

def check_system_dependencies():
    """
    Check basic dependencies required by
    the eSim Automated Tool Manager.
    """

    dependencies = {}

    # --------------------------------------------------------
    # PYTHON
    # --------------------------------------------------------

    python_version = get_python_version()

    dependencies["Python"] = {
        "available":
            python_version is not None,
        "version":
            python_version
    }

    # --------------------------------------------------------
    # GIT
    # --------------------------------------------------------

    git_available = check_command(
        "git"
    )

    dependencies["Git"] = {
        "available":
            git_available,
        "version":
            get_git_version()
            if git_available
            else None
    }

    # --------------------------------------------------------
    # WINGET
    # --------------------------------------------------------

    if platform.system().lower() == "windows":

        winget_available = check_command(
            "winget"
        )

        dependencies["Winget"] = {
            "available":
                winget_available,
            "version":
                get_winget_version()
                if winget_available
                else None
        }

    return dependencies


# ============================================================
# DISPLAY SYSTEM DEPENDENCIES
# ============================================================

def display_dependencies():
    """
    Display dependency check results.
    """

    print(
        "\n========== Dependency Check ==========\n"
    )

    dependencies = (
        check_system_dependencies()
    )

    for name, info in dependencies.items():

        if info["available"]:

            version = info.get(
                "version"
            )

            if version:

                # Only display the first useful
                # version line.

                version_line = (
                    version.splitlines()[0]
                )

                print(
                    f"{name:<12} "
                    f"[OK] Available - "
                    f"{version_line}"
                )

            else:

                print(
                    f"{name:<12} "
                    f"[OK] Available"
                )

        else:

            print(
                f"{name:<12} "
                f"[X] Missing"
            )

    print()


# ============================================================
# CHECK TOOL DEPENDENCIES
# ============================================================

def check_tool_dependencies(tools):
    """
    Check whether all configured external
    tools are available.
    """

    results = {}

    for tool_id, tool in tools.items():

        result = check_tool_version(
            tool["command"],
            tool.get("executable_path")
        )

        results[tool["name"]] = {
            "available":
                result["installed"],
            "version":
                result.get("version"),
            "message":
                result.get("message")
        }

    return results


# ============================================================
# DISPLAY TOOL DEPENDENCIES
# ============================================================

def display_tool_dependencies(tools):
    """
    Display availability and version information
    for configured external tools.
    """

    print(
        "\n========== Tool Dependencies ==========\n"
    )

    results = check_tool_dependencies(
        tools
    )

    for tool_name, info in results.items():

        if info["available"]:

            version = info.get(
                "version"
            )

            if version:

                print(
                    f"{tool_name:<12} "
                    f"[OK] Available - "
                    f"Version {version}"
                )

            else:

                print(
                    f"{tool_name:<12} "
                    f"[OK] Available"
                )

        else:

            print(
                f"{tool_name:<12} "
                f"[X] Missing"
            )

    print()