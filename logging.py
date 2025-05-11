import logging

# Create separate loggers if desired (optional but cleaner)
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # Capture all levels

# Handler for success/info messages
success_handler = logging.FileHandler('success.log')
success_handler.setLevel(logging.INFO)  # Only logs INFO and above, not WARNING or ERROR

# Handler for error messages
error_handler = logging.FileHandler('error.log')
error_handler.setLevel(logging.ERROR)  # Only logs ERROR and CRITICAL

# Formatter (optional but recommended)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
success_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(success_handler)
logger.addHandler(error_handler)

# Example usage
logger.info("This is a successful operation.")  # Goes to success.log
logger.error("This is an error message.")       # Goes to error.log
