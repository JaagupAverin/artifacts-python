import sys


def hello() -> str:
    return "Hello from artifacts-python!"


if __name__ == "__main__":
    print(hello())  # noqa: T201
    sys.exit(0)
