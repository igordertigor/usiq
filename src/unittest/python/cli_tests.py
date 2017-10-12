from unittest import TestCase, mock

import logbook

from usiq import cli


class TestShow(TestCase):

    @mock.patch('usiq.tagger.get_tagger')
    def test_show(self, mock_tagger):
        mock_tagger.return_value = {'artist': 'ANY_ARTIST'}
        with logbook.TestHandler() as log_handler:
            cli.show('ANY_FILENAME')
            mock_tagger.assert_called_once_with('ANY_FILENAME')
            self.assertIn("{'artist': 'ANY_ARTIST'}",
                          log_handler.formatted_records[0])


class TestTag(TestCase):

    def setUp(self):
        self.patch_set_tags = mock.patch('usiq.tagger.set_multiple_tags')
        self.patch_parse_filename = mock.patch('usiq.parser.parse_filename')
        self.mock_set_tags = self.patch_set_tags.start()
        self.mock_parse_filename = self.patch_parse_filename.start()

    def tearDown(self):
        mock.patch.stopall()

    def test_parsed_tags_take_precedence_over_config(self):
        self.mock_parse_filename.return_value = {'artist': 'ANY_ARTIST'}
        args = {'--dry': False,
                '--artist': 'NOT_ARTIST',
                '--pattern': '<artist>'}

        cli.tag(['ANY_FILENAME.mp3'], args)

        self.mock_parse_filename.assert_called_once_with('ANY_FILENAME.mp3',
                                                         '<artist>')
        self.mock_set_tags.assert_called_once_with('ANY_FILENAME.mp3',
                                                   {'artist': 'ANY_ARTIST'},
                                                   prefix='')

    def test_no_default_tag_set_but_value_parsed_from_fname(self):
        self.mock_parse_filename.return_value = {'artist': 'ANY_ARTIST'}
        args = {'--dry': False,
                '--artist': None,
                '--pattern': '<artist>'}

        cli.tag(['ANY_FILENAME.mp3'], args)

        self.mock_parse_filename.assert_called_once_with('ANY_FILENAME.mp3',
                                                         '<artist>')
        self.mock_set_tags.assert_called_once_with('ANY_FILENAME.mp3',
                                                   {'artist': 'ANY_ARTIST'},
                                                   prefix='')

    def test_neither_default_tag_nor_parsed_doesnt_touch_tag(self):
        self.mock_parse_filename.return_value = {}
        args = {'--dry': False,
                '--artist': None,
                '--pattern': 'ANY_PATTERN'}

        cli.tag(['ANY_FILENAME.mp3'], args)

        self.mock_parse_filename.assert_called_once_with('ANY_FILENAME.mp3',
                                                         'ANY_PATTERN')
        self.mock_set_tags.assert_called_once_with('ANY_FILENAME.mp3',
                                                   {},
                                                   prefix='')

    def test_dry_run_doesnt_set_tags(self):
        self.mock_parse_filename.return_value = {'artist': 'ANY_ARTIST'}
        args = {'--dry': True, '--pattern': 'ANY_PATTERN'}

        cli.tag(['ANY_FILENAME.mp3'], args)

        self.mock_set_tags.assert_not_called()

    def test_multiple_filenames(self):
        self.mock_parse_filename.return_value = {'artist': 'ANY_ARTIST'}
        args = {'--dry': False, '--pattern': 'ANY_PATTERN'}

        cli.tag(['FIRST_FILE.mp3', 'SECOND_FILE.flac'], args)

        self.mock_parse_filename.assert_has_calls(
            [mock.call('FIRST_FILE.mp3', 'ANY_PATTERN'),
             mock.call('SECOND_FILE.flac', 'ANY_PATTERN')],
            any_order=True)
        self.mock_set_tags.assert_has_calls(
            [mock.call('FIRST_FILE.mp3',
                       {'artist': 'ANY_ARTIST'},
                       prefix=''),
             mock.call('SECOND_FILE.flac',
                       {'artist': 'ANY_ARTIST'},
                       prefix='')],
            any_order=True)

    def test_logging_if_dry_run(self):
        with logbook.TestHandler() as log_handler:
            self.mock_parse_filename.return_value = {}
            cli.tag(['ANY_FILENAME.mp3'],
                    {'--artist': 'ANY_ARTIST',
                     '--dry': True,
                     '--pattern': 'ANY_PATTERN'})
            should_log = ("Setting tags {'artist': 'ANY_ARTIST'}"
                          " on file ANY_FILENAME.mp3")
            self.assertIn(should_log, log_handler.formatted_records[0])

    def test_logging_if_wet_run(self):
        with logbook.TestHandler() as log_handler:
            self.mock_parse_filename.return_value = {}
            cli.tag(['ANY_FILENAME.mp3'],
                    {'--artist': 'ANY_ARTIST',
                     '--dry': False,
                     '--pattern': 'ANY_PATTERN'})
            should_log = ("Setting tags {'artist': 'ANY_ARTIST'}"
                          " on file ANY_FILENAME.mp3")
            self.assertIn(should_log, log_handler.formatted_records[0])


# Test rename:
