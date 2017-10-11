from . import parser


def create_filename(tags, pattern):
    fields = parser.get_fields(pattern)
    for field in fields:
        pattern = pattern.replace('<{}>'.format(field), tags[field])
    return pattern
