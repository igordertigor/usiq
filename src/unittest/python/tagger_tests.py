from unittest import TestCase, mock
import logbook
from mutagen import id3

from usiq import tagger


class TestBpm2Str(TestCase):

    def test_int_should_remain(self):
        self.assertEqual(tagger.bpm2str(1), '1')

    def test_float_should_round_and_str(self):
        self.assertEqual(tagger.bpm2str(1.4), '1')

    def test_float_should_round_up(self):
        self.assertEqual(tagger.bpm2str(1.8), '2')

    def test_round_should_work_with_strings(self):
        self.assertEqual(tagger.bpm2str('1.4'), '1')

    def test_round_should_work_with_strings_up(self):
        self.assertEqual(tagger.bpm2str('1.8'), '2')


class TestTagger(TestCase):

    @mock.patch('mutagen.File')
    def test_save_saves_mutagen_tags(self, mock_file):
        mock_tags = mock.Mock()
        mock_file.return_value = mock_tags

        t = tagger.Tagger('ANY_FILE')
        mock_file.assert_called_once_with('ANY_FILE')

        mock_tags.assert_not_called()
        t.save()
        mock_tags.save.assert_called_once_with()

    @mock.patch('mutagen.File')
    def test_string_creation(self, mock_file):

        class mockTagger(tagger.Tagger):
            __getitem__ = mock.Mock()

        t = mockTagger('ANY_FILE')
        tstr = str(t)

        self.assertIn('{', tstr)
        self.assertIn('}', tstr)

        t.__getitem__.assert_has_calls(
            [mock.call(key) for key in tagger.FIELDS],
            any_order=True)


class TestMp3Tagger(TestCase):

    @mock.patch('mutagen.File')
    def test_getitem(self, mock_file):
        t = tagger.Mp3Tagger('ANY_FILE')
        t['title']
        mock_tags = mock_file.return_value
        mock_tag = mock_tags.__getitem__.return_value
        mock_tags.__getitem__.assert_called_once_with('TIT2')
        mock_tag.text.__getitem__.assert_called_once_with(0)

    @mock.patch('mutagen.File')
    def test_setitem(self, mock_file):
        t = tagger.Mp3Tagger('ANY_FILE')
        t['title'] = 'ANY_TITLE'
        mock_tags = mock_file.return_value
        mock_tags.__setitem__.assert_called_once_with(
            'TIT2',
            id3.TIT2(text=['ANY_TITLE']))


class TestFlacTagger(TestCase):

    @mock.patch('mutagen.File')
    def test_getitem_for_existing_key(self, mock_file):
        mock_file.return_value.__contains__.return_value = True
        t = tagger.FlacTagger('ANY_FILE')
        t['title']
        mock_tags = mock_file.return_value
        mock_tags['title'].__getitem__.assert_called_once_with(0)

    @mock.patch('mutagen.File')
    def test_getitem_for_nonexisting_key(self, mock_file):
        mock_file.return_value.__contains__.return_value = False
        t = tagger.FlacTagger('ANY_FILE')
        t['title']
        mock_tags = mock_file.return_value
        mock_tags['title'].__getitem__.assert_not_called()

    @mock.patch('mutagen.File')
    def test_setitem(self, mock_file):
        t = tagger.FlacTagger('ANY_FILE')
        t['title'] = 'ANY_TITLE'
        mock_tags = mock_file.return_value
        mock_tags.__setitem__.assert_called_once_with('title', ['ANY_TITLE'])


