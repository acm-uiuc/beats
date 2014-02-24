acoustics
=========

New Acoustics Media Player for ACM@UIUC.

Setup
-----

First, [install and start MongoDB](http://docs.mongodb.org/manual/installation/).

Set up a virtual Python environment for this project.

    virtualenv venv
    source venv/bin/activate

Then install all the Python dependencies.

    pip install -r requirements.txt

Now you're ready to start the Acoustics server.

    python acoustics/main.py
