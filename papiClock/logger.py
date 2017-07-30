import logging

class Logger():

    def __init__(self, name, level="INFO"):
        self.logger = logging.getLogger(name)
        if level == "DEBUG":
            level = logging.DEBUG
        else:
            level = logging.INFO
        self.logger.setLevel(level)
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - [%(filename)s:%(lineno)d]> %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        self.handlers = [console_handler]

    def verbose(self, verbosity=0):
        for handler in self.handlers:
            if verbosity == 0:
                handler.setLevel(logging.ERROR)
            if verbosity == 1:
                handler.setLevel(logging.INFO)
            if verbosity == 2:
                handler.setLevel(logging.DEBUG)
        if verbosity == 0:
            self.logger.setLevel(logging.ERROR)
        if verbosity == 1:
            self.logger.setLevel(logging.INFO)
        if verbosity == 2:
            self.logger.setLevel(logging.DEBUG)

# ==============================================================================
LOGGER = None

def getLogger():
    global LOGGER
    if not LOGGER:
        LOGGER = Logger('papiclock')
    return LOGGER
