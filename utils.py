import constants
import io
import os
import json
from pathlib import Path


def create_manifest(
    ebooks: dict, ebookslanguage: dict, mirrordir: dict, mirrorname: dict
):
    manifest_fpath = get_manifest_fpath()
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


def get_manifest_fpath() -> Path:
    return Path(constants.HOME, constants.INDEXES_FOLDER, constants.MANIFEST_FILENAME)


def load_manifest() -> tuple[dict, dict, dict, dict]:
    manifest_fpath = get_manifest_fpath()
    if manifest_fpath.is_file():
        print(f"{manifest_fpath} exists")
        f = io.open(manifest_fpath, "r", encoding="utf8").read()
        jobj = json.loads(f)
        ebooks = jobj["ebooks"]
        ebookslanguage = jobj["ebookslanguage"]
        mirrordir = jobj["mirrordir"]
        mirrorname = jobj["mirrorname"]

        return ebooks, ebookslanguage, mirrordir, mirrorname
    else:
        return None


def get_ebooks_library() -> dict:
    ebooks = os.listdir(Path(constants.HOME, constants.EBOOKS_FOLDER))
    library = {}
    for ebook in ebooks:
        with io.open(
            Path(constants.HOME, constants.EBOOKS_FOLDER, ebook), "r", encoding="utf8"
        ) as f:
            info = json.loads(f.readline())
            library[info["bookno"]] = info
    return library
