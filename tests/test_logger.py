from pathlib import Path
import sys

sys.path.insert(
    0,
    str(Path(__file__).parent.parent / "src")
)

from logger import log_info, log_error


if __name__ == "__main__":

    log_info("Logger test started.")
    log_info("Testing information logging.")
    log_error("Testing error logging.")

    print("Logger test completed.")

    log_file = (
        Path(__file__).parent.parent
        / "logs"
        / "manager.log"
    )

    print(f"Log file: {log_file}")