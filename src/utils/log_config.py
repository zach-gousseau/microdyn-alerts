# log_config.py
import logging

def setup_logger(name: str):
    # create and configure the logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(name)
