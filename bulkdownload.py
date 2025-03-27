# bulkdownload.py
#
# Downloads all eBooks from a mirror of Project Gutenberg's website, for a specific language.
#
# Software by Michiel Overtoom, motoom@xs4all.nl, July 2009, March 2012. Adapted in 2016 for mirrors.


# Updated in March 2025 by Lucas Marti

"""
Scraping eBooks from Gutenbergs web site isn't allowed anymore.
Instead, you look in http://www.gutenberg.org/MIRRORS.ALL for a mirror nearby you.
You might want to choose a HTTP mirror because FTP mirrors are slow with urllib.urlretrieve (but FTP mirrors are OK if you can use wget).
Choose a suitable mirror URL and put it in the MIRROR variable below.

The program then fetches {MIRROR}/GUTINDEX.ZIP, which is the compressed book index.
In this zip is a textfile called GUTINDEX.ALL, in it every eBook is listed starting on the beginning
of a line, followed by lines of attributes:

    Zur Psychopathologie des Alltagslebens, by Sigmund Freud                 24429
      [Subtitle: Uber Vergessen, Versprechen, Vergreifen, Aberglaube und Irrtum]
      [Language: German]
    Hempfield, by David Grayson                                              33251
     [Subtitle: A Novel]
     [Illustrator: Thomas Fogarty]
    De slavernij in Suriname, by Julien Wolbers                              31060
     [Subtitle: of dezelfde gruwelen der slavernij, die in de 'Negerhut'
      geschetst zijn, bestaan ook in onze West-Indische Kolonien]
     [Language: Dutch]
    De schipbreuk van de "Berlin" 21 Februari 1907, by Jean Louis Pisuisse   33254
     [Subtitle: Volledig verhaal van de scheepsramp
      aan den Hoek van Holland]
     [Illustrator: Louis Raemaekers]
     [Language: Dutch]

The first line has a title and an eBook id number ("De slavernij in Suriname, by J.W.  31060").
Now, where to find the eBook text 31060?
For that, the program fetches {MIRROR}/ls-lR.gz, which contains the compressed directory & file index
in a textfile called 'ls-lR'. It contains chunks like:

    ./3/1/0/6/31060:
    total 156
    -rw-rw-r-- 1 gbnewby pg 77617 Jan 24  2010 31060-8.txt
    -rw-rw-r-- 1 gbnewby pg 29926 Jan 24  2010 31060-8.zip
    drwxrwxr-x 3 gbnewby pg  4096 Jan 24  2010 31060-h
    -rw-rw-r-- 1 gbnewby pg 35794 Jan 24  2010 31060-h.zip

We're interested in the file '31060-0.zip', '31060-8.zip' or '31060.zip'.
From the chunk above we learn it can be found in the directory /3/1/0/6/31060, thus:

    {MIRROR}/3/1/0/6/31060/31060-8.zip

This file is downloaded in the directory 'ebooks-zipped', and contains the eBook text '31060-8.txt',
which is eventually extracted into 'ebooks-unzipped'. Other programs take it from there.

"""


import urllib.request
import urllib.error
import re
import os
import zipfile
import gzip
import datetime
import codecs
import glob
import shutil
from pathlib import Path
import json
import io
import constants


def zip_to_txt(s: str, append: str = "") -> str:
    if isinstance(s, Path):
        return s.parent.as_posix() + "/" + s.stem + ".txt"
    return s.strip(".zip") + ".txt"


def make_alt(s: str, alt: str, extension: str = ".txt"):
    s: Path = Path(s)
    s = s.parent.as_posix() + "/" + s.stem
    s = re.sub(r"-[80]", "", s)
    s = re.sub(r"http:/+", "http://", s)
    return s + alt + extension


def file_exists_in_some_form(fn: str):
    for folder in (constants.ZIPPED_FOLDER, constants.UNZIPPED_FOLDER):
        for extension in (".zip", ".txt"):
            for alt in constants.ALT:
                if Path(
                    make_alt(Path(constants.HOME, folder, fn), alt, extension)
                ).is_file():
                    return True

    return False


def older(a, b):
    """Return True is file 'a' is older than file 'b'."""
    if not os.path.exists(a) or not os.path.exists(b):
        return False
    sta = os.stat(a)
    stb = os.stat(b)
    return sta <= stb


def fetch(mirrorurl, filename, outputfilename):
    """Fetch a file from a gutenberg mirror, if it hasn't been fetched earlier today."""
    mustdownload = False
    if os.path.exists(outputfilename):
        st = os.stat(outputfilename)
        modified = datetime.date.fromtimestamp(st.st_mtime)
        today = datetime.date.today()
        if modified == today:
            print(
                "%s exists, and is up-to-date. No need to download it." % outputfilename
            )
        else:
            print("%d exists, but is out of date. Downloading..." % outputfilename)
            mustdownload = True
    else:
        print("%s not found, downloading..." % outputfilename)
        mustdownload = True

    if mustdownload:
        url = mirrorurl + filename
        try:
            urllib.request.urlretrieve(url, outputfilename)
        except urllib.error.HTTPError as e:
            print(e)


