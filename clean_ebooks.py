# gutenberg.py
#
# Reformats and renames the downloaded etexts.
#
# Software by Michiel Overtoom, motoom@xs4all.nl, July 2009, amended April 2016.
#


# Updated in March 2025 by Lucas Marti

import os
import io
import glob
import re
import constants
from pathlib import Path
from charset_normalizer import from_bytes


def encoding(fn):
    for line in open(fn):
        if line.startswith("Character set encoding:"):
            _, encoding = line.split(":")
            return encoding.strip()
    return "latin1"


def prepare_title(title: str, fn: str) -> str:
    if title == "":
        title = constants.UNKNOWN_TITLE
    title = title[:100]
    title = re.sub(r"\W", "_", title)
    return f"{title}_{fn}"


def beautify(fpath: str, outputdir: str):
    """Reads a raw Project Gutenberg etext, reformat paragraphs,
    and removes fluff.  Determines the title of the book and uses it
    as a filename to write the resulting output text."""
    print(fpath)
    lines = [str(from_bytes(line.strip()).best()) for line in io.open(fpath, "rb")]
    collect = False
    lookforsubtitle = False
    outlines = []
    startseen = endseen = False
    title = ""
    for line in lines:
        if line.startswith("Title: "):
            title = line[7:]
            lookforsubtitle = True
            continue
        if lookforsubtitle:
            if not line.strip():
                lookforsubtitle = False
            else:
                subtitle = line.strip()
                subtitle = subtitle.strip(".")
                title += ", " + subtitle
        if (
            ("*** START" in line)
            or ("***START" in line)
            or (line.startswith("*END THE SMALL PRINT!"))
        ):
            collect = startseen = True
            paragraph = ""
            continue
        if ("*** END" in line) or ("***END" in line):
            endseen = True
            break
        if not collect:
            continue
        if not line:
            paragraph = paragraph.strip()
            for term in constants.REMOVE:
                if paragraph.startswith(term):
                    paragraph = ""
            if paragraph:
                outlines.append(paragraph)
                outlines.append("")
            paragraph = ""
        else:
            paragraph += " " + line

    # Compose a filename.  Replace some illegal file name characters with alternatives.

    filename = Path(fpath).name
    title_filename = prepare_title(title, filename)

    # Report on anomalous situations, but don't make it a showstopper.
    if not title:
        print(filename)
        print("    Problem: No title found")
    if not startseen:
        print(filename)
        print("    Problem: No '*** START' seen")
    if not endseen:
        print(filename)
        print("    Problem: No '*** END' seen")

    f = io.open(Path(constants.HOME, outputdir, title_filename), "w+", encoding="utf8")
    f.write("\n".join(outlines))
    f.close()


def check_dirs():
    if not os.path.exists("ebooks"):
        os.mkdir("ebooks")


def process_txt_ebooks():
    check_dirs()
    for fn in glob.glob("ebooks-test/*.txt"):
        beautify(fn, constants.EBOOKS_FOLDER)


if __name__ == "__main__":
    process_txt_ebooks()
