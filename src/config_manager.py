import json
import os
import shutil
from pathlib import Path


# ============================================================
# CONFIGURATION PATH
# ============================================================

def get_config_path():
    """Return the path to the tools configuration file."""

    return (
        Path(__file__).parent.parent
        / "config"
        / "tools.json"
    )


# ============================================================
# LOAD CONFIGURATION
# ============================================================

def load_configuration():
    """Load the tool configuration."""

    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: "
            f"{config_path}"
        )

    try:

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:

            configuration = json.load(file)

    except json.JSONDecodeError as error:

        raise ValueError(
            "tools.json contains invalid JSON."
        ) from error

    if "tools" not in configuration:
        raise ValueError(
            "Invalid configuration: "
            "'tools' section is missing."
        )

    return configuration


# ============================================================
# SAVE CONFIGURATION
# ============================================================

def save_configuration(configuration):
    """Save the tool configuration safely."""

    config_path = get_config_path()

    # Create a backup before changing the configuration.
    backup_path = config_path.with_suffix(
        ".json.bak"
    )

    try:

        if config_path.exists():

            with open(
                config_path,
                "r",
                encoding="utf-8"
            ) as source:

                backup_data = source.read()

            with open(
                backup_path,
                "w",
                encoding="utf-8"
            ) as backup:

                backup.write(
                    backup_data
                )

        # Write the new configuration.
        with open(
            config_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                configuration,
                file,
                indent=4
            )

            file.write("\n")

        return True, (
            "Configuration saved successfully."
        )

    except Exception as error:

        return False, (
            f"Failed to save configuration: "
            f"{error}"
        )


# ============================================================
# DISPLAY CONFIGURATION
# ============================================================

def display_configuration():
    """Display the current tool configuration."""

    try:

        configuration = (
            load_configuration()
        )

    except Exception as error:

        print(
            "\n[ERROR] "
            f"{error}\n"
        )

        return

    print(
        "\n========== Tool Configuration ==========\n"
    )

    for tool_id, tool in (
        configuration["tools"].items()
    ):

        print(
            f"Tool: {tool.get('name', tool_id)}"
        )

        print(
            f"  Command: "
            f"{tool.get('command', 'Not specified')}"
        )

        executable_path = tool.get(
            "executable_path"
        )

        if executable_path:

            expanded_path = (
                os.path.expandvars(
                    executable_path
                )
            )

            print(
                f"  Configured path: "
                f"{executable_path}"
            )

            print(
                f"  Expanded path: "
                f"{expanded_path}"
            )

            if os.path.isfile(
                expanded_path
            ):

                print(
                    "  Path status: "
                    "[OK] Valid"
                )

            else:

                print(
                    "  Path status: "
                    "[X] Not found"
                )

        else:

            print(
                "  Configured path: "
                "Not specified"
            )

            # Try to find the command on PATH.
            command = tool.get(
                "command"
            )

            if command:

                command_path = (
                    shutil.which(command)
                    if "shutil" in globals()
                    else None
                )

                if command_path:

                    print(
                        f"  PATH executable: "
                        f"{command_path}"
                    )

        print()


# ============================================================
# UPDATE TOOL PATH
# ============================================================

def update_tool_path(
    tool_id,
    new_path
):
    """
    Update the executable path for a tool.
    """

    try:

        configuration = (
            load_configuration()
        )

    except Exception as error:

        return False, str(error)

    if tool_id not in configuration["tools"]:

        return False, (
            "Tool not found."
        )

    # Expand environment variables.
    expanded_path = os.path.expandvars(
        new_path
    )

    # Remove surrounding quotes if the user
    # pasted a quoted Windows path.
    expanded_path = (
        expanded_path
        .strip('"')
        .strip("'")
    )

    if not os.path.isfile(
        expanded_path
    ):

        return False, (
            "The specified executable "
            "does not exist."
        )

    configuration["tools"][tool_id][
        "executable_path"
    ] = new_path

    success, message = (
        save_configuration(
            configuration
        )
    )

    if not success:
        return False, message

    return True, (
        "Tool path updated successfully."
    )


# ============================================================
# CONFIGURE TOOL
# ============================================================

def configure_tool():
    """Interactively configure a tool executable path."""

    try:

        configuration = (
            load_configuration()
        )

    except Exception as error:

        print(
            f"\n[ERROR] {error}"
        )

        return

    tools = configuration[
        "tools"
    ]

    print(
        "\n========== Configure Tool ==========\n"
    )

    tool_ids = list(
        tools.keys()
    )

    for index, tool_id in enumerate(
        tool_ids,
        start=1
    ):

        print(
            f"{index}. "
            f"{tools[tool_id].get('name', tool_id)}"
        )

    print("0. Cancel")

    choice = input(
        "\nSelect a tool: "
    ).strip()

    if choice == "0":

        print(
            "Configuration cancelled."
        )

        return

    try:

        choice_number = int(
            choice
        )

    except ValueError:

        print(
            "Please enter a valid number."
        )

        return

    if (
        choice_number < 1
        or choice_number > len(tool_ids)
    ):

        print(
            "Invalid selection."
        )

        return

    selected_id = (
        tool_ids[
            choice_number - 1
        ]
    )

    selected_tool = (
        tools[selected_id]
    )

    print(
        f"\nSelected tool: "
        f"{selected_tool.get('name', selected_id)}"
    )

    current_path = selected_tool.get(
        "executable_path"
    )

    if current_path:

        print(
            f"Current path: "
            f"{current_path}"
        )

        expanded_current_path = (
            os.path.expandvars(
                current_path
            )
        )

        if os.path.isfile(
            expanded_current_path
        ):

            print(
                "Current path status: "
                "[OK] Valid"
            )

        else:

            print(
                "Current path status: "
                "[X] Not found"
            )

    else:

        print(
            "Current path: "
            "Not configured"
        )

    print(
        "\nEnter the full path to the "
        "executable."
    )

    print(
        "Press Enter to cancel."
    )

    new_path = input(
        "\nNew path: "
    ).strip()

    if not new_path:

        print(
            "Configuration cancelled."
        )

        return

    # Remove quotes if the user pasted:
    # "C:\Program Files\..."
    new_path = (
        new_path
        .strip('"')
        .strip("'")
    )

    expanded_path = (
        os.path.expandvars(
            new_path
        )
    )

    if not os.path.isfile(
        expanded_path
    ):

        print(
            "\n[X] Invalid path."
        )

        print(
            f"File not found:\n"
            f"{expanded_path}"
        )

        return

    success, message = (
        update_tool_path(
            selected_id,
            new_path
        )
    )

    if success:

        print(
            f"\n[OK] {message}"
        )

        print(
            f"Saved path: "
            f"{new_path}"
        )

    else:

        print(
            f"\n[X] {message}"
        )