"""
Logging utility module to set up and configure loggers.
"""
import logging
import sys
import inspect
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")

is_prod = ENVIRONMENT == "prod"

def setup_logger(name: str = None, level: int = logging.INFO if is_prod else logging.DEBUG) -> logging.Logger:
    """Set up and return a configured logger."""
    if name is None:
        # Get the caller's module name
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = module.__name__ if module else "__main__"
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler('server.log')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Default logger instance
logger = setup_logger()