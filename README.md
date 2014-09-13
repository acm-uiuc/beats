Beats by ACM
============

New Acoustics Media Player for ACM@UIUC.

Setup
-----

First, install MySQL locally and start it. Create a database for Beats.

Set up a virtual Python environment for this project.

```bash
virtualenv venv
source venv/bin/activate
```

Then install all the Python dependencies.

```bash
pip install -r requirements.txt
```

Initialize the database.

```bash
python db.py
```

Add songs. From the Python interpreter:

```python
import song
song.add_songs_in_dir('/path/to/music')
```

Finally, create a `beats.cfg` file from `beats.cfg.sample` and customize it.

Now you're ready to start the Beats server.

```bash
python main.py
```
