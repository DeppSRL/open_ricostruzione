from logging.handlers import RotatingFileHandler
import logging
import os


class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def _open(self):
        prevumask=os.umask(0o002)
        # os.fdopen(os.open('/path/to/file', os.O_WRONLY, 0600))
        rtv = logging.handlers.RotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv
