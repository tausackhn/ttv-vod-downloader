__author__ = 'Kirill'

from threading import Thread


class PartHandler(Thread):
    """ Downloaded broadcast parts processing thread"""
    def __init__(self, data_queue, output_file=''):
        super(PartHandler, self).__init__()
        self.setDaemon(True)
        self.data_queue = data_queue
        self.output_file = output_file

    def run(self):
        while True:
            part = self.data_queue.get()
            print(part['url'])
            self.data_queue.task_done()

    def set_output(self, path):
        """ Changing output broadcast file
        :param path: file path
        :type path: str
        """
        self.output_file = path
        print(path)
