# there are a few txt files which are 100mb or more, and generally contain only DNA. this allows you to sift through the largest file and decide quickly


import os
import constants
from pathlib import Path
import shutil

unzipped_folder = Path(constants.HOME, constants.UNZIPPED_FOLDER)
ebooks = os.listdir(unzipped_folder)

ebooks = sorted(ebooks, key=lambda x: -os.path.getsize(Path(unzipped_folder, x)))

for ebook in ebooks:
    choice = None
    ebook_fpath = Path(unzipped_folder, ebook)
    with open(ebook_fpath, "r", encoding="utf8") as f:
        size = os.path.getsize(Path(unzipped_folder, ebook))
        print(f"{ebook}: {size/(1024**2):.1f} MB")
        line_no = 0
        while choice != "Y" and choice != "n":
            line = f.readline()
            print(f"line {line_no}: {line}")
            line_no += 1
            choice = input("Remove?\n")
    if choice == "Y":
        os.remove(ebook_fpath)
        print(f"{ebook} removed")
    elif choice == "n":
        print(f"{ebook} kept")
