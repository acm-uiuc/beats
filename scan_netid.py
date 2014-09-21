#!/usr/bin/env python
# Command line script to add songs in a user's music directory.
# To be run from a production Beats server only.
import sys

if len(sys.argv) == 1:
    print 'Usage: ./scan_netid.py netid1 [netid2 netid3 ...]'
    sys.exit(1)

import song
for netid in sys.argv[1:]:
    song.add_songs_in_dir('/music/' + netid)
