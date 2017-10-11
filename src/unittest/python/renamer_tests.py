from unittest import TestCase, mock

from usiq import rename


class TestCreateFilename(TestCase):

    def test_simple_title(self):
        tags = {'title': 'ANY TITLE', 'artist': 'ANY ARTIST'}
        fname = rename.create_filename(tags, '<artist> - <title>.mp3')
        self.assertEqual(fname, 'ANY ARTIST - ANY TITLE.mp3')
