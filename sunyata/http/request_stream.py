class RequestStream(object):

    def __init__(self, reader, writer, bufsize = 1024 * 1024):
        self.reader = reader
        self.writer = writer
        self.bufsize = bufsize
