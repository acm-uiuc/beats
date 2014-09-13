"""
This is an implementation of packet-by-packet Generalized Processor Sharing, as
described in the following paper:

Abhay K. Parekh and Robert G. Gallager. 1993. A generalized processor sharing
approach to flow control in integrated services networks: the single-node case.
IEEE/ACM Trans. Netw. 1, 3 (June 1993), 344-357. DOI=10.1109/90.234856
http://dx.doi.org/10.1109/90.234856
"""

from db import Session, Song, PlayHistory, Packet, Vote
from song import random_songs
from youtube import get_youtube_video_details, YouTubeVideo
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
import threading
import time
import player

SCHEDULER_INTERVAL_SEC = 0.25
"""Interval at which to run the scheduler loop"""


class Scheduler(object):
    virtual_time = 0.0

    active_sessions = 0
    """Number of users with currently queued songs"""

    def __init__(self):
        self._initialize_virtual_time()
        self._update_active_sessions()
        self._update_finish_times()

    def vote_song(self, user, song_id=None, video_url=None):
        """Vote for a song"""
        session = Session()

        if video_url:
            query = session.query(Packet).filter_by(video_url=video_url)
            packet = query.first()
        elif song_id is not None:
            packet = session.query(Packet).filter_by(song_id=song_id).first()
        else:
            raise Exception('Must specify either song_id or video_url')

        if packet:  # Song is already queued; add a vote
            if user == packet.user:
                session.rollback()
                raise Exception('User %s has already voted for this song' %
                                user)
            try:
                packet.additional_votes.append(Vote(user=user))
                session.commit()
            except FlushError:
                session.rollback()
                raise Exception('User %s has already voted for this song' %
                                user)
            self._update_finish_times(packet.user)
        else:  # Song is not queued; queue it
            if video_url:
                if 'www.youtube.com' in video_url:
                    try:
                        video_details = get_youtube_video_details(video_url)
                        packet = Packet(video_url=video_url,
                                        video_title=video_details['title'],
                                        video_length=video_details['length'],
                                        user=user,
                                        arrival_time=self.virtual_time)
                        session.add(packet)
                        session.commit()
                    except Exception, e:
                        session.rollback()
                        raise e
                else:
                    session.rollback()
                    raise Exception('Unsupported website')
            else:
                try:
                    packet = Packet(song_id=song_id,
                                    user=user,
                                    arrival_time=self.virtual_time)
                    session.add(packet)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    raise Exception('Song with id %d does not exist' % song_id)
            self._update_finish_times(user)
            self._update_active_sessions()
        return self.get_queue()

    @staticmethod
    def num_songs_queued():
        """Returns the number of songs that are queued"""
        session = Session()
        num_songs = session.query(Packet).count()
        session.commit()
        return num_songs

    @staticmethod
    def get_queue(user=None):
        """
        Returns the current ordering of songs

        If there is a song currently playing, puts it at the front of the list.
        If user is specified, returns whether or not the user has voted for
        each song.
        """
        session = Session()
        packets = session.query(Packet).order_by(Packet.finish_time).all()
        session.commit()

        queue = []
        for packet in packets:
            if packet.video_url:
                video = YouTubeVideo(packet)
                video_obj = video.dictify()
                video_obj['packet'] = {
                    'num_votes': packet.num_votes(),
                    'user': packet.user,
                    'has_voted': packet.has_voted(user),
                }
                queue.append(video_obj)
            else:
                song = session.query(Song).get(packet.song_id)
                song_obj = song.dictify()
                song_obj['packet'] = {
                    'num_votes': packet.num_votes(),
                    'user': packet.user,
                    'has_voted': packet.has_voted(user),
                }
                queue.append(song_obj)

        # Put now playing song at front of list
        if player.now_playing:
            for i, song in enumerate(queue):
                try:
                    if player.now_playing.id == song['id']:
                        return {'queue': [queue[i]] + queue[:i] + queue[i+1:]}
                except:
                    pass
                try:
                    if player.now_playing.url == song['url']:
                        return {'queue': [queue[i]] + queue[:i] + queue[i+1:]}
                except:
                    pass

        return {'queue': queue}

    def clear(self):
        session = Session()
        session.query(Packet).delete()
        session.commit()
        player.stop()
        return self.get_queue()

    def remove_song(self, song_id, skip=False):
        """Removes the packet with the given id"""
        session = Session()
        packet = session.query(Packet).filter_by(song_id=song_id).first()
        if (isinstance(player.now_playing, Song) and
                player.now_playing.id == song_id):
            player.stop()
            if skip:
                self.virtual_time = packet.finish_time
        session.delete(packet)
        session.commit()
        self._update_active_sessions()
        return self.get_queue()

    def remove_video(self, url, skip=False):
        """Removes the packet with the given video_url"""
        session = Session()
        packet = session.query(Packet).filter_by(video_url=url).first()
        if (isinstance(player.now_playing, YouTubeVideo) and
                player.now_playing.url == url):
            player.stop()
            if skip:
                self.virtual_time = packet.finish_time
        session.delete(packet)
        session.commit()
        self._update_active_sessions()
        return self.get_queue()

    def play_next(self, skip=False):
        if self.empty():
            random_song = random_songs(1)['results']
            if len(random_song) == 1:
                self.vote_song('RANDOM', random_song[0]['id'])

        if not self.empty():
            if player.now_playing:
                if isinstance(player.now_playing, YouTubeVideo):
                    self.remove_video(player.now_playing.url, skip=skip)
                else:
                    self.remove_song(player.now_playing.id, skip=skip)
            session = Session()
            next_packet = (session.query(Packet).order_by(Packet.finish_time)
                           .first())
            if next_packet:
                if next_packet.video_url:
                    video = YouTubeVideo(next_packet)
                    player.play_media(video)
                    session.commit()
                    return video.dictify()
                else:
                    next_song = session.query(Song).get(next_packet.song_id)
                    player.play_media(next_song)
                    next_song.history.append(
                        PlayHistory(user=next_packet.user))
                    session.commit()
                    return next_song.dictify()

    def empty(self):
        """Returns true if there are no queued songs"""
        # If there are no queued songs, there are also no active sessions
        return self.active_sessions == 0

    @staticmethod
    def _update_finish_times(user=None):
        """
        Updates finish times for packets

        If a user is specified, only update given user's queue.
        """
        session = Session()

        if user:
            packets = (session.query(Packet).filter_by(user=user)
                       .order_by(Packet.arrival_time).all())
        else:
            packets = session.query(Packet).order_by(Packet.arrival_time).all()

        last_finish_time = {}
        for packet in packets:
            length = (packet.video_length or
                      session.query(Song).get(packet.song_id).length)
            user = packet.user

            if user in last_finish_time:
                last_finish = max(last_finish_time[user], packet.arrival_time)
                packet.finish_time = last_finish + length / packet.weight()
                last_finish_time[user] = packet.finish_time
            else:
                packet.finish_time = (
                    packet.arrival_time + length / packet.weight())
                last_finish_time[user] = packet.finish_time

        session.commit()

    def _update_active_sessions(self):
        """Updates the active_sessions member variable"""
        session = Session()
        self.active_sessions = session.query(Packet.user).distinct().count()
        session.commit()

    def _initialize_virtual_time(self):
        """Initializes virtual time to the latest packet arrival time"""
        session = Session()
        last_arrived_packet = (session.query(Packet)
                               .order_by(Packet.arrival_time.desc()).first())
        if last_arrived_packet:
            self.virtual_time = last_arrived_packet.arrival_time
        session.commit()

    def _increment_virtual_time(self):
        """Increments the virtual time"""
        if not self.empty():
            self.virtual_time += SCHEDULER_INTERVAL_SEC / self.active_sessions

    def _scheduler_thread(self):
        """Main scheduler loop"""
        while True:
            # print 'Virtual time: %.3f\tActive sessions: %d' % (
            #     self.virtual_time, self.active_sessions)
            if player.has_ended():
                self.play_next()
            self._increment_virtual_time()
            time.sleep(SCHEDULER_INTERVAL_SEC)

    def start(self):
        """Starts the scheduler"""
        thread = threading.Thread(target=self._scheduler_thread)
        thread.daemon = True
        thread.start()

if __name__ == '__main__':
    s = Scheduler()
    s.start()
    if s.empty():
        s.vote_song('klwang3', 1)
        s.vote_song('klwang3', 2)
        s.vote_song('bezault2', 3)
        s.vote_song('bezault2', 2)
    while True:
        if player.now_playing:
            print player.now_playing
        time.sleep(SCHEDULER_INTERVAL_SEC)
