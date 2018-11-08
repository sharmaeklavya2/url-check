# URL Check

Find broken URLs in HTML files in a directory.

    python3 url_check.py path/to/directory

The program `url_check.py` scans all files in a directory (recursively)
and figures out what should be the URL for each of those files.
It creates a collection of these URLs.

Then for each HTML file in that directory,
it finds URLs in `href` and `src` attributes of all tags
and checks if those URLs are present in the collection of URLs.

Both relative and absolute URLs are allowed in HTML files,
but for absolute URLs, `--base-url` must be passed to `url_check.py`.
