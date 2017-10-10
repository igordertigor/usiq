import re
import os


def parse_filename(fname, pattern):
    basename, _ = os.path.splitext(os.path.abspath(fname))
    title = basename.replace('_', ' ')
    return {'title': title}


def construct_regexp(pattern):
    fields = re.findall(r'<(.*?)>', pattern)
    regexp = pattern.replace('(', r'\(').replace(')', r'\)')
    regexp = re.sub(r'<(artist|title)>', r'(P<\1>.+)', regexp)
    # TODO: other keys
    if 'bpm' in fields:
        regexp = re.sub(r'<bpm>', r'(P<bpm>\d+)', regexp)
    # TODO: InitialKey
    return regexp + '$'
