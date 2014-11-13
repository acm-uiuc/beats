#!/usr/bin/env python
# Scan all songs in /music directory.
# To be run from a production Beats server only.
import song
song.add_songs_in_dir('/music')
