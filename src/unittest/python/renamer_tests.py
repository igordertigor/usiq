from unittest import TestCase, mock

from usiq import renamer


class TestCreateFilename(TestCase):

    def test_simple_title(self):
        tags = {'title': 'ANY TITLE', 'artist': 'ANY ARTIST'}
        fname = renamer.create_filename(tags, '<artist> - <title>')
        self.assertEqual(fname, 'ANY ARTIST - ANY TITLE')

    @mock.patch('os.path.expanduser')
    def test_accept_tilde_for_filename(self, mock_expanduser):
        mock_expanduser.return_value = '/home/tester/ANY_FILE'
        fname = renamer.create_filename({}, '~/ANY_FILE')
        mock_expanduser.assert_called_once_with('~/ANY_FILE')
        self.assertEqual(fname, '/home/tester/ANY_FILE')

    def test_support_formatted_fields(self):
        tags = {'title': 'ANY TITLE', 'artist': 'ANY ARTIST'}
        fname = renamer.create_filename(tags, '<artist.title> - <title.lower>')
        self.assertEqual(fname, 'Any Artist - any title')

    def test_more_complex_filename(self):
        tags = {'title': 'ANY ? TITLE', 'artist': 'Any Artist/something'}
        fname = renamer.create_filename(tags, '<artist>/<title.lower>')
        self.assertEqual(fname, 'Any Artist_something/any _ title')


class TestFilenames(TestCase):

    def test_simple_name(self):
        valid = renamer.format_filename('any file.txt')
        self.assertEqual(valid, 'any file.txt')

    def test_simple_name_with_replace(self):
        valid = renamer.format_filename('any file?.txt')
        self.assertEqual(valid, 'any file_.txt')

    def test_parenthesis(self):
        valid = renamer.format_filename('any file [feat. dummy].txt')
        self.assertEqual(valid, 'any file (feat. dummy).txt')

    def test_parenthesis_and_inch(self):
        valid = renamer.format_filename('any file [7" version].mp3')
        self.assertEqual(valid, 'any file (7in version).mp3')
