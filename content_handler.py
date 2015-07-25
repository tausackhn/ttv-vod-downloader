# coding=utf-8
__author__ = 'Kirill'

from threading import Thread
import math


class PartHandler(Thread):
    """ Downloaded broadcast parts processing thread"""

    def __init__(self, data_queue, output_file=None, sorted_chunks=None):
        if not sorted_chunks:
            sorted_chunks = []
        super(PartHandler, self).__init__()
        self.setDaemon(True)
        self.data_queue = data_queue
        self.output_file = output_file
        self.sorted_chunks = sorted_chunks
        self.num_chunks = len(sorted_chunks)
        self.num_chunks_done = 0
        self.chunks_data = [0] * self.num_chunks
        self.chunk_size = 920360  # approximate size of 1 chunk

    def run(self):
        while True:
            part = self.data_queue.get()
            index = self.sorted_chunks.index(part['url'])
            self.chunks_data[index] = part['data']
            if index == 0:
                while len(self.chunks_data) > 0 and self.chunks_data[0] != 0:
                    data = self.chunks_data.pop(0)
                    self.output_file.write(data)
                    self.output_file.flush()
                    self.sorted_chunks.pop(0)

            self.num_chunks_done += 1
            num_octotorp = math.floor(20 * self.num_chunks_done / self.num_chunks)
            done_percent = 100 * self.num_chunks_done / self.num_chunks
            file_size = self.chunk_size * self.num_chunks / 1024 / 1024 / 1024
            file_size_done = self.chunk_size * self.num_chunks_done / 1024 / 1024 / 1024
            print('\r[' + '#' * num_octotorp + ' ' * (20 - num_octotorp) + '] %4.1f/%4.1fGB  %6.2f' % (
                file_size_done, file_size, done_percent) + '%', end='')
            self.data_queue.task_done()

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
