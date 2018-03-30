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
    filename = format_quotes(filename)
    valid_chars = '-_.() {}{}'.format(string.ascii_letters, string.digits)
    filename = ''.join(c if c in valid_chars else '_' for c in filename)
    return filename


def format_quotes(filename):
    if '"' not in filename:
        return filename

    if len([c for c in filename if c == '"']) == 1:
        return filename.replace('"', 'in')

    output = []
    last_char = ''
    open_quote = False
    for i, c in enumerate(filename):
        if c == '"':
            if open_quote:
                # Assume that we definitely want to close any quote first
                open_quote = False
            elif last_char == ' ':
                # This is almost definitely an opening quote
                open_quote = True
            elif last_char.isdigit():
                # Almost sure to be inches
                output.append('in')
        else:
            output.append(c)
        last_char = c
    return ''.join(output)
