"""
General file and other interaction utilities.

Generally you want to import by importing the directory, utilities, and
accessing by utilities.function (instead of utilities.general_utils.function).
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import userpaths
import xlrd

import pandas as pd

import importlib.resources as pkg_resources
from . import config

PLATFORM = platform.system()

with pkg_resources.open_text(config, "nans.json") as nansfile:
    NANS = json.load(nansfile)
    MAIN_PATH = os.path.join(
        os.path.dirname(__file__),
        "../../../"
    )
with pkg_resources.open_text(config, "regions.json") as regions:
    REGIONS = json.load(regions)
with pkg_resources.path(config, "user-manual.pdf") as p:
    HELP_DOC = str(p)

_icon_to_use = {
    'Windows': "NI.ico",
    "Linux": "NI.xbm",
    "Darwin": "NI.icns"
}

with pkg_resources.path(config, _icon_to_use[PLATFORM]) as p:
    PROGRAM_ICON = None if PLATFORM == 'Windows' else "@" + str(p)

if PLATFORM == "Windows":
    with pkg_resources.open_text(config, "rloc.txt") as rloc:
        R_LOC = os.path.join(rloc.read().strip('\n'), "bin/Rscript.exe")
else:
    R_LOC = "Rscript"


USER_PATH = os.path.join(userpaths.get_my_documents(), "niclassify")


_required_folders = [
    os.path.join(USER_PATH),
    os.path.join(USER_PATH, "config"),
    os.path.join(USER_PATH, "output"),
    os.path.join(USER_PATH, "data"),
    os.path.join(USER_PATH, "output/classifiers"),
    os.path.join(USER_PATH, "logs"),
    os.path.join(USER_PATH, "logs/delim"),
    os.path.join(USER_PATH, "logs/delim/tree"),
    os.path.join(USER_PATH, "logs/delim/delim"),
    os.path.join(USER_PATH, "logs/ftgen"),
    os.path.join(MAIN_PATH, "data"),
    os.path.join(USER_PATH, "data/unprepared")
]

# make sure required folders exist and get/prepare user config
for i, f in enumerate(_required_folders):
    if not os.path.exists(f):
        os.makedirs(f)
        if i == 1:  # config folder
            # copy over config files for user config
            with open(os.path.join(f, "nans.json"), "w") as user_nans:
                json.dump(NANS, user_nans)
            with open(os.path.join(f, "regions.json"), "w") as user_regions:
                json.dump(REGIONS, user_regions)
    elif i == 1:  # user configs (may) already exist
        try:  # user nans exist, load
            with open(os.path.join(f, "nans.json")) as nansfile:
                NANS = json.load(nansfile)
        except(FileNotFoundError, KeyError):  # nans do not exist, copy
            with open(os.path.join(f, "nans.json"), "w") as user_nans:
                json.dump(NANS, user_nans)
        try:  # user regions exist, load
            with open(os.path.join(f, "regions.json")) as regions:
                REGIONS = json.load(regions)
        except (FileNotFoundError, KeyError):  # regions do not exist, copy
            with open(os.path.join(f, "regions.json"), "w") as user_regions:
                json.dump(REGIONS, user_regions)


class RNotFoundError(Exception):
    pass


class RScriptFailedError(Exception):
    pass


def clean_folder(path):
    """Delete contents of a folder.
    If supplied file, deletes the file.
    The folder is removed and replaced.

    Args:
        path (str): folder pathname.
    """
    path = os.path.realpath(path)
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path)
        os.mkdir(path)

def get_data(filename, excel_sheet=None):
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext in [".xlsx", ".xlsm", ".xlsb", ".xltx", ".xltm", ".xls", ".xlt", ".xml"]:
            # Excel file handling
            sheet = int(excel_sheet) - 1 if excel_sheet and excel_sheet.isdigit() else excel_sheet or 0

            raw_data = pd.read_excel(
                filename,
                sheet_name=sheet,
                na_values=NANS,
                keep_default_na=True,
            )

        elif ext in [".csv", ".tsv", ".txt"]:
            sep = "\t" if ext == ".tsv" else None

            try:
                raw_data = pd.read_csv(
                    filename,
                    sep=sep,
                    na_values=NANS,
                    keep_default_na=True,
                    encoding="utf-8",
                    engine="python" if sep is None else "c",
                )
            except UnicodeDecodeError:
                raw_data = pd.read_csv(
                    filename,
                    sep=sep,
                    na_values=NANS,
                    keep_default_na=True,
                    encoding="windows-1252",
                    engine="python" if sep is None else "c",
                )

            # Fallback for wrong separator
            if raw_data.shape[1] == 1 and sep != "\t":
                try:
                    raw_data = pd.read_csv(
                        filename,
                        sep="\t",
                        na_values=NANS,
                        keep_default_na=True,
                        encoding="utf-8",
                        engine="c",
                    )
                except UnicodeDecodeError:
                    raw_data = pd.read_csv(
                        filename,
                        sep="\t",
                        na_values=NANS,
                        keep_default_na=True,
                        encoding="windows-1252",
                        engine="c",
                    )

        else:
            raise TypeError("Unsupported file type or missing extension.")

        return raw_data

    except Exception as e:
        print(f"\n[ERROR] Failed to read file: {filename}")
        print(f"        Error: {e.__class__.__name__} — {str(e)}\n")
        raise RuntimeError("NIClassify: Could not read file. Try saving it from Excel manually.") from e



def keyboardInterruptHandler(signal, frame):
    """Handle keyboard interrupts.

    Likely to go unused, but good to have.
    """
    exit(0)


def view_open_file(filename):
    """
    Open a file or directory with system default.

    Args:
        filename (str): Path to file, should be absolute.
    """
    filename = os.path.realpath(filename)
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])
