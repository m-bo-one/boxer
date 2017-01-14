import os
import sys
import hashlib
import logging.config
import uuid
import time

import yaml
import gevent

from PIL import Image

from conf import settings


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def enum_names(enum, ignore=None):
    if ignore is None:
        ignore = []
    return [prop.name for prop in enum if prop.name not in ignore]


def generate_token():
    return hashlib.md5(uuid.uuid4().hex + str(time.time())).hexdigest()


def generate_temp_password(password, secret_key=settings.SECRET_KEY):
    return hashlib.md5("".join([password, secret_key])).hexdigest()


def check_temp_password(password, hashed):
    return bool(generate_temp_password(password) == hashed)


def enum_convert(enum_type, search_type):
    enums = (prop for prop in dir(enum_type)
             if not prop.startswith('_') and not
             prop.startswith('__'))
    for cls_enum in enums:
        if getattr(enum_type, cls_enum) == search_type:
            return cls_enum.lower()


def decode_enum(enum_type, search_str):
    enums = (prop for prop in dir(enum_type)
             if not prop.startswith('_') and not
             prop.startswith('__'))
    for cls_enum in enums:
        if cls_enum.lower() == search_str.lower():
            return getattr(enum_type, cls_enum)
    else:
        return 0


def setup_logging(default_path='logging.yaml',
                  default_level=logging.INFO,
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
        logging.getLogger().setLevel(default_level)
    else:
        logging.basicConfig(level=default_level)


def await_greenlet(func, *args, **kwargs):
    thread = gevent.spawn(func, *args, **kwargs)
    return thread.get()


def get_image(image_name, root_path=settings.ASSETS_PATH, with_close=True):
    image = Image.open(os.path.join(root_path, image_name))
    if with_close:
        image.close()
    return image


def clear_dir(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)

        except Exception as e:
            print(e)
