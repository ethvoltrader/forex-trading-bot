"""
Logging Configuration for Forex Trading Bot
Creates organized logs with timestamps, levels, and file storage
"""

import logging
import os
from datetime import datetime


def setup_logger(name='ForexBot', log_file=None, console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Set up logging configuration for the trading bot.
    
    Args:
        name (str): Logger name (default: 'ForexBot')
        log_file (str): Path to log file (default: auto-generated with timestamp)
        console_level: Logging level for console output (default: INFO)
        file_level: Logging level for file output (default: DEBUG)
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        >>> logger = setup_logger('ForexBot')
        >>> logger.info("Bot started")
        >>> logger.debug("Detailed debug info")
        >>> logger.error("Something went wrong")
    """
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("✅ Created 'logs' directory")
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture everything, filter at handler level
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler (prints to screen) - Less verbose
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (saves to file) - More detailed
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f'logs/bot_{timestamp}.log'
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Log the initialization
    logger.info(f"Logger initialized - Console: {logging.getLevelName(console_level)}, File: {logging.getLevelName(file_level)}")
    logger.info(f"Log file: {log_file}")
    
    return logger


def get_logger(name='ForexBot'):
    """
    Get an existing logger instance.
    Use this in other modules after calling setup_logger() once.
    
    Args:
        name (str): Logger name
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


# Example usage and testing
if __name__ == "__main__":
    # Test the logger
    print("\n" + "="*70)
    print("TESTING LOGGER CONFIGURATION")
    print("="*70 + "\n")
    
    logger = setup_logger('TestBot')
    
    print("\n--- Testing different log levels ---\n")
    
    logger.debug("This is a DEBUG message - detailed info for developers")
    logger.info("This is an INFO message - normal operations")
    logger.warning("This is a WARNING message - something to watch")
    logger.error("This is an ERROR message - something went wrong")
    logger.critical("This is a CRITICAL message - serious problem!")
    
    print("\n" + "="*70)
    print("✅ Logger test complete! Check the 'logs' folder for the log file.")
    print("="*70 + "\n")
