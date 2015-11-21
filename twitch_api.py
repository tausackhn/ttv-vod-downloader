# coding=utf-8
__author__ = 'Kirill'

import urllib.request
import urllib.error
import json
import os
import re
import sys
from queue import Queue
from urllib.parse import urljoin
from time import sleep

import m3u8

from async_loader import DownloadManager
from content_handler import PartHandler, ConsoleWriter


class TwitchAPI:
    """ Static class for Twitch API constants """
    API_DOMAIN = 'https://api.twitch.tv'
    KRAKEN = '/kraken'
    API = '/api'
    USHER_DOMAIN = 'http://usher.twitch.tv'
    HLS_DOMAIN = 'https://vod.ak.hls.ttvnw.net/v1/AUTH_system'


class Broadcast(object):
    """ A class represents twitch vod """

    def __init__(self, vod_id, json_info):
        self.vod_id = vod_id
        self.json_info = json_info
        self.chunks = None

    def take_chunks(self):
        token_url = (TwitchAPI.API_DOMAIN +
                     TwitchAPI.API +
                     '/vods/' + self.vod_id + '/access_token')
        with urllib.request.urlopen(token_url) as response:
            token_json = json.loads(response.read().decode('utf-8'))
        quality_playlist_url = (TwitchAPI.USHER_DOMAIN +
                                '/vod/' + self.vod_id +
                                '?nauthsig=' + token_json['sig'] +
                                '&nauth=' + token_json['token'] +
                                '&allow_source=true')
        variant_playlist = m3u8.load(quality_playlist_url)
        try:
            source_playlist_url = next(i.uri for i in variant_playlist.playlists if i.media[0].group_id == 'chunked')
        except StopIteration:
            print('Source(Chunked) playlist have not found.')
            sys.exit(0)
        chunks_m3u8 = m3u8.load(source_playlist_url)
        chunks_rel_path = chunks_m3u8.segments.uri
        self.chunks = list(map(lambda x: urljoin(source_playlist_url, x), chunks_rel_path))


def download_vods(broadcasts, num_threads, resume=False, max_cache_size=100):
    """ Download broadcasts from list with Broadcast objects
    :param broadcasts: list of Broadcast objects
    :type broadcasts: list
    """
    url_queue = Queue()
    response_queue = Queue()
    dm = DownloadManager(url_queue=url_queue,
                         data_queue=response_queue,
                         max_threads=num_threads)
    part_handler = PartHandler(download_manager=dm,
                               data_queue=response_queue,
                               max_cache_size=max_cache_size)
    view = ConsoleWriter(part_handler)
    dm.start()
    part_handler.start()
    view.start()

    for vod in broadcasts:
        print('Broadcast v%s downloading has been started.' % vod.vod_id)
        directory = vod.json_info['channel']['name'] + '\\' + str(vod.vod_id)
        os.makedirs(directory, exist_ok=True)
        os.chdir(directory)
        if resume and os.path.exists('_finished'):
            os.chdir('..\\..')
            print('Broadcast v%s already downloaded!' % vod.vod_id)
            continue
        create_info(vod)
        vod.take_chunks()
        part_handler.set_output(str(vod.vod_id) + '.ts')
        part_handler.set_sorted_parts(vod.chunks)
        for url in vod.chunks:
            url_queue.put(url)
        while not url_queue.empty():
            sleep(0.1)
        url_queue.join()
        while not response_queue.empty():
            sleep(0.1)
        response_queue.join()
        open('_finished', 'w').close()
        print('\nBroadcast v%s downloading finished.' % vod.vod_id)
        os.chdir('..\\..')


def take_broadcasts(channel):
    """ Get list of past broadcasts
    :param channel: channel name
    :type channel: str
    :return: list of ids
    :rtype: list
    """
    broadcasts_url = (TwitchAPI.API_DOMAIN +
                      TwitchAPI.KRAKEN +
                      '/channels/' +
                      channel +
                      '/videos?broadcasts=true')
    broadcasts = []
    try:
        with urllib.request.urlopen(broadcasts_url) as response:
            broadcasts_json = json.loads(response.read().decode('utf-8'))
        while len(broadcasts_json['videos']) > 0:
            for vod in broadcasts_json['videos']:
                broadcasts.append(Broadcast(vod['_id'].strip('v'), vod))
            broadcasts_url = broadcasts_json['_links']['next']
            with urllib.request.urlopen(broadcasts_url) as response:
                broadcasts_json = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError:
        print('Incorrect channel name.')
        sys.exit(1)
    broadcasts.reverse()  # oldest must be downloaded first
    return broadcasts


def download_ids(id_list, num_threads, resume=False, max_cache_size=100):
    """ Download broadcasts from list with ids
    :param id_list: list with broadcast ids
    :type id_list: list
    """
    download_vods([id_to_broadcast(vod_id) for vod_id in id_list], num_threads, resume, max_cache_size)


def download_all(channel, num_threads, resume=False, max_cache_size=100):
    """ Download available broadcasts from channel
    :param channel: channel name
    :type channel: str
    """
    download_vods(take_broadcasts(channel), num_threads, resume, max_cache_size)


def id_to_broadcast(vod_id):
    """ Return Broadcast object from id
    :param vod_id: a broadcast id
    :type vod_id: int
    """
    broadcast_url = (TwitchAPI.API_DOMAIN +
                     TwitchAPI.KRAKEN +
                     '/videos/v' +
                     str(vod_id))
    try:
        with urllib.request.urlopen(broadcast_url) as response:
            broadcast_json = json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError:
        print('Incorrect broadcast url.')
        sys.exit(1)
    return Broadcast(broadcast_json['_id'].strip('v'), broadcast_json)


def create_info(vod):
    """ Creating info file about broadcast
    :param vod: broadcast
    :type vod: Broadcast
    """
    file = open('info.txt', mode='w')
    file.write(json.dumps(vod.json_info))
    file.close()


def parse_twitch_url(url):
    match = re.search('https?://(?:www.)?twitch.tv/(?P<channel_name>\w+)/(?P<type>\D{1})/(?P<id>\d+)', url,
                      flags=re.IGNORECASE)
    info = None
    if match:
        info = {'channel_name': match.group('channel_name'),
                'type': match.group('type'),
                'id': int(match.group('id'))}
    return info
