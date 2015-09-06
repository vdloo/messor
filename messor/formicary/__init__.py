import logging
import os 
from messor.utils import ensure_directories

logger = logging.getLogger(__name__)

FORMICARY_PATH = '~/messor'

def compose_formicary_path(path):
    relative_path = os.path.join(FORMICARY_PATH, path)
    return os.path.expanduser(relative_path)

def ensure_formicary_directories(required_directories):
    formicary_directories = map(compose_formicary_path, required_directories)
    ensure_directories(formicary_directories)

def main():
    logger.info("Ensuring directory structure exists..")
    ensure_formicary_directories(['outbox', 'inbox'])
    logger.info("Directory structure exists!")
    logger.info("Drop files in %s/<DESTINATIONHOSTNAME> to sync them to the "
                "inbox on that host" % compose_formicary_path('outbox'))
