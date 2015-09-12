import logging
import os 
from messor.utils import ensure_directories
from messor.settings import FORMICARY_PATH

logger = logging.getLogger(__name__)

def compose_formicary_path(path):
    return os.path.join(FORMICARY_PATH, path)

def ensure_formicary_directories(required_directories):
    formicary_directories = map(compose_formicary_path, required_directories)
    ensure_directories(formicary_directories)

def setup_formicary():
    logger.info("Ensuring directory structure exists..")
    ensure_formicary_directories(['outbox', 'inbox'])
    logger.info("Directory structure exists!")
    logger.info("Drop files in %s/<DESTINATIONHOSTNAME> to sync them to the "
                "inbox on that host" % compose_formicary_path('outbox'))
