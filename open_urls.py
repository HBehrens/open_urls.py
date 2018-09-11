#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import subprocess
import argparse

ALL_FINDERS = dict()

# John Gruber's regex from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
REGEX_URL = re.compile(r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")
def find_urls(line):
    def normalized(url):
        return url if ':' in url else ('http://' + url)

    return set(normalized(url) for url in REGEX_URL.findall(line))

ALL_FINDERS['urls'] = find_urls


# maps tasks such as T1234 -> https://tasks/1234
REGEX_TASK = re.compile(r"""\bT(\d+)\b""")
def find_tasks(line):
    return set('https://tasks/' + m.group(1) for m in REGEX_TASK.finditer(line))

ALL_FINDERS['tasks'] = find_tasks


def find_all(lines, finders):
    urls = set()
    for line in lines:
        for finder in finders:
            urls.update(finder(line))
    return urls


def process_file(infile, finders, cmd, dry_run):
    lines = infile.readlines()

    for url in find_all(lines, finders):
        args = '{} {}'.format(cmd, url).strip()
        if dry_run:
            print(args)
        else:
            result = subprocess.call(args, shell=True)
            if result != 0:
                exit(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scans file for patterns and opens found URLs.')
    parser.add_argument('infile', metavar='FILE', type=argparse.FileType('r'),
                        help='file to analyze')
    finder_keys = sorted(ALL_FINDERS.keys())
    parser.add_argument('--finders', dest='finders', nargs='*', default=finder_keys,
                        choices=finder_keys,
                        help='only given set of finders')
    parser.add_argument('--cmd', dest='cmd', default='open',
                        help='command to execute for each URL')
    parser.add_argument('--dry-run', dest='dry_run', action='store_const', const=True,
                        help='print all commands to be executed')

    args = parser.parse_args()
    args.finders = [finder for key, finder in ALL_FINDERS.items() if key in args.finders]

    process_file(args.infile, args.finders, args.cmd, args.dry_run)
