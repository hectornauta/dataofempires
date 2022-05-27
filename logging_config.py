import logging

def configure_logging(module):
    logging.basicConfig(
        level=logging.CRITICAL,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(f'logs/{module}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()
