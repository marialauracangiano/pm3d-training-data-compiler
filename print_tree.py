from pathlib import Path


def print_tree(path: Path, prefix: str = ""):
    """Recursively prints a directory tree including hidden and compiled files."""
    if not path.exists():
        print(f"{path} does not exist")
        return

    # Include all files and directories, even hidden
    files = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    for i, f in enumerate(files):
        connector = "└── " if i == len(files) - 1 else "├── "
        print(prefix + connector + f.name)
        if f.is_dir():
            extension = "    " if i == len(files) - 1 else "│   "
            print_tree(f, prefix + extension)


# Set your project root here
project_root = Path(
    "/Users/mlcangia/Documents/PSA/PM3D/pm3d-b4i-copy/pm3d-b4i-data-compiler-new"
)
print_tree(project_root)
