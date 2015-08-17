# coding=utf-8
from distutils.core import setup
import sys
# noinspection PyUnresolvedReferences
import py2exe


class Target(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = '1.0.0.0'


sys.argv.append('py2exe')

App_Target = Target(
    script='ttv-vod-downloader.py',
    dest_base='twitch-vod-downloader',
    name='Twitch broadcast downloader',
    description='Async broadcast downloader for new hls format.'
)

setup(
    name='Twitch',
    console=[App_Target],
    options={'py2exe': {'bundle_files': 1, 'compressed': True, 'optimize': 2}},
    zipfile=None, requires=['py2exe', 'm3u8']
)
