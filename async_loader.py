# coding=utf-8
__author__ = 'Kirill'

from threading import Thread
import urllib.request
from http.client import IncompleteRead


class DownloadingThread(Thread):
    """ Threaded url download """
    def __init__(self, url_queue, data_queue):
        super(DownloadingThread, self).__init__()
        self.url_queue = url_queue
        self.data_queue = data_queue
        self.daemon = True

    def run(self):
        while True:
            url = self.url_queue.get()
            while True:
                try:
                    self.download_url(url)
                except IncompleteRead:
                    continue
                except Exception as error:
                    print("\rUnexpected error: %s with args: %s" % (error, error.args))
                break
            self.url_queue.task_done()

    def download_url(self, url):
        with urllib.request.urlopen(url) as response:
            self.data_queue.put({'url': response.geturl(), 'data': response.read()})


class DownloadManager:
    """ A simple DownloadingThread pool """
    def __init__(self, url_queue, data_queue, max_threads=4):
        self.url_queue = url_queue
        self.data_queue = data_queue
        self.max_threads = max_threads

    def start(self):
        for i in range(self.max_threads):
            thread = DownloadingThread(self.url_queue, self.data_queue)
            thread.setDaemon(True)
            thread.start()
