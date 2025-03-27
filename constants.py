from pathlib import Path

MIRROR = "http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/"
LANGUAGE = "English"
HOME = Path(__file__).parent
ALT = ["", "-0", "-8"]

ZIPPED_FOLDER = "ebooks-zipped"
UNZIPPED_FOLDER = "ebooks-unzipped"
INDEXES_FOLDER = "indexes"

MANIFEST_FILENAME = f"manifest_{LANGUAGE}.json"

# Repetitive stuff I don't want to read a 1000 times on my eBook reader.
REMOVE = ["Produced by", "End of the Project Gutenberg", "End of Project Gutenberg"]
