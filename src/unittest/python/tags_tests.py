from unittest import TestCase, mock

from usiq import tags


class TestBpm2Str(TestCase):

    def test_int_should_remain(self):
        self.assertEqual(tags.bpm2str(1), '1')

    def test_float_should_round_and_str(self):
        self.assertEqual(tags.bpm2str(1.4), '1')

    def test_float_should_round_up(self):
        self.assertEqual(tags.bpm2str(1.8), '2')

    def test_round_should_work_with_strings(self):
        self.assertEqual(tags.bpm2str('1.4'), '1')

    def test_round_should_work_with_strings_up(self):
        self.assertEqual(tags.bpm2str('1.8'), '2')


class TestTags(TestCase):

    @mock.patch('mutagen.File')
    def test_save_saves_mutagen_tags(self, mock_file):
        mock_tags = mock.Mock()
        mock_file.return_value = mock_tags

        t = tags.Tags('ANY_FILE')
        mock_file.assert_called_once_with('ANY_FILE')

        mock_tags.assert_not_called()
        t.save()
        mock_tags.save.assert_called_once_with()

    @mock.patch('mutagen.File')
    def test_string_creation(self, mock_file):

        class mockTags(tags.Tags):
            __getitem__ = mock.Mock()

        t = mockTags('ANY_FILE')
        tstr = str(t)

        self.assertIn('{', tstr)
        self.assertIn('}', tstr)

        t.__getitem__.assert_has_calls(
            [mock.call(key) for key in tags.FIELDS],
            any_order=True)


class TestMp3Tags(TestCase):

    @mock.patch('mutagen.File')
    def test_getitem(self, mock_file):
        t = tags.Mp3Tags('ANY_FILE')
        t['title']
        mock_tags = mock_file.return_value
        mock_tag = mock_tags.__getitem__.return_value
        mock_tags.__getitem__.assert_called_once_with('TIT2')
        mock_tag.text.__getitem__.assert_called_once_with(0)

    @mock.patch('mutagen.File')
    def test_setitem(self, mock_file):
        t = tags.Mp3Tags('ANY_FILE')
        t['title'] = 'ANY_TITLE'
        mock_tags = mock_file.return_value
        mock_tag = mock_tags.__getitem__.return_value
        mock_tags.__getitem__.assert_called_once_with('TIT2')
        self.assertSequenceEqual(mock_tag.text, ['ANY_TITLE'])


class TestFlacTags(TestCase):

    @mock.patch('mutagen.File')
    def test_getitem(self, mock_file):
        t = tags.FlacTags('ANY_FILE')
        t['title']
        mock_tags = mock_file.return_value
        mock_tags['title'].__getitem__.assert_called_once_with(0)

    @mock.patch('mutagen.File')
    def test_setitem(self, mock_file):
        t = tags.FlacTags('ANY_FILE')
        t['title'] = 'ANY_TITLE'
        mock_tags = mock_file.return_value
        mock_tags.__setitem__.assert_called_once_with('title', ['ANY_TITLE'])


class TestGetTags(TestCase):

    @mock.patch('mutagen.File')
    def test_returns_mp3_tags_for_mp3(self, mock_file):
        t = tags.get_tags('ANY_FILE.mp3')
        self.assertIsInstance(t, tags.Mp3Tags)

    @mock.patch('mutagen.File')
    def test_returns_flac_tags_for_flac(self, mock_file):
        t = tags.get_tags('ANY_FILE.flac')
        self.assertIsInstance(t, tags.FlacTags)

    @mock.patch('mutagen.File')
    def test_is_case_insensitive(self, mock_file):
        t = tags.get_tags('ANY_FILE.FlAc')
        self.assertIsInstance(t, tags.FlacTags)

    @mock.patch('mutagen.File')
    def test_raises_notaggererror_for_unknown_type(self, mock_file):
        with self.assertRaises(tags.NoTaggerError):
            tags.get_tags('ANY_FILE')
