import logging

logging_config = {
    "level": logging.INFO,
    "format": "%(asctime)s | [%(levelname)s]: %(message)s"
}

logging.basicConfig(level=logging_config["level"],
                    format=logging_config["format"])
logging.info(f"Logging Level {logging_config['level']} loaded.")