class TestM4aTagger(TestCase):

    def setUp(self):
        self.patch_mutagen = mock.patch('mutagen.File')
        self.mock_mutagen = self.patch_mutagen.start()

    def tearDown(self):
        mock.patch.stopall()

    def test_getitem(self):
        t = tagger.M4aTagger('ANY_FILE')
        t['title']
        mock_tags = self.mock_mutagen.return_value
        mock_tag = mock_tags.__getitem__.return_value
        mock_tags.__getitem__.assert_called_once_with('\xa9nam')
        mock_tag.__getitem__.assert_called_once_with(0)

    def test_setitem(self):
        t = tagger.M4aTagger('ANY_FILE')
        t['title'] = 'ANY_TITLE'
        mock_tags = self.mock_mutagen.return_value
        mock_tags.__setitem__.assert_called_once_with('\xa9nam', ['ANY_TITLE'])

    def test_special_handling_when_getting_tracknumber(self):
        mock_tags = self.mock_mutagen.return_value
        mock_tags.__getitem__.return_value.__getitem__.return_value = (5, 10)
        t = tagger.M4aTagger('ANY_FILE')
        trackno = t['tracknumber']
        self.assertEqual(trackno, '5')

    def test_special_handling_when_setting_tracknumber(self):
        mock_tags = self.mock_mutagen.return_value
        mock_tags.__getitem__.return_value.__getitem__.return_value = (5, 10)
        t = tagger.M4aTagger('ANY_FILE')
        t['tracknumber'] = '6'
        mock_tags.__getitem__.return_value.__setitem__.assert_called_once_with(
            0, (6, 10))

    def test_warning_when_getting_key(self):
        with logbook.TestHandler() as log_handler:
            t = tagger.M4aTagger('ANY_FILE')
            t['key']
            assert log_handler.has_warning(
                'Keys are not supported for M4A files')

    def test_warning_when_setting_key(self):
        with logbook.TestHandler() as log_handler:
            t = tagger.M4aTagger('ANY_FILE')
            t['key'] = 'a4'
            assert log_handler.has_warning(
                'Keys are not supported for M4A files')


class TestGetTagger(TestCase):

    @mock.patch('mutagen.File')
    def test_returns_mp3_tags_for_mp3(self, mock_file):
        t = tagger.get_tagger('ANY_FILE.mp3')
        self.assertIsInstance(t, tagger.Mp3Tagger)

    @mock.patch('mutagen.File')
    def test_returns_flac_tags_for_flac(self, mock_file):
        t = tagger.get_tagger('ANY_FILE.flac')
        self.assertIsInstance(t, tagger.FlacTagger)

    @mock.patch('mutagen.File')
    def test_returns_m4a_tags_for_m4a(self, mock_file):
        t = tagger.get_tagger('ANY_FILE.m4a')
        self.assertIsInstance(t, tagger.M4aTagger)

    @mock.patch('mutagen.File')
    def test_is_case_insensitive(self, mock_file):
        t = tagger.get_tagger('ANY_FILE.FlAc')
        self.assertIsInstance(t, tagger.FlacTagger)

    @mock.patch('mutagen.File')
    def test_raises_notaggererror_for_unknown_type(self, mock_file):
        with self.assertRaises(tagger.NoTaggerError):
            tagger.get_tagger('ANY_FILE')


class TestSetMultipleTags(TestCase):

    def setUp(self):
        self.patch_get_tagger = mock.patch('usiq.tagger.get_tagger')
        self.mock_get_tagger = self.patch_get_tagger.start()
        self.mock_tagger = self.mock_get_tagger.return_value

    def tearDown(self):
        mock.patch.stopall()

    def test_all_tags_are_set(self):
        tagger.set_multiple_tags('ANY_FILENAME', {'artist': 'ANY_ARTIST',
                                                  'title': 'ANY_TITLE'})
        self.mock_tagger.__setitem__.assert_has_calls([
            mock.call('artist', 'ANY_ARTIST'),
            mock.call('title', 'ANY_TITLE')
        ], any_order=True)

    def test_prefix_is_used(self):
        tagger.set_multiple_tags('ANY_FILENAME',
                                 {'--artist': 'THIS', 'artist': 'NOT THIS'},
                                 prefix='--')

        self.mock_tagger.__setitem__.assert_called_once_with('artist', 'THIS')

    def test_empty_tags_sets_nothing(self):
        tagger.set_multiple_tags('ANY_FILENAME', {})
        self.mock_tagger.__setitem__.assert_not_called()

    def test_final_state_is_saved_if_any_tags_changed(self):
        tagger.set_multiple_tags('ANY_FILENAME', {'artist': 'ANY_ARTIST'})
        self.mock_tagger.save.assert_called_once_with()

    def test_final_state_is_not_saved_if_no_tags_changed(self):
        tagger.set_multiple_tags('ANY_FILENAME', {})
        self.mock_tagger.save.assert_not_called()

    def test_invalid_keys_are_ignored(self):
        tagger.set_multiple_tags('ANY_FILENAME', {'INVALID_KEY': 'ANY_VALUE'})
        self.mock_tagger.__setitem__.assert_not_called()
