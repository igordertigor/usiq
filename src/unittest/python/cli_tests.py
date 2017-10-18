from unittest import TestCase, mock
from io import StringIO
import yaml

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
                '--import': None,
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
                '--import': None,
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
                '--import': None,
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
        args = {'--dry': True, '--import': None, '--pattern': 'ANY_PATTERN'}

        cli.tag(['ANY_FILENAME.mp3'], args)

        self.mock_set_tags.assert_not_called()

    def test_multiple_filenames(self):
        self.mock_parse_filename.return_value = {'artist': 'ANY_ARTIST'}
        args = {'--dry': False, '--import': None, '--pattern': 'ANY_PATTERN'}

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
                     '--import': None,
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
                     '--import': None,
                     '--dry': False,
                     '--pattern': 'ANY_PATTERN'})
            should_log = ("Setting tags {'artist': 'ANY_ARTIST'}"
                          " on file ANY_FILENAME.mp3")
            self.assertIn(should_log, log_handler.formatted_records[0])

    def test_no_pattern_no_parsing(self):
        cli.tag(['ANY_FILENAME.mp3'],
                {'--artist': 'ANY_ARTIST',
                 '--import': None,
                 '--dry': False,
                 '--pattern': None})
        self.mock_parse_filename.assert_not_called()
        self.mock_set_tags.assert_called_once_with('ANY_FILENAME.mp3',
                                                   {'artist': 'ANY_ARTIST'},
                                                   prefix='')

    @mock.patch('os.path.abspath')
    @mock.patch('builtins.open')
    @mock.patch('yaml.load')
    def test_tags_are_read_from_yaml_file(self,
                                          mock_load,
                                          mock_open,
                                          mock_abspath):
        mock_load.return_value = {'ANY_FILENAME.mp3': {'artist': 'ANY_ARTIST'}}
        mock_abspath.side_effect = lambda fname: fname
        cli.tag(['ANY_FILENAME.mp3'],
                {'--import': 'ANY_YAML',
                 '--dry': False,
                 '--pattern': None})
        mock_load.assert_called_once_with(mock_open.return_value)
        self.mock_set_tags.assert_called_once_with('ANY_FILENAME.mp3',
                                                   {'artist': 'ANY_ARTIST'},
                                                   prefix='')

    @mock.patch('os.path.abspath')
    @mock.patch('builtins.open')
    @mock.patch('yaml.load')
    def test_pattern_takes_precedence_over_yaml(self,
                                                mock_load,
                                                mock_open,
                                                mock_abspath):
        mock_load.return_value = {'FILENAME_ARTIST.mp3':
                                  {'artist': 'ANY_ARTIST'}}
        mock_abspath.side_effect = lambda fname: fname
        self.mock_parse_filename.return_value = {'artist': 'FILENAME_ARTIST'}
        cli.tag(['FILENAME_ARTIST.mp3'],
                {'--import': 'ANY_YAML',
                 '--dry': False,
                 '--pattern': '<artist>'})
        self.mock_set_tags.assert_called_once_with(
            'FILENAME_ARTIST.mp3',
            {'artist': 'FILENAME_ARTIST'},
            prefix='')

    @mock.patch('os.path.abspath')
    @mock.patch('builtins.open')
    @mock.patch('yaml.load')
    def test_arguments_take_precendece_over_yaml(self,
                                                 mock_load,
                                                 mock_open,
                                                 mock_abspath):
        mock_load.return_value = {'ANY_FILE.mp3':
                                  {'artist': 'ANY_ARTIST'}}
        mock_abspath.side_effect = lambda fname: fname
        cli.tag(['ANY_FILE.mp3'],
                {'--import': 'ANY_YAML',
                 '--dry': False,
                 '--pattern': None,
                 '--artist': 'OTHER ARTIST'})
        self.mock_set_tags.assert_called_once_with(
            'ANY_FILE.mp3',
            {'artist': 'OTHER ARTIST'},
            prefix='')


