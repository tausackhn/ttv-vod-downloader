# coding=utf-8
__author__ = 'Kirill'


class Observable:
    def __init__(self):
        self.__observers = []

    def add_observer(self, observer):
        self.__observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.notify(self, *args, **kwargs)


class Observer:
    def __init__(self, observable):
        observable.add_observer(self)

    def notify(self, observable, *args, **kwargs):
        pass
