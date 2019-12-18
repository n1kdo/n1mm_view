# How to install n1mm_view on Raspberry Pi

1. install Raspian "buster" "lite" onto your Raspberry Pi -- we don't need the full version. https://www.raspberrypi.org/downloads/raspbian/
1. log in
1. open terminal window
1. `$ sudo apt-get update` -- this takes about 2 minutes
1. `$ sudo apt-get upgrade` -- this takes a while.
1. `$ sudo apt-get install git python3-dev python3-pygame python3-matplotlib python3-cartopy python3-pykdtree python3-scipy`

Copy the project files into place.
1. `$ git clone https://github.com/n1kdo/n1mm_view.git`
1. `$ cd n1mm_view`
1. `$ ls` You should see that the n1mm_view files have been installed.

Complete the "Configure Apache" instructions.

Now you can run the programs.

There are two programs of interest.  You will want to open a separate terminal window for each.

First, start the collector: `$ ./collector.py` -- the collector will create the database
`n1mm_view.db` if it is not present.

After the collector has started, use your other terminal window and start the dashboard:
`./dashboard.py`.  As the QSOs are collected by the collector, the dashboard will show
statistics.

The collector can be stopped with control-c.  

The dashboard responds to a few hotkeys:
* 'n' -- show the next display page
* 'q' -- exit the dashboard (this does not work if you start it via autostart/systemd)
* 'leftarrow' -- cycle to next graph
* 'rightarrow' -- cycle to previous graph

You can flush the collected statistics (perhaps immediately before the
contest starts) by shutting down the collector and dashboard and then
deleting the database:

`$ rm n1mm_view.db` -- then restart the collector immediately.

## How to install the autostart scripts

You can install systemd configuration files on your system to make the
collector and dashboard processes start automatically at boot time.

1. get root (sudo bash, or whatever way you like)
1. `cp init/*.service /lib/systemd/system`
1. `systemctl enable n1mm_view_collector`
1. `systemctl enable n1mm_view_dashboard`

Upon reboot, the collector and dashboard should start automatically.  
Consider this rather experimental at this time.  It might work.
It works for me.

## Challenges, "Gotchas", and Caveat Emptor

My experience is that this all works better if you have static IP addresses
for every computer running N1MM+ and the Raspberry Pi.  Configuration of
static IP is beyond the scope of this document.

