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
