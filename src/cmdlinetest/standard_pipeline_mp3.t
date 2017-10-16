First we create two mp3 files using sox

  $ sox -n one_note.mp3 synth 5 sin 347
  $ sox -n two_notes.mp3 synth 5 sin 347 sin 354

Now, we tag them by pattern match
  $ usiq --pattern="<artist>_<title>" tag *.mp3
  .*INFO.*Setting tags {'(artist|title)': '(note|one)', '(artist|title)': '(one|note)'} on file one_note.mp3 (re)
  .*INFO.*Setting tags {'(artist|title)': '(notes|two)', '(artist|title)': '(two|notes)'} on file two_notes.mp3 (re)

Change artist using command line option
  $ usiq --artist="Any Artist" tag *.mp3
  .*INFO.*Setting tags {'artist': 'Any Artist'} on file one_note.mp3 (re)
  .*INFO.*Setting tags {'artist': 'Any Artist'} on file two_notes.mp3 (re)

Rename by pattern
  $ usiq --pattern="<artist.upper> - <title.upper>" rename *.mp3
  .*INFO.*Moving one_note.mp3 -> ANY ARTIST - NOTE.mp3 (re)
  .*INFO.*Moving two_notes.mp3 -> ANY ARTIST - NOTES.mp3 (re)

Show information
  $ usiq show "ANY ARTIST - NOTE.mp3"
  .*INFO.*{.*'artist': 'Any Artist'.*} (re)

Check that ls also gives the right pattern
  $ ls
  ANY ARTIST - NOTE.mp3
  ANY ARTIST - NOTES.mp3
