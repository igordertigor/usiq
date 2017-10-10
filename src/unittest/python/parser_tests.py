from unittest import mock, TestCase

from usiq import parser


class TestParser(TestCase):

    @mock.patch('os.path.abspath')
    def test_title_only(self, mock_abspath):
        mock_abspath.return_value = 'ANY_TITLE.mp3'
        tags = parser.parse_filename('ANY_TITLE.mp3', '<title>')
        self.assertDictEqual({'title': 'ANY TITLE'}, tags)


class TestConstructRegexp(TestCase):

    def test_only_title(self):
        regexp = parser.construct_regexp('<title>')
        self.assertEqual(regexp, r'(P<title>.+)$')

    def test_artist_and_title(self):
        regexp = parser.construct_regexp('<artist>_-_<title>')
        self.assertEqual(regexp, r'(P<artist>.+)_-_(P<title>.+)$')

    def test_bpm_is_digits(self):
        regexp = parser.construct_regexp('<title>_(<bpm>BPM)')
        self.assertEqual(regexp, r'(P<title>.+)_\((P<bpm>\d+)BPM\)$')

    def test_album_artist_album_artist_title(self):
        regexp = parser.construct_regexp(
            '<albumartist>/<album>/<artist>_-_<title>_(<bpm>BPM).flac')
        self.assertEqual(
            regexp,
            r'(P<albumartist>.+)/(P<album>.+)/'
            r'(P<artist>.+)_-_(P<title>.+)_\((P<bpm>\d+)BPM\).flac$')

    def test_title_and_key(self):
        regexp = parser.construct_regexp('<title>_(<key>).mp3')
        self.assertEqual(regexp, r'(P<title>.+)_\((P<key>\d+[ABab])\).mp3$')

    def test_year_title_key(self):
        regexp = parser.construct_regexp(
            '<year>/<tracknumber>_<title>_(<key>).mp3')
        self.assertEqual(regexp,
                         r'(P<year>\d+)/(P<tracknumber>\d+)_(P<title>.+)'
                         '_\((P<key>\d+[ABab])\).mp3$')
