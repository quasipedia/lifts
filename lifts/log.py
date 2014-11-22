import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)-8s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %03d',
    level=logging.INFO)
log = logging.getLogger('lifts')