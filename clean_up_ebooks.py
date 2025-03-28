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
from utils import load_manifest, get_ebooks_library
import json


def encoding(fn):
    for line in open(fn):
        if line.startswith("Character set encoding:"):
            _, encoding = line.split(":")
            return encoding.strip()
    return "latin1"


def title_to_filename(title: str) -> str:
    if title == "":
        title = constants.UNKNOWN_TITLE
    title = title[:100].lower()
    title = re.sub(r"\W+", "_", title)
    return title + ".txt"


def split_title(title: str) -> str:
    title_list = title.split(", by ")
    if len(title_list) > 1:
        return title_list[0], title_list[1]
    else:
        return title_list[0], constants.UNKNOWN_AUTHOR


def dump_book_info(catalog_title: str, filename: str, bookno: int) -> str:
    title, author = split_title(catalog_title)
    return json.dumps(
        {"title": title, "author": author, "filename": filename, "bookno": bookno},
        ensure_ascii=False,
    )


def beautify(fpath: str, catalog_title: str, outputdir: str):
    """Reads a raw Project Gutenberg etext, reformat paragraphs,
    and removes fluff.
    Use the title from the manifest.
    Converts everything to utf8
    """
    lines = [str(from_bytes(line.strip()).best()) for line in io.open(fpath, "rb")]
    collect = False
    outlines = []
    startseen = endseen = False
    for line in lines:
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

    filename = Path(fpath).name
    bookno = bookno_from_filename(filename)

    # so that you can readline() and json.loads() all the info you need in minimal time
    outlines = [dump_book_info(catalog_title, filename, bookno)] + outlines

    title_filename = title_to_filename(catalog_title)

    if not startseen:
        print("No '*** START' seen")
    if not endseen:
        print("No '*** END' seen")

    f = io.open(Path(constants.HOME, outputdir, title_filename), "w+", encoding="utf8")
    f.write("\n".join(outlines))
    f.close()


def check_dirs():
    if not os.path.exists("ebooks"):
        os.mkdir("ebooks")


def bookno_from_filename(fn: str) -> str:
    stem = Path(fn).stem
    stem = re.sub(r"-[08]", "", stem)
    return stem


def title_lang_from_manifest(
    bookno: str, ebooks: dict, ebookslanguage: dict
) -> tuple[str, str]:
    return ebooks.get(bookno, constants.UNKNOWN_TITLE), ebookslanguage.get(
        bookno, constants.UNKNOWN_LANGUAGE
    )


def process_unzipped_ebooks(dirname: str, accept_unknown_language: bool):
    check_dirs()
    ebooks, ebookslanguage, _, _ = load_manifest()
    library = get_ebooks_library()
    for fn in glob.glob(f"{dirname}/*.txt"):
        bookno = bookno_from_filename(fn)
        title, lang = title_lang_from_manifest(bookno, ebooks, ebookslanguage)
        print(bookno, title, lang)
        if bookno not in library.keys() and (
            lang == constants.LANGUAGE or accept_unknown_language
        ):
            beautify(fn, title, constants.EBOOKS_FOLDER)
        else:
            print("Not processing book")


if __name__ == "__main__":
    process_unzipped_ebooks("ebooks-unzipped", True)
