import yaml
import logging 

def load_confs(confs_path='conf.yaml'):
    """
    Load configurations from file.
     - If configuration file is available, load it
     - If configuraiton file is not available attempt to load configuration template
    Configurations are never explicitly validated.
    :param confs_path: Path to a configuration file, appropriately formatted for this application
    :type confs_path: str
    :return: Python native object, containing configuration names and values
    :rtype: dict
    """

    try:
        logging.info('Attempting to load conf from path: {}'.format(confs_path))

        # Attempt to load conf from confPath
        CONFS = yaml.load(open(confs_path))

    except IOError:
        logging.warn('Unable to open user conf file. Attempting to run with default values from conf template')

        # Attempt to load conf from template path
        template_path = confs_path + '.template'
        CONFS = yaml.load(open(template_path))

    return CONFS


def get_conf(conf_name):
    """
    Get a configuration parameter by its name
    :param conf_name: Name of a configuration parameter
    :type conf_name: str
    :return: Value for that conf (no specific type information available)
    """
    return load_confs()[conf_name]