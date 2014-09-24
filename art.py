from os import splitext, isfile
import mutagen
import hashlib

art_path = "/home/prin/Music/theArt/"

def index_art(path):
    ext = splitext(path)

    art_uri = ""
    if ext == ".mp3":
        art_uri = index_mp3_art(path)
    elif ext == ".flac":
        art_uri = index_flac_art(path)
    
    return art_uri

def index_mp3_art(song):
    try:
        tags = mutagen.mp3.Open(song)
    except:
        return False
    art = ""
    for tag in tags:
        if tag.startswith("APIC"):
            data = tags[tag].data
            break

    path = write_art(data)

    return path

def index_flac_art(song):
    try:
        tags = mutagen.flac.Open(song)
    except:
        return False
    if tags.pictures[0].data:
        data = tags.pictures[0].data

    path = write_art(data)

    return path

def write_art(data):
    if not data:
        return None

    filename = song.md5_for_file(data) + ".jpg"

    if not isfile(art_path + filename):
        out = open(art_path + filename, "w")
        out.write(data)
        out.close()
        print "indexed " + filename

    return art_path + filename

def md5_for_file(f, block_size=2**20):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()
