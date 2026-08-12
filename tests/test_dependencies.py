from pathlib import Path
import sys

sys.path.insert(
    0,
    str(Path(__file__).parent.parent / "src")
)

from dependency_checker import check_system_dependencies


def test_dependencies():

    dependencies = check_system_dependencies()

    print("\nDependency test results:")

    for name, info in dependencies.items():
        print(
            f"{name}: "
            f"{'Available' if info['available'] else 'Missing'}"
        )


if __name__ == "__main__":
    test_dependencies()