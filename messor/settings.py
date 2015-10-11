import os 

FORAGER_BUFFER = '~/buffer'
FORMICARY_PATH = '~/messor'
PICKUP_HOSTS_FILE = '~/.messor_pickup_hosts'

FORAGER_BUFFER = os.path.expanduser(FORAGER_BUFFER)
FORMICARY_PATH = os.path.expanduser(FORMICARY_PATH)
PICKUP_HOSTS_FILE = os.path.expanduser(PICKUP_HOSTS_FILE)

PICKUP_HOSTS = list(map(str.strip, open(PICKUP_HOSTS_FILE).readlines()))
assert len(PICKUP_HOSTS) > 0, "define one or more pickup hosts in %s" % PICKUP_HOSTS_FILE
