from song import Song, urlify, pathify
import player
import time
import threading

class Queue:
    queue = []
    position = -1

    def get_queue(self):
        dict_queue = [media.dictify() for media in self.queue]
        obj = {'queue': dict_queue}
        if self.is_valid_position(self.position) and \
                self.queue[self.position] == player.now_playing:
            obj['position'] = self.position
        return obj

    def add(self, media):
        self.queue.append(media)
        return self.get_queue()

    def remove(self, pos):
        if self.is_valid_position(pos):
            del self.queue[pos]
            if self.position > pos:
                self.position -= 1
            elif self.position == pos:
                player.stop()
        return self.get_queue()

    def clear(self):
        self.queue = []
        self.position = -1
        player.stop()
        return self.get_queue()

    def now_playing(self):
        obj = {'player_status': player.get_status()}
        if player.now_playing:
            obj['song'] = player.now_playing.dictify()
        return obj

    def set_position(self, pos):
        if self.is_valid_position(pos):
            self.position = pos
            player.play_media(self.queue[self.position])
            return self.queue[self.position].dictify()

    def play_next(self, force=False):
        if player.play_subitem():
            return self.queue[self.position].dictify()
        if self.has_next():
            return self.set_position(self.position + 1)
        if force and self.is_valid_position(0):
            return self.set_position(0)

    def is_valid_position(self, pos):
        return 0 <= pos < len(self.queue)

    def has_next(self):
        return self.is_valid_position(self.position + 1)

    def autoplay_thread(self):
        while True:
            if player.has_ended() and \
                    (self.has_next() or player.is_youtube_video()):
                self.play_next()
            time.sleep(0.25)

    def start_autoplay(self):
        t = threading.Thread(target=self.autoplay_thread)
        t.daemon = True
        t.start()
