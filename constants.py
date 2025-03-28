from pathlib import Path


# These parameters you can change yourself
MIRROR = "http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/"
# This is the language you want to scrape.
LANGUAGE = "English"


HOME = Path(__file__).parent
ALT = ["", "-0", "-8"]


EBOOKS_FOLDER = "ebooks"
ZIPPED_FOLDER = "ebooks-zipped"
UNZIPPED_FOLDER = "ebooks-unzipped"
INDEXES_FOLDER = "indexes"


UNKNOWN_TITLE = "UNKNOWN_TITLE"
UNKNOWN_AUTHOR = "UNKNOWN_AUTHOR"
UNKNOWN_LANGUAGE = "UNKNOWN_LANGUAGE"
DEFAULT_LANGUAGE = "English"


MANIFEST_FILENAME = f"manifest.json"

# Repetitive stuff I don't want to read a 1000 times on my eBook reader.
REMOVE = ["Produced by", "End of the Project Gutenberg", "End of Project Gutenberg"]
