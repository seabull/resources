from os import path

import yaml
import logging.config
from typing import List

from log_config import handlers

#config_file=path.join(path.dirname(path.abspath(__file__)), 'logging_config.yaml')

def log_init(config_file: str, log_level: int = logging.WARNING, loggers: List = None) -> None:
    with open(config_file, 'r') as conf:
        try:
            logging_config = yaml.load(stream=conf, Loader=yaml.SafeLoader)
        except yaml.YAMLError as e:
            print(f"Error loading logger config {e}")
    
    logging.config.dictConfig(logging_config)
    if loggers is None:
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]

    for log in loggers:
        log.setLevel(log_level)

#log_init(config_file)


# Set the logging level for all loggers in scope
# This level can be overwritten by the following in a file
#   logger = logging.getlogger(__name__)
#   logger.setLevel(logging.INFO)
#loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
#for log in loggers:
#  log.setLevel(log_level)
