"""Interactive script for compiling tex files.

Especially useful for larger documents with nested output directories.
Here, latexmk will fail as it will not make all subdirectories.

Usage:
    python build.py

From there, you can navigate through the options.
"""

import shutil
import subprocess
from pathlib import Path

# ######################################################
# Configure these environmental variables and paths
BASE_DIR = Path(__file__).parent.resolve()  # project root
SRC = BASE_DIR / "src"  # tex source files
# the following tex files (in SRC) can be processed
FILES = [
    "main",
    # ...
]
TEMP = BASE_DIR / ".temp"  # temp files dir
OUT = BASE_DIR / "out"  # output files dir
PREFIX = ""  # prefix for the output files
# ######################################################

# the following compiling routines can be selected interactively
ROUTINES = [
    "clean",  # clean up the temp files
    "compile",  # compile a single tex file
    "watch",  # watch a tex file for changes
    "compile_all",  # compile all tex files
]
# Add numbers to files and routines for easy navigation
FILES_DICT = {i: f for i, f in zip(range(1, len(FILES) + 1), FILES)}
ROUTINES_DICT = {i: f for i, f in zip(range(1, len(ROUTINES) + 1), ROUTINES)}


def main() -> None:
    selector = ", ".join([f"{i} - {f}" for i, f in ROUTINES_DICT.items()])
    routine_id = input(f"Run routine ({selector}): ")
    try:
        globals()[ROUTINES_DICT[int(routine_id)]]()
    except KeyError:
        print("Unexpected index. Stopping...")


def clean() -> None:
    """Clean all temporary tex and bibtex files."""
    print("Cleaning temp files...")
    biber_cache = subprocess.getoutput("biber --cache")
    shutil.rmtree(biber_cache, ignore_errors=True)
    shutil.rmtree(TEMP, ignore_errors=True)


def _init_temp_dir(file: str) -> str:
    """Initialise the temp output directory with the src structure."""
    temp_dir = f"{TEMP}/{file}"
    subprocess.run(
        f"rsync -a {SRC}/ {temp_dir} --include \\*/ --exclude \\*",
        shell=True,
    )
    return temp_dir


def _user_file_selector() -> str:
    """Prompt the user for a tex file to use."""
    selector = ", ".join([f"{i} - {f}" for i, f in FILES_DICT.items()])
    file_id = input(f"File to watch/compile ({selector}): ")
    file = f"{FILES_DICT[int(file_id)]}"
    return file


def _compile(temp_dir: str, file: str) -> None:
    """Compile a tex file using latexmk."""
    subprocess.run(
        f"latexmk -cd -output-directory={temp_dir} {SRC}/{file}.tex",
        shell=True,
    )
    shutil.copyfile(f"{temp_dir}/{file}.pdf", f"{OUT}/{PREFIX}_{file}.pdf")


def watch() -> None:
    """Compile a tex file and preview changes continuously in pdf-viewer."""
    file = _user_file_selector()
    temp_dir = _init_temp_dir(file)
    subprocess.run(
        f"latexmk -cd -pvc -output-directory={temp_dir} {SRC}/{file}.tex",
        shell=True,
    )


def compile() -> None:
    """Compile a tex file and save to /out."""
    file = _user_file_selector()
    temp_dir = _init_temp_dir(file)
    _compile(temp_dir, file)


def compile_all() -> None:
    """Compile all tex files and save to /out."""
    for file in FILES:
        temp_dir = _init_temp_dir(file)
        _compile(temp_dir, file)


if __name__ == "__main__":
    main()
