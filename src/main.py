import json
import os
from pathlib import Path

from version_checker import check_tool_version, compare_versions
from installer import install_tool, update_tool

from dependency_checker import (
    display_dependencies,
    display_tool_dependencies
)

from config_manager import (
    display_configuration,
    configure_tool
)

from logger import log_info, log_error


def load_tools():
    """Load tool definitions from the configuration file."""

    config_path = (
        Path(__file__).parent.parent
        / "config"
        / "tools.json"
    )

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["tools"]


def get_tool_command(tool):
    """Return the configured executable path or default command."""

    if tool.get("executable_path"):
        return os.path.expandvars(
            tool["executable_path"]
        )

    return tool["command"]


def display_tools(tools):
    """Display installation and version status of all tools."""

    print("\n========== Tool Status ==========\n")

    for tool_id, tool in tools.items():

        command = get_tool_command(tool)

        result = check_tool_version(command)

        if result["installed"]:
            status = "Installed"

            if tool.get("required_version"):
                comparison = compare_versions(
                    result["version"],
                    tool["required_version"]
                )

                if comparison == "compatible":
                    status = "Compatible"

                elif comparison == "update_required":
                    status = "Update required"

                elif comparison == "newer":
                    status = "Newer version"

            print(
                f"{tool['name']:<12} "
                f"Version: {str(result['version'] or 'Unknown'):<10} "
                f"Status: {status}"
            )

        else:
            print(
                f"{tool['name']:<12} "
                f"Status: Not installed"
            )

    print()


def install_selected_tool(tools):
    """Allow the user to select and install a tool."""

    print("\n========== Install Tool ==========\n")

    tool_ids = list(tools.keys())

    for index, tool_id in enumerate(tool_ids, start=1):
        print(
            f"{index}. {tools[tool_id]['name']}"
        )

    print("0. Cancel")

    choice = input(
        "\nSelect a tool: "
    ).strip()

    if choice == "0":
        return

    try:
        choice_number = int(choice)

        if (
            choice_number < 1
            or choice_number > len(tool_ids)
        ):
            print("Invalid selection.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    selected_id = tool_ids[
        choice_number - 1
    ]

    selected_tool = tools[selected_id]

    command = get_tool_command(selected_tool)

    result = check_tool_version(command)

    if result["installed"]:
        print(
            f"\n{selected_tool['name']} is already installed "
            f"(version {result['version']})."
        )
        return

    print(
        f"\nInstalling {selected_tool['name']}..."
    )

    log_info(
        f"Installation requested for "
        f"{selected_tool['name']}"
    )

    success, message = install_tool(
        selected_tool
    )

    if success:
        print(f"[✓] {message}")

        log_info(
            f"{selected_tool['name']}: {message}"
        )

    else:
        print(f"[✗] {message}")

        log_error(
            f"{selected_tool['name']}: {message}"
        )


def update_selected_tool(tools):
    """Allow the user to select and update a tool."""

    print("\n========== Update Tool ==========\n")

    tool_ids = list(tools.keys())

    for index, tool_id in enumerate(tool_ids, start=1):
        print(
            f"{index}. {tools[tool_id]['name']}"
        )

    print("0. Cancel")

    choice = input(
        "\nSelect a tool: "
    ).strip()

    if choice == "0":
        return

    try:
        choice_number = int(choice)

        if (
            choice_number < 1
            or choice_number > len(tool_ids)
        ):
            print("Invalid selection.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    selected_id = tool_ids[
        choice_number - 1
    ]

    selected_tool = tools[selected_id]

    command = get_tool_command(selected_tool)

    result = check_tool_version(command)

    if not result["installed"]:
        print(
            f"\n{selected_tool['name']} is not installed. "
            "Install it first."
        )
        return

    print(
        f"\nCurrent version: {result['version']}"
    )

    print(
        f"Checking for updates to "
        f"{selected_tool['name']}..."
    )

    log_info(
        f"Update requested for "
        f"{selected_tool['name']}"
    )

    success, message = update_tool(
        selected_tool
    )

    if success:
        print(f"[✓] {message}")

        log_info(
            f"{selected_tool['name']}: {message}"
        )

    else:
        print(f"[✗] {message}")

        log_error(
            f"{selected_tool['name']}: {message}"
        )

    updated_command = get_tool_command(
        selected_tool
    )

    updated_result = check_tool_version(
        updated_command
    )

    if updated_result["installed"]:
        print(
            f"Current version: "
            f"{updated_result['version']}"
        )


def view_logs():
    """Display the application log file."""

    log_file = (
        Path(__file__).parent.parent
        / "logs"
        / "manager.log"
    )

    print("\n========== Logs ==========\n")

    if not log_file.exists():
        print("No log file found.")
        return

    try:
        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:
            content = file.read()

        if content.strip():
            print(content)
        else:
            print("Log file is empty.")

    except Exception as error:
        print(
            f"Unable to read log file: {error}"
        )


def show_menu():
    """Display the main menu."""

    print("\n========================================")
    print("       eSim Automated Tool Manager")
    print("========================================")

    print("\n1. List installed tools")
    print("2. Check tool versions")
    print("3. Install a tool")
    print("4. Update a tool")
    print("5. Check dependencies")
    print("6. Configure tools")
    print("7. View logs")
    print("8. Exit")


def main():
    """Run the main application."""

    tools = load_tools()

    while True:

        show_menu()

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            display_tools(tools)

        elif choice == "2":
            display_tools(tools)

        elif choice == "3":
            install_selected_tool(tools)

        elif choice == "4":
            update_selected_tool(tools)

        elif choice == "5":
            display_dependencies()
            display_tool_dependencies(tools)

        elif choice == "6":
            display_configuration()
            configure_tool()

        elif choice == "7":
            view_logs()

        elif choice == "8":
            print(
                "\nExiting eSim Automated Tool Manager."
            )
            break

        else:
            print(
                "\nInvalid choice. "
                "Please select 1-8."
            )


if __name__ == "__main__":
    main()