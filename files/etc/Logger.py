import logging
from logging.handlers import RotatingFileHandler

class Log:

    logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    
    def __init__(self, fileName):
        self.logHandler = RotatingFileHandler(fileName, mode='a', maxBytes=50*1024, backupCount=2, encoding=None, delay=0)
        self.logHandler.setFormatter(self.logFormatter)
        self.logHandler.setLevel(logging.INFO)
        
        self.log = logging.getLogger('root')
        self.log.setLevel(logging.INFO)
        self.log.addHandler(self.logHandler)
        
    def write(self, *args, **kwargs):
        self.log.info(*args, **kwargs)