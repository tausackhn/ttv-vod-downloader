# coding=utf-8
__author__ = 'Kirill'

import urllib.request
import json
import os
from queue import Queue
from urllib.parse import urljoin

import m3u8
from async_loader import DownloadManager
from content_handler import PartHandler


class TwitchAPI:
    """ Static class for Twitch API constants """
    API_DOMAIN = 'https://api.twitch.tv'
    KRAKEN = '/kraken'
    API = '/api'
    USHER_DOMAIN = 'http://usher.twitch.tv'
    HLS_DOMAIN = 'https://vod.ak.hls.ttvnw.net/v1/AUTH_system'


class Broadcast:
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
        playlists_url = (TwitchAPI.USHER_DOMAIN +
                         '/vod/' + self.vod_id +
                         '?nauthsig=' + token_json['sig'] +
                         '&nauth=' + token_json['token'] +
                         '&allow_source=true')
        with urllib.request.urlopen(playlists_url) as response:
            variant_playlist = response.readlines()
        source_playlist_url = variant_playlist[3].decode('ASCII')  # source video
        m3u8_list = m3u8.load(source_playlist_url)
        chunks_rel_path = m3u8_list.segments.uri
        self.chunks = list(map(lambda x: urljoin(source_playlist_url, x), chunks_rel_path))


def download_vods(broadcasts, num_threads, resume=False):
    """ Download broadcasts from list with Broadcast objects
    :param broadcasts: list of Broadcast objects
    :type broadcasts: list
    """
    url_queue = Queue()
    response_queue = Queue()
    dm = DownloadManager(url_queue, response_queue, num_threads)
    part_handler = PartHandler(response_queue)
    dm.start()
    part_handler.start()

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
        url_queue.join()
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
    with urllib.request.urlopen(broadcasts_url) as response:
        broadcasts_json = json.loads(response.read().decode('utf-8'))
    broadcasts = []
    while len(broadcasts_json['videos']) > 0:
        for vod in broadcasts_json['videos']:
            broadcasts.append(Broadcast(vod['_id'].strip('v'), vod))
        broadcasts_url = broadcasts_json['_links']['next']
        with urllib.request.urlopen(broadcasts_url) as response:
            broadcasts_json = json.loads(response.read().decode('utf-8'))
    return broadcasts.reverse()  # oldest must be downloaded first


def download_ids(id_list, num_threads, resume=False):
    """ Download broadcasts from list with ids
    :param id_list: list with broadcast ids
    :type id_list: list
    """
    download_vods([id_to_broadcast(vod_id) for vod_id in id_list], num_threads, resume)


def download_all(channel, num_threads, resume=False):
    """ Download available broadcasts from channel
    :param channel: channel name
    :type channel: str
    """
    download_vods(take_broadcasts(channel), num_threads, resume)


def id_to_broadcast(vod_id):
    """ Return Broadcast object from id
    :param vod_id: a broadcast id
    :type vod_id: int
    """
    broadcast_url = (TwitchAPI.API_DOMAIN +
                     TwitchAPI.KRAKEN +
                     '/videos/v' +
                     str(vod_id))
    with urllib.request.urlopen(broadcast_url) as response:
        broadcast_json = json.loads(response.read().decode('utf-8'))
    return Broadcast(broadcast_json['_id'].strip('v'), broadcast_json)


def create_info(vod):
    """ Creating info file about broadcast
    :param vod: broadcast
    :type vod: Broadcast
    """
    file = open('info.txt', mode='w')
    file.write(json.dumps(vod.json_info))
    file.close()
