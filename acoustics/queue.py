from song import get_song, urlify, pathify
import player
from time import sleep

class Queue:
    queue = []
    position = -1

    def get_queue(self):
        return {'queue': self.queue}

    def add(self, song_id):
        self.queue.append(get_song(song_id))
        return self.get_queue()

    def clear(self):
        self.queue = []
        return self.get_queue()

    def now_playing(self):
        return {'position': self.position, 'song': player.now_playing, 'player_status': player.get_status()}


    def set_position(self, pos):
        if self.is_valid_position(pos):
            self.position = pos
            player.play_song(self.queue[self.position])
            return self.queue[self.position]

    def play_next(self, force=False):
        if self.has_next():
            return self.set_position(self.position + 1)
        if force and self.is_valid_position(0):
            return self.set_position(0)

    def is_valid_position(self, pos):
        return 0 <= pos < len(self.queue)

    def has_next(self):
        return self.is_valid_position(self.position + 1)
