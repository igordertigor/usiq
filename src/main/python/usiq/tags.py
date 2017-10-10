import mutagen


class Tags(object):

    def __init__(self, fname):
        self.tags = mutagen.File(fname)

    def save(self):
        self.tags.save()

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __str__(self):
        return str({key: self[key]
                    for key in ['title',
                                'artist',
                                'album',
                                'genre',
                                'albumartist',
                                'bpm',
                                'key']})


class Mp3Tags(Tags):

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
             'key': 'TKEY',
             }
        return d[key]


class FlacTags(Tags):

    def __getitem__(self, key):
        return self.tags[key][0]

    def __setitem__(self, key, value):
        self.tags[key] = [value]


def bpm2str(value):
    return str(int(round(float(value))))
