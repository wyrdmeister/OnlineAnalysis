# -*- coding: utf-8 -*-

""" Logger module

This module implements a general purpose logger class based on the logging
module.

"""

import logging
import logging.handlers


class Logger(object):

    """ Logger class
    This class defines a simple general purpose logger on top of the standard
    logging module.

    """

    def __init__(self, name="Default", level=logging.INFO, server=None):
        """ Constructor.
        Accept as optional input parameters the logger name and the logging
        level.
        """
        self._name = name
        self._hname = name + "_handler"
        self._server = server
        self._level = level
        self._init_logger()

    def _init_logger(self):
        """ Initialize the logger object. """
        # Setup logger
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(self._level)

        if len(self._logger.handlers) == 1 and self._logger.handlers[0].name == self._hname:
            return

        if len(self._logger.handlers) > 0:
            self._logger.handlers = []

        # Add handler
        if self._server is not None:
            try:
                (host, port) = self._server.split(':')
                _handler = logging.handlers.DatagramHandler(host, int(port))
            except:
                pass
        else:
            _handler = logging.StreamHandler()
            _handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s:%(message)s'))
        _handler.setLevel(self._level)
        _handler.name = self._hname
        self._logger.addHandler(_handler)

    def __getstate__(self):
        """ Enable the logger object to be pickled. """
        odict = self.__dict__.copy()  # copy the dict since we change it
        del odict['_logger']          # remove logger entry
        return odict

    def __setstate__(self, idict):
        """ Enable the logger object to be unpickled. """
        self.__dict__.update(idict)   # restore dict
        self._init_logger()

    def level(self):
        """ Return current logger level. """
        return self._level()

    def critical(self, msg, *args, **kwargs):
        """ Equivalent to logging.critical """
        if 'exc_info' in kwargs and bool(kwargs['exc_info']) == True and self._logger.level != logging.DEBUG:
            kwargs['exc_info'] = False
        self._logger.log(logging.CRITICAL, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """ Equivalent to logging.error """
        if 'exc_info' in kwargs and bool(kwargs['exc_info']) == True and self._logger.level != logging.DEBUG:
            kwargs['exc_info'] = False
        self._logger.log(logging.ERROR, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """ Equivalent to logging.warning """
        if 'exc_info' in kwargs and bool(kwargs['exc_info']) == True and self._logger.level != logging.DEBUG:
            kwargs['exc_info'] = False
        self._logger.log(logging.WARN, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """ Equivalent to logging.info """
        if 'exc_info' in kwargs and bool(kwargs['exc_info']) == True and self._logger.level != logging.DEBUG:
            kwargs['exc_info'] = False
        self._logger.log(logging.INFO, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """ Equivalent to logging.debug """
        self._logger.log(logging.DEBUG, msg, *args, **kwargs)

    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL