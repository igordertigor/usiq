import re
import os

from .tagger import FIELDS


def parse_filename(fname, pattern):
    basename, _ = os.path.splitext(os.path.abspath(fname))
    title = basename.replace('_', ' ')
    return {'title': title}


def construct_regexp(pattern):
    fields = set(re.findall(r'<(.*?)>', pattern)).intersection(set(FIELDS))
    regexp = pattern.replace('(', r'\(').replace(')', r'\)')
    simple_fields = list(fields - {'bpm', 'key'})
    regexp = re.sub(r'<({})>'.format('|'.join(simple_fields)),
                    r'(P<\1>.+)',
                    regexp)
    if 'bpm' in fields:
        regexp = re.sub(r'<bpm>', r'(P<bpm>\d+)', regexp)

    if 'key' in fields:
        regexp = re.sub(r'<key>', r'(P<key>\d+[ABab])', regexp)
    # TODO: InitialKey
    return regexp + '$'
