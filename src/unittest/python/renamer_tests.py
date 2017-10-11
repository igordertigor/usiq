from unittest import TestCase, mock

from usiq import renamer


class TestCreateFilename(TestCase):

    def test_simple_title(self):
        tags = {'title': 'ANY TITLE', 'artist': 'ANY ARTIST'}
        fname = renamer.create_filename(tags, '<artist> - <title>.mp3')
        self.assertEqual(fname, 'ANY ARTIST - ANY TITLE.mp3')
