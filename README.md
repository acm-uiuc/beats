acoustics
=========

New Acoustics Media Player for ACM@UIUC.

Setup
-----

First, install MySQL locally and start it. Create a database for Acoustics.

Set up a virtual Python environment for this project.

    virtualenv venv
    source venv/bin/activate

Then install all the Python dependencies.

    pip install -r requirements.txt

Initialize the database.

    python acoustics/db.py

Add songs. From the Python interpreter (in the acoustics directory):

```python
import song
song.add_songs_in_dir('/path/to/music')
```

Finally, create an `acoustics.cfg` file from `acoustics.cfg.sample` and customize it.

Now you're ready to start the Acoustics server.

    python acoustics/main.py
