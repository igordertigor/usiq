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
    number_fields = {'bpm', 'year', 'tracknumber'}
    complex_fields = number_fields | {'key'}
    simple_fields = list(fields - complex_fields)
    regexp = re.sub(r'<({})>'.format('|'.join(simple_fields)),
                    r'(P<\1>.+)',
                    regexp)
    for field in number_fields:
        if field in fields:
            regexp = re.sub(r'<{}>'.format(field),
                            r'(P<{}>\d+)'.format(field),
                            regexp)

    if 'key' in fields:
        regexp = re.sub(r'<key>', r'(P<key>\d+[ABab])', regexp)
    return regexp + '$'
