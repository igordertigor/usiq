from unittest import mock, TestCase
import re

from usiq import parser


class TestParser(TestCase):

    @mock.patch('os.path.abspath')
    def test_title_only(self, mock_abspath):
        mock_abspath.return_value = 'ANY_TITLE.mp3'
        tags = parser.parse_filename('ANY_TITLE.mp3', '<title>')
        self.assertDictEqual({'title': 'ANY TITLE'}, tags)

    @mock.patch('os.path.abspath')
    def test_complex_pattern(self, mock_abspath):
        mock_abspath.return_value = '/ANY/PATH/ANY_ARTIST-ANY_TITLE_80BPM.mp3'
        tags = parser.parse_filename('ANY_ARTIST-ANY_TITLE_80BPM.mp3',
                                     '<artist>-<title>_<bpm>BPM')
        self.assertDictEqual(tags,
                             {'title': 'ANY TITLE',
                              'artist': 'ANY ARTIST',
                              'bpm': '80'})


class TestConstructRegexp(TestCase):

    def test_only_title(self):
        regexp = parser.construct_regexp('<title>')
        parsed = re.search(regexp, 'Any title').groupdict()
        self.assertSequenceEqual(list(parsed.keys()), ['title'])

    def test_artist_and_title(self):
        regexp = parser.construct_regexp('<artist>_-_<title>')
        parsed = re.search(regexp, 'Any artist_-_Any title').groupdict()
        self.assertSetEqual(set(parsed.keys()), {'title', 'artist'})
        self.assertEqual(parsed['title'], 'Any title')
        self.assertEqual(parsed['artist'], 'Any artist')

    def test_bpm_is_digits(self):
        regexp = parser.construct_regexp('<title>_(<bpm>BPM)')
        parsed = re.search(regexp, 'Any title_(200BPM)').groupdict()
        self.assertSetEqual(set(parsed.keys()), {'title', 'bpm'})
        self.assertEqual(parsed['title'], 'Any title')
        self.assertEqual(parsed['bpm'], '200')

    def test_album_artist_album_artist_title(self):
        regexp = parser.construct_regexp(
            '<albumartist>/<album>/<artist>_-_<title>_(<bpm>BPM)')
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
        parsed = re.search(regexp,
                           'Any_title_(12A)').groupdict()
        self.assertSetEqual(set(parsed.keys()), {'title', 'key'})
        self.assertEqual(parsed['title'], 'Any_title')
        self.assertEqual(parsed['key'], '12A')

    def test_year_title_key(self):
        regexp = parser.construct_regexp(
            '<year>/<tracknumber>_<title>_(<key>)')
        parsed = re.search(regexp,
                           '2011/04_Any_title_(5b)').groupdict()
        self.assertSetEqual(set(parsed.keys()),
                            {'year', 'tracknumber', 'title', 'key'})
        self.assertEqual(parsed['year'], '2011')
        self.assertEqual(parsed['tracknumber'], '04')
        self.assertEqual(parsed['title'], 'Any_title')
        self.assertEqual(parsed['key'], '5b')

    def test_names_are_separated_by_slash(self):
        regexp = parser.construct_regexp('<artist>_-_<title>')
        parsed = re.search(regexp,
                           '/path/to/any_artist_-_any_title').groupdict()
        self.assertSetEqual(set(parsed.keys()), {'artist', 'title'})
        self.assertEqual(parsed['artist'], 'any_artist')
        self.assertEqual(parsed['title'], 'any_title')

    def test_wildcard(self):
        regexp = parser.construct_regexp('<__any__>_-_<title>')
        parsed = re.search(regexp,
                           '/path/to/any_non-sense_-_any_title').groupdict()
        self.assertSetEqual(set(parsed.keys()), {'title'})
        self.assertEqual(parsed['title'], 'any_title')


class TestGetFields(TestCase):

    def test_simple_get_fields(self):
        fields = parser.get_fields('<artist>_<title>_<bpm>')
        self.assertSetEqual(set(fields), {'artist', 'title', 'bpm'})

    def test_formatted_fields(self):
        fields = parser.get_fields('<artist.lower>_<title>')
        self.assertDictEqual(fields, {'artist': 'lower',
                                      'title': None})