class TestRename(TestCase):

    def setUp(self):
        self.patch_rename = mock.patch('os.rename')
        self.patch_get_tagger = mock.patch('usiq.tagger.get_tagger')
        self.patch_path_exists = mock.patch('os.path.exists')
        self.patch_makedirs = mock.patch('os.makedirs')
        self.mock_rename = self.patch_rename.start()
        self.mock_get_tagger = self.patch_get_tagger.start()
        self.mock_path_exists = self.patch_path_exists.start()
        self.mock_makedirs = self.patch_makedirs.start()
        self.mock_get_tagger.return_value = {'artist': 'ANY_ARTIST',
                                             'title': 'ANY_TITLE',
                                             'bpm': '101'}
        self.mock_path_exists.return_value = False

    def tearDown(self):
        mock.patch.stopall()

    def test_operates_on_all_filenames(self):
        cli.rename(['FIRST_FILE.mp3', 'SECOND_FILE.flac'],
                   {'--dry': False, '--pattern': '<artist>'})
        self.mock_rename.assert_has_calls(
            [mock.call('FIRST_FILE.mp3', 'ANY_ARTIST.mp3'),
             mock.call('SECOND_FILE.flac', 'ANY_ARTIST.flac')],
            any_order=True)

    def test_fails_for_empty_patterns(self):
        with self.assertRaises(cli.UsiqError):
            cli.rename(['ANY_FILE.mp3'],
                       {'--dry': False, '--pattern': ''})

    def test_fails_for_constant_patterns(self):
        with self.assertRaises(cli.UsiqError):
            cli.rename(['ANY_FILE.mp3'],
                       {'--dry': False, '--pattern': 'CONSTANT_PATTERN'})

    def test_honors_dry_run(self):
        cli.rename(['ANY_FILE.mp3'],
                   {'--dry': True, '--pattern': '<artist>'})
        self.mock_rename.assert_not_called()

    def test_logs_if_dry_run(self):
        with logbook.TestHandler() as log_handler:
            cli.rename(['ANY_FILE.mp3'],
                       {'--dry': True, '--pattern': '<artist>'})
            should_log = "Moving ANY_FILE.mp3 -> ANY_ARTIST.mp3"
            self.assertIn(should_log, log_handler.formatted_records[0])

    def test_logs_if_wet_run(self):
        with logbook.TestHandler() as log_handler:
            cli.rename(['ANY_FILE.mp3'],
                       {'--dry': False, '--pattern': '<artist>'})
            should_log = "Moving ANY_FILE.mp3 -> ANY_ARTIST.mp3"
            self.assertIn(should_log, log_handler.formatted_records[0])

    def test_adds_file_extension_to_pattern(self):
        cli.rename(['ANY_FILE.ANY_EXTENSION'],
                   {'--dry': False, '--pattern': '<artist>'})
        self.mock_rename.assert_called_once_with('ANY_FILE.ANY_EXTENSION',
                                                 'ANY_ARTIST.ANY_EXTENSION')

    def test_fails_if_pattern_has_extension(self):
        with self.assertRaises(cli.UsiqError):
            cli.rename(['ANY_FILE.mp3'],
                       {'--dry': False, '--pattern': '<artist>.mp3'})

    def test_does_not_move_to_existing_file(self):
        self.mock_path_exists.return_value = True
        with logbook.TestHandler() as log_handler:
            cli.rename(['ANY_FILE.mp3'],
                       {'--dry': False, '--pattern': '<artist>'})
            should_log = ("Not moving ANY_FILE.mp3 -> ANY_ARTIST.mp3,"
                          " target file exists!")
            self.assertIn(should_log, log_handler.formatted_records[0])

        self.mock_rename.assert_not_called()

    def test_creates_directory_if_non_existent(self):
        self.mock_path_exists.side_effect = lambda x: (not x ==
                                                       'ANY_FOLDER/ANY_ARTIST'
                                                       '.mp3')
        cli.rename(['ANY_FILE.mp3'],
                   {'--dry': False, '--pattern': 'ANY_FOLDER/<artist>'})
        self.mock_makedirs.assert_called_once_with('ANY_FOLDER', exist_ok=True)
        self.mock_rename.assert_called_once_with('ANY_FILE.mp3',
                                                 'ANY_FOLDER/ANY_ARTIST.mp3')


class TestExport(TestCase):

    @mock.patch('os.path.abspath', side_effect=lambda fn: '/abs/' + fn)
    @mock.patch('usiq.cli.open_file_or_stdinout')
    @mock.patch('usiq.tagger.get_tagger')
    def test_happy_path(self, mock_get_tagger, mock_open, mock_abspath):
        fake_open_file = StringIO()
        mock_open.return_value.__enter__.return_value = fake_open_file

        mock_get_tagger.return_value.todict.side_effect = [
            {'artist': 'FIRST'},
            {'artist': 'SECOND'},
        ]

        cli.export(['FIRST_FILE.mp3', 'SECOND_FILE.flac'],
                   {'--output': 'out.yaml'})

        mock_open.assert_called_once_with('out.yaml', 'w')
        fake_open_file.seek(0)
        recovered_yaml = yaml.load(fake_open_file.read())
        self.assertDictEqual(recovered_yaml,
                             {'/abs/FIRST_FILE.mp3': {'artist': 'FIRST'},
                              '/abs/SECOND_FILE.flac': {'artist': 'SECOND'}})
        mock_abspath.assert_has_calls([mock.call('FIRST_FILE.mp3'),
                                       mock.call('SECOND_FILE.flac')],
                                      any_order=True)


class TestConfig(TestCase):

    @mock.patch('os.path.exists')
    @mock.patch('builtins.open')
    @mock.patch('yaml.load')
    def test_with_config(self, mock_load, mock_open, mock_exists):
        mock_exists.return_value = True
        mock_load.return_value = {'--artist': 'ANY_ARTIST',
                                  '--pattern': '<title>'}
        args = cli.with_config({'--artist': 'ANY_OTHER_ARTIST',
                                '--config': 'ANY_CONFIG_FILE'})
        self.assertDictEqual(args, {'--artist': 'ANY_OTHER_ARTIST',
                                    '--config': 'ANY_CONFIG_FILE',
                                    '--pattern': '<title>'})
        mock_load.assert_has_calls([mock.call(mock_open().__enter__())])
        mock_open.assert_has_calls([mock.call('ANY_CONFIG_FILE')])

    @mock.patch('os.path.exists')
    @mock.patch('builtins.open')
    @mock.patch('yaml.load')
    def test_without_config(self, mock_load, mock_open, mock_exists):
        mock_exists.return_value = False
        args = cli.with_config({'--artist': 'ANY_OTHER_ARTIST',
                                '--config': 'ANY_CONFIG_FILE'})
        self.assertDictEqual(args, {'--artist': 'ANY_OTHER_ARTIST',
                                    '--config': 'ANY_CONFIG_FILE'})
        mock_load.assert_not_called()
        mock_open.assert_not_called()
