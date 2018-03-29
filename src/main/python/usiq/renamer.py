import os
import string
from . import parser


def create_filename(tags, pattern):
    fields = parser.get_fields(pattern)
    for field, formatter in fields.items():
        if formatter:
            pattern = pattern.replace(
                '<{}.{}>'.format(field, formatter),
                format_filename(getattr(tags[field], formatter)()))
        else:
            pattern = pattern.replace(
                '<{}>'.format(field),
                format_filename(tags[field]))
    return os.path.expanduser(pattern)


def format_filename(filename):
    filename = filename.replace('[', '(').replace(']', ')')
    filename = filename.replace('"', 'in')
    valid_chars = '-_.() {}{}'.format(string.ascii_letters, string.digits)
    filename = ''.join(c if c in valid_chars else '_' for c in filename)
    return filename
