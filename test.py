__author__ = 'Kirill'

from async_loader import DownloadManager as Downloader
from queue import Queue
from twitch_api import take_broadcasts
import content_handler as ch


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

    manager = Downloader(queue, out_queue, 10)
    manager.start()

    for url in urls:
        queue.put(url)

    handler = ch.PartHandler(out_queue)
    handler.start()

    queue.join()
    out_queue.join()


def api_test():
    blist = take_broadcasts('guit88man')
    for b in blist:
        print(b.title)


loader_test()
