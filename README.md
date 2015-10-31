messor
===========

Sneakernet filesync. Use mobile devices to transfer data from one host to the other.  

&nbsp;  

<p align="center">
  <img src="https://raw.githubusercontent.com/vdloo/messor/master/docs/animation/assets/messor.gif" alt="animated example"/>
</p>



How does it work?
-----------------
Imagine two machines, one is the source and one the destination. The source machine has an outbox folder containing a directory named after the host where the files should go. If the carrier is in the network of the source host, it will download all files that fit from the outbox to its local buffer. The destination machine has an inbox folder. Once the carrier is in the destination host's network it will upload the files from the directory for that host in the local buffer to the destination host's inbox.

Features
--------
- file level deduplication
- blackhole outbox directory
- zero configuration on the hosts
- sync over ssh

Use case
--------
There are various reasons why transferring data by physically taking it somewhere might be desirable. For me the use case is mostly that I've spent a lot of time on trains and buses over the past couple of years and I've often wondered how much data I could have moved by just taking it with me in small batches. Commuting has been a fact of life ever since the 19th century. The difference between now and then is that we have supercomputers in our pockets.

> Never underestimate the bandwidth of a station wagon full of tapes hurtling down the highway. —Tanenbaum, Andrew S. (1989).

Installation
------------
You only need to install messor on your carrier device. I use a rooted android running linux in a chroot.
```
git clone https://github.com/vdloo/messor.git
cd messor/src
mkvirtualenv messor
pip install -r requirements/base.txt
```

To specify hosts to sync from add the hostnames to ```~/.messor_pickup_hosts```. The user running messor on the carrier will need to be able to [passwordlessly login to these hosts over ssh](https://wiki.archlinux.org/index.php/SSH_keys#Simple_method). If you need to use a specific port for a host [define it](https://wiki.archlinux.org/index.php/Secure_Shell#Saving_connection_data_in_ssh_config) in your ```~/.ssh/config```. 
```
echo "192.168.12.34" >> ~/.messor_pickup_hosts
```

I recommend using hostnames that can only be reached locally so that you won't accidentally transfer the files over 3G and burn through your mobile data.

Usage
-----

On the host you want to sync from (in this example that is ```192.168.12.34```, create the outbox directory for the destination.
```
ssh 192.168.12.34
mkdir -p ~/messor/outbox/192.168.56.78
```

Dump files there that you want to have synced to the destination's inbox directory.
```
cp -R ~/some_file_directory/ ~/messor/outbox/192.168.56.78/
```

On the carrier, if you start the pick_up script when you are in the source host's network outbox files will be downloaded to the local buffer until the limit set in ```settings.py``` is reached.
```
cd messor/src
workon messor
export PYTHONPATH=.
./bin/pick_up --verbose
```

Once you are in the destination host's network, running the drop_off script will upload the files.
```
./bin/drop_off --verbose
```

Automation
----------
You can run the pick_up and drop_off scripts at any time, if there are no involved hosts in range or no files to sync, nothing will happen. For example, you could start the drop off and pick up sequentially in a cron, or trigger it once the carrier connects to a network over wifi.


Development
-----------
```
workon messor
pip install -r requirements/development.txt
./runtests.sh
```
