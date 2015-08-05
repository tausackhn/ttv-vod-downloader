# coding=utf-8
__author__ = 'Kirill'

from threading import Thread
import urllib.request
from http.client import IncompleteRead
import urllib.error
import gc


class DownloadingThread(Thread):
    """ Threaded url download """
    def __init__(self, url_queue, data_queue):
        super(DownloadingThread, self).__init__()
        self.url_queue = url_queue
        self.data_queue = data_queue
        self.__running = True

    def run(self):
        while True:
            while self.__running:
                url = self.url_queue.get()
                while True:
                    try:
                        self.download_url(url)
                    except IncompleteRead:
                        continue
                    except MemoryError:
                        gc.collect()
                        continue
                    except urllib.error.HTTPError:
                        continue
                    break
                self.url_queue.task_done()

    def download_url(self, url):
        with urllib.request.urlopen(url) as response:
            self.data_queue.put({'url': response.geturl(), 'data': response.read()})

    def pause(self):
        self.__running = False

    def resume(self):
        self.__running = True


class DownloadManager(object):
    """ A simple DownloadingThread pool """
    def __init__(self, url_queue, data_queue, max_threads=4):
        super().__init__()
        self.url_queue = url_queue
        self.data_queue = data_queue
        self.max_threads = max_threads
        self.threads = [DownloadingThread(self.url_queue, self.data_queue) for _ in range(self.max_threads)]
        for t in self.threads:
            t.setDaemon(True)

    def start(self):
        for t in self.threads:
            t.start()

    def pause(self):
        for t in self.threads:
            t.pause()

    def resume(self):
        for t in self.threads:
            t.resume()
