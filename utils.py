import os
import sys
import logging.config

import yaml
import gevent

from PIL import Image

from conf import settings


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def setup_logging(default_path='conf/logging.yaml', default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def await_greenlet(func, *args, **kwargs):
    thread = gevent.spawn(func, *args, **kwargs)
    return thread.get()


def get_image(image_name, root_path=settings.MEDIA_PATH, with_close=True):
    image = Image.open(os.path.join(root_path, image_name))
    if with_close:
        image.close()
    return image
