__author__ = 'Kirill'

import urllib.request
import json
import os
from queue import Queue
from async_loader import DownloadManager
from content_handler import PartHandler


class TwitchAPI:
    """ Static class for Twitch API constants """
    API_DOMAIN = 'https://api.twitch.tv'
    KRAKEN = '/kraken'
    API = '/api'
    USHER_DOMAIN = 'https://usher.twitch.tv'
    HLS_DOMAIN = 'https://vod.ak.hls.ttvnw.net/v1/AUTH_system'


class Broadcast:
    """ A class represents twitch vod """

    def __init__(self, vod_id, json_info):
        self.vod_id = vod_id
        self.json_info = json_info
        self.parts = []

    def take_parts(self):
        # TODO implement method. Set self.parts as list of part urls.
        pass


def download_vods(broadcasts, resume=False):
    """ Download broadcasts from list with Broadcast objects
    :param broadcasts: list of Broadcast objects
    :type broadcasts: list
    """
    url_queue = Queue()
    response_queue = Queue()
    dm = DownloadManager(url_queue, response_queue, 10)
    part_handler = PartHandler(response_queue)
    dm.start()
    part_handler.start()

    for vod in broadcasts:
        directory = vod.json_info['channel']['name'] + '\\' + str(vod.vod_id)
        os.makedirs(directory, exist_ok=True)
        os.chdir(directory)
        if resume:
            if os.path.exists('_finished'):
                os.chdir('..\\..')
                continue
        create_info(vod)
        vod.take_parts()
        part_handler.set_output(str(vod.vod_id) + '.ts')
        part_handler.set_sorted_parts(vod.parts)
        # TODO addition part urls to url_queue
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


def download_ids(id_list, resume=False):
    """ Download broadcasts from list with ids
    :param id_list: list with broadcast ids
    :type id_list: list
    """
    download_vods([id_to_broadcast(vod_id) for vod_id in id_list])


def download_all(channel, resume=False):
    """ Download available broadcasts from channel
    :param channel: channel name
    :type channel: str
    """
    download_vods(take_broadcasts(channel), resume)


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
