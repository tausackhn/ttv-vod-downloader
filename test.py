__author__ = 'Kirill'

from async_loader import DownloadManager as Downloader
from queue import Queue
from twitch_api import take_broadcasts


def loader_test():
    urls = ['https://api.twitch.tv/kraken/videos/v6216180',
            'https://api.twitch.tv/kraken/videos/v6216484',
            'https://api.twitch.tv/kraken/videos/v6273114',
            'https://api.twitch.tv/kraken/videos/v6320418',
            'https://api.twitch.tv/kraken/videos/v6326713',
            'https://api.twitch.tv/kraken/videos/v6363749',
            'https://api.twitch.tv/kraken/videos/v6395236',
            'https://api.twitch.tv/kraken/videos/v6469438',
            'https://api.twitch.tv/kraken/videos/v6549940',
            'https://api.twitch.tv/kraken/videos/v6627227', ]
    queue = Queue()
    out_queue = Queue()
    for url in urls:
        queue.put(url)

    manager = Downloader(queue, out_queue, 10)
    manager.start()

    while True:
        try:
            data = out_queue.get()
            print('Downloaded %s' % data.decode('utf-8')[0:40])
        except Exception as exc:
            print('  Error: %s' % exc)


def api_test():
    blist = take_broadcasts('guit88man')
    for b in blist:
        print(b.title)

api_test()
