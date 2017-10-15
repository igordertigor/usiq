# Usiq makes keeping your music library very simple.

I really like [beets](http://beets.io/). I love the beets philosophy to
automatically keep tags and filenames in sync. That was a gamechanger in
the way I deal with electronic music. Unfortunately, beets is a bit too
much for my taste.
- It always tries to fetch the "correct" tags from musicbrainz, but most
  of my music is sufficiently uncommon that these sources don't know about
  it.
- It keeps a database of all your files and their tags and is by that
  everything but stateless. This is particularly inconvenient if you
  forgot to tag your music correctly when you imported it and beets
  afterwards overwrites your corrected tags by its internal state.
- When searching for music, beets doesn't really play at its best and is
  very slow.

Usiq adopts beets' philosophy to use software to synchronize tags and
filenames both ways, but it does not come with the overhead of online
lookups and statefulness. Instead usiq, does nothing but really
synchronize tags and filenames. If you want to play your music, you need
something else (for example I started moving from beets to developing usiq
when I discovered [cmus](https://cmus.github.io/), which to me seems like
the best music player ever developed (if your tags are in order).

Note that usiq is currently under heavy development and a lot of features
may be quite unstable.

## Installation

Should be as easy as

    pip install usiq

Alternatively, you can install usiq from source (I wouldn't know why).
Usiq is built using [pybuilder](http://pybuilder.github.io/) and
installation should be as simple as

    pyb install

## Basic usage

Help can be found by typing

    usiq -h

In short, usiq adopts a command-action pattern to cover different use
cases. So

    usiq show <FILENAME>

would for example show the tags for a given file.

## Usage examples


### Rename mp3 files to match tags

This example assumes that you have a couple of mp3 files lying around that
you want to move to a location based on their tags

    usiq --pattern="$HOME/Music/<albumartist>/<album>/<artist>_-_<title>" rename *.mp3

You can add formatting for filenames (e.g. if you for example your target
filesystem is not case sensitive) by using format specifiers

    usiq --pattern="<artist.upper>_-_<title.upper>" rename *.mp3

### Interactive editing of files in the current folder

This exports the tags from the current folder to a yaml file, opens your
configured editor on the yaml file and when you close, it uses the yaml
file to change the tags of all selected files

    usiq -o - export *.mp3 | vipe - | usiq -i - tag *.mp3

Note that this example makes use of
[vipe](https://github.com/juliangruber/vipe/blob/master/vipe.sh) for
interactive stream editing.
