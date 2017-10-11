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
            self.assertEqual(log_handler.formatted_records[0],
                             "[INFO] Generic: {'artist': 'ANY_ARTIST'}")


class TestTag(TestCase):

    @mock.patch('usiq.tagger.set_multiple_tags')
    @mock.patch('usiq.parser.parse_filename')
    def test_parsed_tags_take_precedence_of_config(self,
                                                   mock_tags_from,
                                                   mock_set_tags):
        mock_tags_from.return_value = {'artist': 'ANY_ARTIST'}
        args = {'--dry': False,
                '--artist': 'NOT_ARTIST',
                '--pattern': '<artist>.mp3'}
        cli.tag(['ANY_FILENAME.mp3'], args)
        mock_set_tags.assert_called_once_with('ANY_FILENAME.mp3',
                                              {'artist': 'ANY_ARTIST'},
                                              prefix='')


# Further tests:
# No default tag set but parsed
# Neither default tag nor parsed
# respects dry switch
# correct logging

# Test rename:
