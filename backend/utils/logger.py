import logging

def setup_logger(name, level=logging.INFO):
    """Setup a logger with a specified name and log level."""
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

# Example usage
logger = setup_logger("SurvivorSoulRPG")
logger.info("Logger is set up")