def urlretrieve_try_alt(url: str, outputfilename: str):
    outputfilename = Path(constants.HOME, constants.ZIPPED_FOLDER, outputfilename)
    try:
        urllib.request.urlretrieve(url, outputfilename)
    except urllib.error.HTTPError as e:
        success = False
        print(f"404: {url} not found")

        for append in constants.ALT:
            url_txt = make_alt(url, append)
            outputfilename_txt = make_alt(outputfilename, append)
            try:
                urllib.request.urlretrieve(url_txt, outputfilename_txt)
                success = True
                break

            except urllib.error.HTTPError as e:
                print(f"404: {url_txt} not found")
        if success:
            print(f"Found {url_txt}")


def make_folders():

    # Ensure directories exist.
    if not os.path.exists(constants.INDEXES_FOLDER):
        os.mkdir(constants.INDEXES_FOLDER)

    if not os.path.exists(constants.ZIPPED_FOLDER):
        os.mkdir(constants.ZIPPED_FOLDER)

    if not os.path.exists(constants.UNZIPPED_FOLDER):
        os.mkdir(constants.UNZIPPED_FOLDER)


def parse_index():
    manifest_fpath = Path(constants.HOME, constants.MANIFEST_FILENAME)
    if manifest_fpath.is_file():
        print(f"{manifest_fpath} exists")
        f = io.open(manifest_fpath, "r", encoding="utf8").read()
        jobj = json.loads(f)
        return (
            jobj["ebooks"],
            jobj["ebookslanguage"],
            jobj["mirrordir"],
            jobj["mirrorname"],
        )
    # Download the book index, and unzip it.
    fetch(constants.MIRROR, "GUTINDEX.zip", f"{constants.INDEXES_FOLDER}/GUTINDEX.zip")
    if not os.path.exists(f"{constants.INDEXES_FOLDER}/GUTINDEX.ALL") or older(
        f"{constants.INDEXES_FOLDER}/GUTINDEX.ALL",
        f"{constants.INDEXES_FOLDER}/GUTINDEX.zip",
    ):
        print("Extracting GUTINDEX.ALL from GUTINDEX.zip...")
        zipfile.ZipFile(f"{constants.INDEXES_FOLDER}/GUTINDEX.zip").extractall(
            f"{constants.INDEXES_FOLDER}/"
        )
    else:
        print("No need to extract GUTINDEX.ALL")

    # Download the file index, and gunzip it.
    fetch(constants.MIRROR, "ls-lR.gz", f"{constants.INDEXES_FOLDER}/ls-lR.gz")
    if not os.path.exists(f"{constants.INDEXES_FOLDER}/ls-lR") or older(
        f"{constants.INDEXES_FOLDER}/ls-lR", f"{constants.INDEXES_FOLDER}/ls-lR.gz"
    ):
        print("Extracting ls-lR from ls-lR.gz...")
        inf = gzip.open(f"{constants.INDEXES_FOLDER}/ls-lR.gz", "rb")
        outf = open(f"{constants.INDEXES_FOLDER}/ls-lR", "wb")
        outf.write(inf.read())
        inf.close()
        outf.close()
    else:
        print("No need to extract ls-lR")

    # Parse the file index
    print("Parsing file index...")
    mirrordir = {}
    mirrorname = {}
    re_txt0file = re.compile(r".*? (\d+\-0\.zip)")  # UTF-8 encoded (?)
    re_txt8file = re.compile(r".*? (\d+\-8\.zip)")  # latin-8 encoded (?)
    re_txtfile = re.compile(r".*? (\d+\.zip)")  # ascii encoded (?)
    for line in open(f"{constants.INDEXES_FOLDER}/ls-lR"):
        if line.startswith("./"):
            line = line[2:].strip()
            if line.endswith(":"):
                line = line[:-1]
            if line.endswith("old") or "-" in line:
                continue
            lastseendir = line
            continue
        m = re_txt0file.match(line)
        if not m:
            m = re_txt8file.match(line)
        if not m:
            m = re_txtfile.match(line)
        if m:
            filename = m.groups()[0]
            if "-" in filename:  # For filenames like '12104-0.zip'.
                nr, _ = filename.split("-")
            elif "." in filename:  # For filenames like '32901.zip'.
                nr, _ = filename.split(".")
            else:
                print("Unexpected filename:", filename)
            ebookno = int(nr)
            if not ebookno in mirrordir:
                mirrordir[ebookno] = lastseendir
                mirrorname[ebookno] = filename

    # Parse the GUTINDEX.ALL file and extract all language-specific titles from it.
    print("Parsing book index...")
    inpreamble = True
    ebooks = {}  # number -> title
    ebookslanguage = {}  # number -> language
    ebookno = None
    nr = 0
    langre = re.compile(r"\[Language: (\w+)\]")
    for line in codecs.open(
        f"{constants.INDEXES_FOLDER}/GUTINDEX.ALL", encoding="utf8"
    ):
        line = line.replace(
            "\xa0", " "
        )  # Convert non-breaking spaces to ordinary spaces.

        if inpreamble:  # Skip the explanation at the start of the file.
            if "TITLE and AUTHOR" in line:
                inpreamble = False
            else:
                continue

        if not line.strip():
            continue  # Ignore empty lines.

        if line.startswith("<==End of GUTINDEX.ALL"):
            break  # Done.

        if line.startswith((" ", "\t", "[")):
            # Attribute line; see if it specifies the language.
            m = langre.search(line)
            if m:
                language = m.group(1)
                ebookslanguage[ebookno] = language
        else:
            # Possibly title line: "The German Classics     51389"
            parts = line.strip().rsplit(" ", 1)
            if len(parts) < 2:
                continue
            title, ebookno = parts
            title = title.strip()
            try:
                if ebookno.endswith(("B", "C")):
                    ebookno = ebookno[:-1]
                ebookno = int(ebookno)
                # It's a genuine title.
                ebooks[ebookno] = title
            except ValueError:
                continue  # Missing or invalid ebook number

    if not manifest_fpath.is_file():
        with io.open(manifest_fpath, "w+", encoding="utf8") as f:
            f.write(
                json.dumps(
                    {
                        "ebooks": ebooks,
                        "ebookslanguage": ebookslanguage,
                        "mirrordir": mirrordir,
                        "mirrorname": mirrorname,
                    },
                    ensure_ascii=False,
                    indent=4,
                )
            )
            f.close()
            print(f"Wrote {manifest_fpath}")
    return ebooks, ebookslanguage, mirrordir, mirrorname


def download_ebooks(
    ebooks: dict,
    ebookslanguage: dict,
    mirrordir: dict,
    mirrorname: dict,
    print_report: bool = True,
):
    # Default language is English; mark every eBook which hasn't a language specified as English.
    for nr, title in ebooks.items():
        if not nr in ebookslanguage:
            ebookslanguage[nr] = "English"

    if print_report:
        # print(report of found eBooks.)
        nr = 0
        for ebookno in sorted(ebooks.keys()):
            if ebookslanguage[ebookno] != constants.LANGUAGE:
                continue
            titel = ebooks[ebookno].encode("ascii", "replace")
            filename = mirrorname.get(ebookno, "UNKNOWN")
            filedir = mirrordir.get(ebookno, "UNKNOWN")
            print("%d. %s (%s in %s)" % (ebookno, titel, filename, filedir))
            nr += 1
        print("%d ebooks found for language %s" % (nr, constants.LANGUAGE))

    # Fetch the eBook zips.
    n_ebooks = len(ebooks)
    for nr, ebookno in enumerate(sorted(ebooks.keys())):
        if (
            ebookslanguage[ebookno] != constants.LANGUAGE
        ):  # Only fetch books for specified language.
            continue
        filedir = mirrordir.get(ebookno)
        filename = mirrorname.get(ebookno)
        if not filedir or not filename:
            continue
        url = constants.MIRROR + filedir + "/" + filename

        file_exists = file_exists_in_some_form(filename)

        if file_exists:
            print(f"({nr}/{n_ebooks}) {filename} exists, download not necessary")
        else:
            if not filename.startswith("0") and not file_exists:
                print(f"({nr}/{n_ebooks}) downloading {filename}...")
                urlretrieve_try_alt(url, filename)

            # Fast, but requires external wget utility.
            # cmd = "wget -O %s %s" % (fn, url)
            # os.system(cmd)


def unzip_files():
    # Unzip them.
    errors = []
    for fn in glob.glob(f"{constants.ZIPPED_FOLDER}/*.zip"):
        print("extracting", fn)
        try:
            zipfile.ZipFile(fn).extractall(f"{constants.UNZIPPED_FOLDER}/")
        except zipfile.BadZipfile:
            errors.append(
                "Error: can't unzip %s" % fn
            )  # Some files in the Gutenberg archive are damaged.

    # Some extracted files will end up in a subdirectory. Move them up into 'ebooks-unzipped' and remove the empty subdirectory.
    for dirn in glob.glob(f"{constants.UNZIPPED_FOLDER}/*"):
        if os.path.isdir(dirn):
            print("moving", dirn)
            for fn in glob.glob(os.path.join(dirn, "*")):
                parts = fn.split(os.sep)
                ofn = os.path.join(constants.UNZIPPED_FOLDER, parts[-1])
                if os.path.exists(ofn):
                    os.unlink(ofn)
                shutil.move(fn, constants.UNZIPPED_FOLDER)
            os.rmdir(dirn)

    if errors:
        print("Errors:")
        for error in errors:
            print(error)


def move_txt():
    for fn in glob.glob(f"{constants.ZIPPED_FOLDER}/*.txt"):
        shutil.move(fn, Path(constants.HOME, constants.UNZIPPED_FOLDER))


if __name__ == "__main__":
    make_folders()
    ebooks, ebookslanguage, mirrordir, mirrorname = parse_index()
    download_ebooks(ebooks, ebookslanguage, mirrordir, mirrorname, False)
    # unzip_files()
    move_txt()
