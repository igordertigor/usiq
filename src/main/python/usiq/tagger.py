import os
import mutagen


FIELDS = ('title',
          'artist',
          'album',
          'genre',
          'albumartist',
          'bpm',
          'key',
          'tracknumber',
          'year')


class NoTaggerError(Exception):
    pass


class Tagger(object):

    def __init__(self, fname):
        self.tags = mutagen.File(fname)

    def save(self):
        self.tags.save()

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __str__(self):
        return str({key: self[key] for key in FIELDS})


class Mp3Tagger(Tagger):

    supported_extensions = ('.mp3',)

    def __getitem__(self, key):
        return self.tags[self.translate_key(key)].text[0]

    def __setitem__(self, key, value):
        self.tags[self.translate_key(key)].text = [value]

    @staticmethod
    def translate_key(key):
        d = {'title': 'TIT2',
             'artist': 'TPE1',
             'album': 'TALB',
             'genre': 'TCON',
             'albumartist': 'TPE2',
             'bpm': 'TBPM',
             'tracknumber': 'TRCK',
             'year': 'TYER',
             'key': 'TKEY',
             }
        return d[key]


class FlacTagger(Tagger):

    supported_extensions = ('.flac', '.ogg')

    def __getitem__(self, key):
        return self.tags[key][0]

    def __setitem__(self, key, value):
        self.tags[key] = [value]


def get_tagger(fname):
    basename, extension = os.path.splitext(fname)
    tagger = [tagr
              for tagr in Tagger.__subclasses__()
              if extension.lower() in tagr.supported_extensions]
    if len(tagger):
        return tagger[0](fname)
    else:
        raise NoTaggerError('Could not find tagger for extension {}'
                            .format(extension))


def bpm2str(value):
    return str(int(round(float(value))))


def set_multiple_tags(fname, tags, prefix=''):
    tagger = get_tagger(fname)
    for key in FIELDS:
        value = tags[prefix + key]
        if value is not None:
            tagger[key] = value
    tagger.save()
