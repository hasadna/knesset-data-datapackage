import logging, sys, os
from shutil import rmtree


def setup_logging(debug=False):
    logLevel = logging.DEBUG if debug else logging.INFO
    [logging.root.removeHandler(handler) for handler in tuple(logging.root.handlers)]
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("%(name)s:%(lineno)d\t%(levelname)s\t%(message)s"))
    stdout_handler.setLevel(logLevel)
    logging.root.addHandler(stdout_handler)
    logging.root.setLevel(logLevel)


def setup_datapath(path=None, delete=False):
    if not path:
        path = os.path.abspath(os.path.join(os.getcwd(), "data"))
    if os.path.exists(path) and delete:
        rmtree(path)
    if not os.path.exists(path):
        os.mkdir(path)
    return path
