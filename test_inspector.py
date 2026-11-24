
from file_inspector import inspect_file

print(
    "Safe file:",
    inspect_file("tests/safe.txt")
)

print(
    "Sensitive file:",
    inspect_file("tests/sensitive.txt")
)

print(
    "Missing file:",
    inspect_file("tests/missing.txt")
)
