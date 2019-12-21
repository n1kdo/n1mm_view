# How to install n1mm_view on Raspberry Pi

1. install Raspian "buster" "lite" onto your Raspberry Pi -- we don't need the full version. https://www.raspberrypi.org/downloads/raspbian/
1. log in
1. open terminal window
1. Run the following four commands
* `git clone https://github.com/n1kdo/n1mm_view.git`
this downloads the latest copy of n1mm_view to your pi
* `cd n1mm_view`
This moves into the project directory
* `pip install numpy`
make sure library for higher math computations is available
* `sudo ./rpi_install.sh` 
Installs the remaining libraries and prerequisites. also gets all current updates for Raspbian.) This also handles everything in the Configure_Apache document. If you will not use the webserver option, you can simply stop the apache daemon (`sudo apachectl stop`)
This last command will run for quite some time. We gave it a lot of things to do.

Update config.py with your operating settings. "MyClubCall" is a placeholder. For pre-testing, make the event start time before and the event end time after your current clock time. Other options in the configuration file are helpfully commented.

# Running N1MM_view
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

