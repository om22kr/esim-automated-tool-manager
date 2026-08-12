from pathlib import Path
import sys

sys.path.insert(
    0,
    str(Path(__file__).parent.parent / "src")
)

from installer import get_platform


def test_platform_detection():
    platform_name = get_platform()

    print(f"Detected platform: {platform_name}")

    assert platform_name in [
        "windows",
        "linux",
        "macos",
        "unknown"
    ]


if __name__ == "__main__":
    test_platform_detection()
    print("Platform detection test passed.")