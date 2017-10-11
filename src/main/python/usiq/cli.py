import os
import sys
from logbook import StreamHandler, info

from usiq import tagger, parser, renamer

StreamHandler(sys.stdout).push_application()


def show(fname):
    info(tagger.get_tagger(fname))


def tag(fnames, args):
    default_tags = {key: args['--' + key]
                    for key in tagger.FIELDS
                    if '--' + key in args and args['--' + key] is not None}
    for fname in fnames:
        tags = default_tags.copy()
        tags.update(parser.parse_filename(fname, args['--pattern']))
        info('Setting tags {} on file {}'.format(tags, fname))
        if not args['--dry']:
            tagger.set_multiple_tags(fname, tags, prefix='')


def rename(fnames, args):
    for fname in fnames:
        tags = tagger.get_tagger(fname)
        new_fname = renamer.create_filename(tags, args['--pattern'])
        _, extension = os.path.splitext(fname)
        new_fname += extension
        info('Moving {} -> {}'.format(fname, new_fname))
        if not args['--dry']:
            os.rename(fname, new_fname)
