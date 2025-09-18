import os  # TODO: remove unused import

def greet(name):
    print("Hello " + name)  # noqa: E999  # long line will trigger linter

if __name__ == "__main__":
    greet("World")
