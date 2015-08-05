# coding=utf-8
__author__ = 'Kirill'

from threading import Thread
import math

from observers import Observer, Observable


class PartHandler(Observable, Thread):
    """ Thread which handle downloaded parts of broadcast """

    def __init__(self, download_manager, data_queue, max_cache_size, output_file=None, sorted_chunks=None):
        super(PartHandler, self).__init__()
        Thread.__init__(self)
        if not sorted_chunks:
            sorted_chunks = []
        self.setDaemon(True)

        self.download_manager = download_manager
        self.data_queue = data_queue
        self.output_file = output_file
        self.sorted_chunks = sorted_chunks
        self.max_cache_size = max_cache_size

        self.num_chunks = len(sorted_chunks)
        self.num_chunks_done = 0
        self.chunks_data = [0] * self.num_chunks
        self.chunk_size = 920360  # approximate size of 1 chunk
        self.cache_size = 0

    def run(self):
        while True:
            content = self.data_queue.get()
            index = self.sorted_chunks.index(content['url'])
            self.chunks_data[index] = content['data']
            self.num_chunks_done += 1
            self.cache_size += 1
            self.chunk_size += (len(content['data']) - self.chunk_size) / self.num_chunks_done
            self.notify_observers(chunk_size=self.chunk_size,
                                  num_chunks=self.num_chunks,
                                  num_chunks_done=self.num_chunks_done)
            self.data_queue.task_done()

            if self.cache_size > self.max_cache_size:
                self.download_manager.pause()

            if index == 0:
                while len(self.chunks_data) > 0 and self.chunks_data[0] != 0:
                    self.output_file.write(self.chunks_data.pop(0))
                    self.sorted_chunks.pop(0)
                    self.cache_size -= 1
                self.output_file.flush()
                self.download_manager.resume()

    def set_output(self, path):
        """ Changing output broadcast file
        :param path: file path
        :type path: str
        """
        if self.output_file:
            self.output_file.close()
        self.output_file = open(path, 'wb')

    def set_sorted_parts(self, parts):
        self.sorted_chunks = parts
        self.num_chunks = len(parts)
        self.chunks_data = [0] * self.num_chunks
        self.num_chunks_done = 0
        self.cache_size = 0


class ConsoleWriter(Observer, Thread):
    def __init__(self, observable):
        super().__init__(observable)
        Thread.__init__(self)
        self.setDaemon(True)

    def notify(self, observable, *args, **kwargs):
        num_chunks_done = kwargs['num_chunks_done']
        num_chunks = kwargs['num_chunks']
        chunk_size = kwargs['chunk_size']

        num_signs = math.floor(20 * num_chunks_done / num_chunks)
        done_percent = 100 * num_chunks_done / num_chunks
        file_size = chunk_size * num_chunks / 1024 / 1024 / 1024
        file_size_done = chunk_size * num_chunks_done / 1024 / 1024 / 1024

        info_str = ('\r{:6.2f}%  ['.format(done_percent) +
                    '#' * num_signs +
                    ' ' * (20 - num_signs) +
                    '] {:4.1f}/{:4.1f}GB'.format(file_size_done, file_size) +
                    '    Press Ctrl+C to exit.')
        print(info_str, end='')

    def run(self):
        while True:
            pass
