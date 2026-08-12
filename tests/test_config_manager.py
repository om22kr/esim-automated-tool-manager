from pathlib import Path
import sys

sys.path.insert(
    0,
    str(Path(__file__).parent.parent / "src")
)

from config_manager import display_configuration


if __name__ == "__main__":
    display_configuration()