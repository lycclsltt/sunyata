from threading import Thread

class Concurrent(object):

    thlist = []

    @classmethod
    def go(cls, target, *args, **kwargs):
        print(target)
        print(args)
        print(kwargs)
        th = Thread(target=target, args=args, kwargs=kwargs)
        cls.thlist.append(th)
        th.start()