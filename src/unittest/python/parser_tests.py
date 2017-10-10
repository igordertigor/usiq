from unittest import mock, TestCase
import re

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
        self.assertEqual(regexp, r'(?P<title>.+)$')
        parsed = re.search(regexp, 'Any title').groupdict()
        self.assertSequenceEqual(list(parsed.keys()), ['title'])

    def test_artist_and_title(self):
        regexp = parser.construct_regexp('<artist>_-_<title>')
        self.assertEqual(regexp, r'(?P<artist>.+)_-_(?P<title>.+)$')
        parsed = re.search(regexp, 'Any artist_-_Any title').groupdict()
        self.assertSetEqual(set(parsed.keys()), {'title', 'artist'})
        self.assertEqual(parsed['title'], 'Any title')
        self.assertEqual(parsed['artist'], 'Any artist')

    def test_bpm_is_digits(self):
        regexp = parser.construct_regexp('<title>_(<bpm>BPM)')
        self.assertEqual(regexp, r'(?P<title>.+)_\((?P<bpm>\d+)BPM\)$')
        parsed = re.search(regexp, 'Any title_(200BPM)').groupdict()
        self.assertSetEqual(set(parsed.keys()), {'title', 'bpm'})
        self.assertEqual(parsed['title'], 'Any title')
        self.assertEqual(parsed['bpm'], '200')

    def test_album_artist_album_artist_title(self):
        regexp = parser.construct_regexp(
            '<albumartist>/<album>/<artist>_-_<title>_(<bpm>BPM)')
        self.assertEqual(
            regexp,
            r'(?P<albumartist>.+)/(?P<album>.+)/'
            r'(?P<artist>.+)_-_(?P<title>.+)_\((?P<bpm>\d+)BPM\)$')
        parsed = re.search(regexp,
                           'Any Artist/Any Album/'
                           'Any Artist feat. Any other Artist'
                           '_-_Any title_(200BPM)').groupdict()
        self.assertSetEqual(set(parsed.keys()),
                            {'title', 'artist', 'bpm', 'albumartist', 'album'})
        self.assertEqual(parsed['title'], 'Any title')
        self.assertEqual(parsed['artist'], 'Any Artist feat. Any other Artist')
        self.assertEqual(parsed['bpm'], '200')
        self.assertEqual(parsed['albumartist'], 'Any Artist')
        self.assertEqual(parsed['album'], 'Any Album')

    def test_title_and_key(self):
        regexp = parser.construct_regexp('<title>_(<key>)')
        self.assertEqual(regexp, r'(?P<title>.+)_\((?P<key>\d+[ABab])\)$')
        parsed = re.search(regexp,
                           'Any_title_(12A)').groupdict()
        self.assertSetEqual(set(parsed.keys()), {'title', 'key'})
        self.assertEqual(parsed['title'], 'Any_title')
        self.assertEqual(parsed['key'], '12A')

    def test_year_title_key(self):
        regexp = parser.construct_regexp(
            '<year>/<tracknumber>_<title>_(<key>)')
        self.assertEqual(regexp,
                         r'(?P<year>\d+)/(?P<tracknumber>\d+)_(?P<title>.+)'
                         '_\((?P<key>\d+[ABab])\)$')
        parsed = re.search(regexp,
                           '2011/04_Any_title_(5b)').groupdict()
        self.assertSetEqual(set(parsed.keys()),
                            {'year', 'tracknumber', 'title', 'key'})
        self.assertEqual(parsed['year'], '2011')
        self.assertEqual(parsed['tracknumber'], '04')
        self.assertEqual(parsed['title'], 'Any_title')
        self.assertEqual(parsed['key'], '5b')
