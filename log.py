import logging, os, time
from colorlog import ColoredFormatter

def is_file_older_than_x_days(file, days=1): 
    file_time = os.path.getmtime(file)
    return ((time.time() - file_time) / 3600 > 24*days)
    
class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    FORMATS = {
        logging.ERROR: "%(levelname)-8s | %(msg)s [%(module)s, line  %(lineno)d]",
        logging.WARNING: "%(levelname)-8s | %(msg)s [%(module)s, line  %(lineno)d]",
        logging.CRITICAL: "%(levelname)-8s | %(msg)s [%(module)s, line %(lineno)d]",
        logging.DEBUG: "%(levelname)-8s | %(msg)s [%(module)s, line  %(lineno)d]",
        "DEFAULT": "%(levelname)-8s | %(msg)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        formatter = ColoredFormatter(log_fmt)
        return formatter.format(record)

LOG_LEVEL = logging.INFO
logging.root.setLevel(LOG_LEVEL)


