import logging
import sys

def setup_logging():
    # Log4j style format
    log_format = "%-5p,%d{yyyy-MM-dd HH:mm:ss,SSS} (%t) [%c] %m [%M:%L]%n"
    py_format = "%(levelname)-5s,%(asctime)s.%(msecs)03d (%(threadName)s) [%(name)s] %(message)s [%(funcName)s:%(lineno)d]"

    logging.basicConfig(
        level=logging.INFO,
        format=py_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )