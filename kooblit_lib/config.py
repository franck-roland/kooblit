import os
import yaml

__all__ = ["appConfig"]


def get_root_dir():
    ''' Go through the filetree to find the folder with the manage.py
    '''
    parent = os.path.dirname(__file__)
    while 1:
        if os.path.isfile(os.path.join(parent, 'manage.py')):
            break
        parent = os.path.dirname(parent)
    return os.path.abspath(parent)


class Config(object):
    ''' Object Representation of the config file
    '''

    def __init__(self, config_path):
        with open(config_path, "r") as fdesc:
            conf = yaml.load(fdesc.read())

        Config.CONFIG_DICT = conf

    def get(self, key, raise_if_absent=False, default=None, separator="__"):
        ''' Return the value according to the key
        The form of the key is key + separator + sub_key_1 + separator + ...
        ex:
            >>> instance.get(key="toto__tata__titi", separator="__")
            CONFIG_DICT["toto"]["tata"]["titi"]

        You can choose to raise an exception or return a default value if the
        key does not exists
        '''

        sub_keys = key.split(separator)

        val = Config.CONFIG_DICT
        for sub_key in sub_keys:
            try:
                val = val[sub_key]
            except KeyError:
                if raise_if_absent:
                    raise
                else:
                    return default

        return val

appConfig = Config(config_path=os.path.join(get_root_dir(), "config", "config.yml"))
