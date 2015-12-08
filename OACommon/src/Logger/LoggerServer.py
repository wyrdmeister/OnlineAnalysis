# -*- coding: utf-8 -*-
"""
LoggerServer

A UDP server that can collect datagrams from logging extension
The server will listen on localhost, port 9999

"""

import errno
import threading
import collections
import SocketServer
import cPickle
import logging
import select


class DequeHandler(logging.Handler):

    """ Store log events as formatted strings in a deque object. """

    def __init__(self, length, level=logging.NOTSET):
        """ Constructor. """
        logging.Handler.__init__(self, level)

        # Create queue
        self.queue = collections.deque(maxlen=length)

        # Init status
        self._status = logging.NOTSET

    def emit(self, record):
        """ Stores a record. """
        self.queue.append(self.format(record))
        if record.levelno > self._status:
            self._status = record.levelno

    def clear(self):
        """ Clear queue. """
        self.queue.clear()
        self._status = logging.NOTSET

    def status(self):
        """ Return status. """
        return self._status

    def pop(self):
        """ Pop an element from the beginning of the queue. """
        try:
            return self.queue.popleft()
        except:
            return None

    def count(self):
        """ Return the length of the queue. """
        return len(self.queue)


class LoggerServerHandler(SocketServer.BaseRequestHandler):

    """ Handler log messages sent via UDP. """

    def handle(self):
        """ Handle datagram. """
        try:
            # Discard first 4 bytes (length of message)
            rec = logging.makeLogRecord(cPickle.loads(self.request[0][4:]))
            self.server.logger.handle(rec)

        except Exception, e:
            self.server.logger.error("Error handling a log message (Error: %s)", e)


class LoggerServer(threading.Thread):

    """ Logger server main class """

    def __init__(self, name=None, level=logging.INFO, filename=None, num=1000):
        """ Constructor. """
        # Parent constructor
        threading.Thread.__init__(self)

        # Create logger UDP server
        self.server = SocketServer.UDPServer(('localhost', 9999), LoggerServerHandler)

        # Init server logger
        self.server.logger = logging.getLogger(name)
        self.server.logger.setLevel(level)
        self.server.logger.handlers = []
        if filename is not None:
            h = logging.FileHandler(filename)
        else:
            h = logging.StreamHandler()
        h.setLevel(level)
        h.setFormatter(logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s:%(message)s', '%b %d, %H:%M:%S'))
        self.server.logger.addHandler(h)

        # Add deque handler
        self.dh = DequeHandler(num)
        self.dh.setLevel(level)
        self.dh.setFormatter(logging.Formatter('[%(asctime)s] %(name)s(%(processName)s):%(levelname)s:%(message)s', '%b %d, %H:%M:%S'))
        self.server.logger.addHandler(self.dh)

    def run(self):
        """ Main entrypoint of logger thread. """
        self.server.logger.info("Starting logging server.")
        while True:
            try:
                self.server.serve_forever()
                break
            except select.error as e:
                if e.args[0] == errno.EINTR:
                    self.server.logger.debug("Logging server listener was interrupted by a syscall. Restarting.")
                else:
                    raise e
        self.server.logger.info("Logging server terminated")

    def resetError(self):
        """ Reset error queue. """
        self.dh.clear()

    def countErrors(self):
        """ Return number of error from last reset. """
        return len(self.dh.queue)

    def getError(self, num):
        """ Return an error from the queue. """
        if num < len(self.dh.queue):
            return self.dh.queue[num]
        else:
            return ''

    def setLevel(self, level):
        """ Set logger level. """
        try:
            level = getattr(logging, level)
        except AttributeError:
            self.server.logger.error("Error setting log level to '%s'.", level)
        else:
            self.server.logger.setLevel(level)
            self.server.logger.handlers[0].setLevel(level)

    def getStatus(self):
        """ Return status of logger (worst event recorded). """
        return self.dh.status()