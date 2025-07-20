import os
import shutil
import logging
from ruamel.yaml import YAML

here = os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger(__name__)

def setup_logging(log_level):
    """
    Setup logging
        Verbosity decided on user input
        :param log_level: User defined log level
        :type log_level: str
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        print(
            "\033[91mInvalid log level passed. Please select from debug | info | warning | error\033[0m"
        )
        raise ValueError("{}-Invalid log level.".format(log_level))
    logging.basicConfig(level=numeric_level)

class FileFormatter(logging.Formatter):
    """Class to create a log output which is colored based on level.
    """

    def __init__(self, *args, **kwargs):
        super(FileFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        msg = str(record.msg)
        level_name = str(record.levelname)
        name = str(record.name)
        funcName = str(record.funcName)
        if level_name == 'DEBUG':
            return '{0:>9s} | {2} | {1}'.format( level_name , msg, name+'.'+funcName)
        else:
            return '{0:>9s} | {1}'.format( level_name , msg)
class ColoredFormatter(logging.Formatter):
    """
        Class to create a log output which is colored based on level.
    """

    def __init__(self, *args, **kwargs):
        super(ColoredFormatter, self).__init__(*args, **kwargs)
        self.colors = {
            'DEBUG': '\033[94m',
            'INFO': '\033[92m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
        }

        self.reset = '\033[0m'

    def format(self, record):
        msg = str(record.msg)
        level_name = str(record.levelname)
        name = str(record.name)
        color_prefix = self.colors[level_name]
        funcName = str(record.funcName)
        if level_name == 'DEBUG':
            return '{0}{1:>9s} | {4} | {2}{3}'.format(color_prefix,
                                                level_name , msg,
                                                self.reset, name+'.'+funcName)
        else:
            return '{0}{1:>9s} | {2}{3}'.format(color_prefix,
                                                level_name , msg,
                                                self.reset)


def dump_yaml(foo, outfile):
    '''
    This function dumps dictionary into yaml files
    Args: foo -> dictionary to be put into yaml
          outfile -> yaml file
    '''
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.compact(seq_seq=False, seq_map=False)
    yaml.dump(foo, outfile)

def load_yaml(foo, no_anchors=False):
    '''
    This function loads yaml files into dictionaries
    Args: foo -> yaml file
          no_anchors -> Boolean arg to configure yaml loading based on yaml anchors
    '''
    if not os.path.isfile(foo):
        logger.error(f"{foo} not found!")
        raise SystemExit(1)

    if no_anchors:
        yaml = YAML(typ="safe")
    else:
        yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.compact(seq_seq=False, seq_map=False)
    yaml.indent = 4
    yaml.block_seq_indent = 2

    with open(foo, "r") as file:
        return yaml.load(file)

def clean_dir(directory):
    '''
    Cleans the directory recursively if the directory exists
    Args: directory -> directory to be cleaned
    '''

    # Cleaning the directory
    if os.path.isdir(directory):
        logger.info(f'Removing directory {directory} recursively')
        shutil.rmtree(directory)
    else:
        pass

def mover(build, config)-> None:
    """mover function"""
    for to_move in config["mover"]:
        dest= os.path.join(f"{build}/", to_move)
        shutil.copytree(to_move, dest, dirs_exist_ok=True)

def directory_setup(build, config):
    """Creates the directory structure"""
    os.makedirs(f"{build}", exist_ok=True)
    os.makedirs(f"{build}/tags", exist_ok=True)
    os.makedirs(f"{build}/blog", exist_ok=True)
    config_src= load_yaml(config)
    mover(build, config_src)

def clean_dir(directory):
    '''
    Cleans the directory recursively if the directory exists
    Args: directory -> directory to be cleaned
    '''

    # Cleaning the directory
    if os.path.isdir(directory):
        logger.info(f'Removing directory {directory} recursively')
        shutil.rmtree(directory)
    else:
        pass
