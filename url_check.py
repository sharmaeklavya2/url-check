#!/usr/bin/env python3

import sys
import os
from os.path import join as pjoin
from collections import OrderedDict
from urllib.parse import urljoin
import argparse


PROG_NAME = os.path.basename(os.path.abspath(__file__))


def print_error_message(msg, exit_code=None):
    if not isinstance(msg, str):
        msg = ': '.join(msg)
    print('{}: {}'.format(PROG_NAME, msg), file=sys.stderr)
    if exit_code is not None:
        sys.exit(exit_code)


def scan(root_path, base_url, url_to_fpath_map=None, fpath_url_pairs=None, verbosity=0):
    if not os.path.isdir(root_path):
        print_error_message('{} is not a directory'.format(repr(root_path)), 1)
    if not base_url.endswith('/'):
        base_url += '/'
    if url_to_fpath_map is None:
        url_to_fpath_map = OrderedDict()
    if fpath_url_pairs is None:
        fpath_url_pairs = []

    for dirpath, dnames, fnames in os.walk(root_path):
        dirpath2 = os.path.relpath(dirpath, root_path)
        for fname in fnames:
            fpath = pjoin(dirpath2, fname)
            if fpath.startswith('./'):
                fpath = fpath[2:]
            url = urljoin(base_url, fpath)
            if verbosity >= 1:
                print('scan: {} -> {}'.format(fpath, url))
            url_to_fpath_map[url] = fpath
            if fname == 'index.html':
                url2 = urljoin(base_url, dirpath2)
                if not url2.endswith('/'):
                    url2 = url2 + '/'
                if verbosity >= 1:
                    print('scan: {} -> {}'.format(fpath, url2))
                url_to_fpath_map[url2] = fpath

    return url_to_fpath_map


def check_urls(fpath, page_url, base_url, url_map, verbosity=0):
    from lxml import etree

    with open(fpath) as fp:
        text = fp.read().strip()
    document = etree.HTML(text)

    error_count = 0
    for tag in document.iter():
        url = None
        for attr in ['src', 'href']:
            url = tag.attrib.get(attr)
            if url is not None:
                break

        if url is not None:
            if verbosity >= 2:
                print('{}.{}: {}'.format(tag.tag, attr, url))
            url2 = url.split('#')[0].split('?')[0]
            abs_url = urljoin(page_url, url2)
            if not abs_url.startswith(base_url):
                continue
            if abs_url not in url_map:
                error_count += 1
                print('{fpath}:{line}: {tag}.{attr}: {url} not found'.format(
                    url=url2, tag=tag.tag, attr=attr, fpath=fpath, line=tag.sourceline))
    return error_count


def check_urls_in_all_files(root_path, base_url, url_to_fpath_map, verbosity=0):
    if not base_url.endswith('/'):
        base_url += '/'
    error_count = 0
    for url, fpath in url_to_fpath_map.items():
        if fpath.endswith('.html'):
            fpath2 = pjoin(root_path, fpath)
            error_count += check_urls(fpath2, url, base_url, url_to_fpath_map, verbosity=verbosity)
    return error_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fpath', help='Path to file/directory where to check urls')
    parser.add_argument('--base-url', help='URL of website')
    parser.add_argument('-v', '--verbose', dest='verbosity', action='count', default=0)
    args = parser.parse_args()

    base_url = args.base_url
    if base_url is None:
        base_url = '/'.join(list('abcdefgh'))

    url_to_fpath_map = scan(args.fpath, base_url, verbosity=args.verbosity)
    error_count = check_urls_in_all_files(args.fpath, base_url, url_to_fpath_map,
        verbosity=args.verbosity)
    if error_count:
        sys.exit(1)


if __name__ == '__main__':
    main()
