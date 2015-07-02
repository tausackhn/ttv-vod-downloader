__author__ = 'Kirill'

from threading import Thread
import urllib.request


class DownloadingThread(Thread):
        def __init__(self, url_queue, data_queue):
                super(DownloadingThread, self).__init__()
                self.url_queue = url_queue
                self.data_queue = data_queue
                self.daemon = True

        def run(self):
                while True:
                        url = self.url_queue.get()
                        try:
                                self.download_url(url)
                        except Exception as exc:
                                print('%s generated an exception %s' % (url, exc))
                        self.url_queue.task_done()

        def download_url(self, url):
                # print('Downloading %s at thread #%s' % (url, self.ident))
                with urllib.request.urlopen(url) as response:
                        self.data_queue.put(response.read())


class DownloadManager:
        def __init__(self, url_queue, data_queue, max_threads=4):
                self.url_queue = url_queue
                self.data_queue = data_queue
                self.max_threads = max_threads

        def start(self):
                for i in range(self.max_threads):
                        thread = DownloadingThread(self.url_queue, self.data_queue)
                        thread.start()
