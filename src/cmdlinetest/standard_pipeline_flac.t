First we create two mp3 files using sox

  $ sox -n one_note.flac synth 5 sin 347
  $ sox -n two_notes.flac synth 5 sin 347 sin 354

Now, we tag them by pattern match
  $ usiq --pattern="<artist>_<title>" tag *.flac
  .*INFO.*Setting tags {'(artist|title)': '(note|one)', '(artist|title)': '(one|note)'} on file one_note.flac (re)
  .*INFO.*Setting tags {'(artist|title)': '(notes|two)', '(artist|title)': '(two|notes)'} on file two_notes.flac (re)

Change artist using command line option
  $ usiq --artist="Any Artist" tag *.flac
  .*INFO.*Setting tags {'artist': 'Any Artist'} on file one_note.flac (re)
  .*INFO.*Setting tags {'artist': 'Any Artist'} on file two_notes.flac (re)

Rename by pattern
  $ usiq --pattern="Test/<artist.upper> - <title.upper>" rename *.flac
  .*INFO.*Moving one_note.flac -> Test/ANY ARTIST - NOTE.flac (re)
  .*INFO.*Moving two_notes.flac -> Test/ANY ARTIST - NOTES.flac (re)

Show information
  $ usiq show "Test/ANY ARTIST - NOTE.flac"
  .*INFO.*{.*'artist': 'Any Artist'.*} (re)

Check that ls also gives the right pattern
  $ ls
  Test
  $ ls Test/
  ANY ARTIST - NOTE.flac
  ANY ARTIST - NOTES.flac
