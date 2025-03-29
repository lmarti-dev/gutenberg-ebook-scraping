
# Original README

This is a set of python scripts which downloads all 
Dutch ebooks from Project Gutenberg, renames them to
human-readabele filenames, formats them so they display well 
on my ebook reader, and tosses them into subdirectories for 
easier navigation.

Written by Michiel Overtoom, motoom@xs4all.nl

How to use:

- Run bulkdownload.py to download the raw texts from a mirror of Project Gutenberg's eBook archive.
- Run gutenberg.py to reformat and rename the raw texts.
- Run toss.py to distribute them over subdirectories.

After that, upload them to your eBook reader, and enjoy!

In March 2016 I reworked this program since it's no longer allowed to scrape
from Gutenberg's main web site. This newer version:

- downloads from a mirror instead of scraping from Gutenberg's main web site
- language can be specified
- better input encoding detection
- outputs UTF8 encoded text files

# March 2025 update

I improved the code in a few places. Notably,

- Codecs are now managed by an external library, `charset_normalizer`. All the ebooks are converted to utf8.
- The title is not heuristically found from the text file, but rather from the manifest, which already contains it.
- The ebook info is saved in a manifest.json file to avoid running some costly for loops again. 
- Some ebooks were not stored in zip format but rather in txt. The code now looks for likely filename alternatives before giving up.
- `sift.py` allows one to peek at the largest ebooks (some of them are 200MB) to see whether they're worth keeping. 
- The final ebooks have a json snippet in the first line so that one can get the information easily using a single `readline()`
- Important values are set in `constants.py`