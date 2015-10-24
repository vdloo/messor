import os 

MESSOR_PATH = '~/messor'
MESSOR_PATH = os.path.expanduser(MESSOR_PATH)

MESSOR_BUFFER = os.path.join(MESSOR_PATH, 'buffer')
PICKUP_HOSTS_FILE = '~/.messor_pickup_hosts'
PICKUP_HOSTS_FILE = os.path.expanduser(PICKUP_HOSTS_FILE)

PICKUP_HOSTS = list(map(str.strip, open(PICKUP_HOSTS_FILE).readlines()))
assert len(PICKUP_HOSTS) > 0, "define one or more pickup hosts in %s" % PICKUP_HOSTS_FILE
