import os
import logging
from logging.handlers import RotatingFileHandler


def _resolve_log_dir() -> str:
    """
    Return a writable log directory.

    On Android/Chaquopy, __file__ resolves to a path *inside* the APK zip
    (e.g. /data/.../base.apk!/src/logger.py) which is read-only.
    We detect Android by checking ANDROID_DATA and use the app's private
    files directory instead.  On desktop we keep the original behaviour.
    """
    android_data = os.environ.get("ANDROID_DATA")
    android_files = os.environ.get("IRIS_FILES_DIR")

    if android_data:

        if android_files:
            log_dir = os.path.join(android_files, "logs")
        else:

            log_dir = os.path.join(android_data, "iris", "logs")
    else:

        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(root, "logs")

    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError:

        import tempfile

        log_dir = tempfile.gettempdir()

    return log_dir


_LOG_DIR = _resolve_log_dir()
_LOG_FILE = os.path.join(_LOG_DIR, "iris.log")


def get_logger(name: str = "Iris", level=logging.DEBUG) -> logging.Logger:

    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        file_handler = RotatingFileHandler(
            _LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2, encoding="utf-8"
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()

        console_formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.propagate = False

    return logger
