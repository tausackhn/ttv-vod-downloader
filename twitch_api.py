__author__ = 'Kirill'

import urllib.request
import json


class TwitchAPI:
    API_DOMAIN = 'https://api.twitch.tv'
    KRAKEN = '/kraken'
    API = '/api'
    USHER_DOMAIN = 'https://usher.twitch.tv'
    HLS_DOMAIN = 'https://vod.ak.hls.ttvnw.net/v1/AUTH_system'


class Broadcast:
    def __init__(self, title, vod_id, date, game, length, url, channel):
        self.title = title
        self.id = vod_id
        self.date = date
        self.game = game
        self.length = length
        self.url = url
        self.channel = channel
        self.parts = []

        # def take_parts(self):


def take_broadcasts(channel):
    broadcasts_url = (TwitchAPI.API_DOMAIN +
                      TwitchAPI.KRAKEN +
                      '/channels/' +
                      channel +
                      '/videos?broadcasts=true')
    with urllib.request.urlopen(broadcasts_url) as response:
        broadcasts_json = json.loads(response.read().decode('utf-8'))
    broadcasts = []
    while broadcasts_json['videos'].__len__() > 0:
        for vod in broadcasts_json['videos']:
            broadcasts.append(Broadcast(vod['title'],
                                        vod['_id'],
                                        vod['recorded_at'],
                                        vod['game'],
                                        vod['length'],
                                        vod['url'],
                                        vod['channel']['name']
                                        )
                              )
        broadcasts_url = broadcasts_json['_links']['next']
        with urllib.request.urlopen(broadcasts_url) as response:
            broadcasts_json = json.loads(response.read().decode('utf-8'))
    return broadcasts
