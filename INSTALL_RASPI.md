# How to install n1mm_view on Raspberry Pi

1. install Raspian "buster" or "bullseye" onto your Raspberry Pi.  This could also be the "lite" version -- we don't require the full version. https://www.raspberrypi.org/downloads/raspbian/
1. log in, set up your Pi's internet connection
1. open terminal window
1. Run the following four commands
* `git clone https://github.com/n1kdo/n1mm_view.git`
this downloads the latest copy of n1mm_view to your pi
* `cd n1mm_view`
This moves into the N1MM_view project directory
* `pip install numpy` `sudo apt install python3-numpy`
make sure library for higher math computations is available
* `chmod +x rpi_install.sh`
* If you are not running with the default 'pi' user, then modify the file `init/ramdisk-sync.service` and replace instances of `pi` with your username.
* `sudo ./rpi_install.sh` 
Installs the remaining libraries and prerequisites (also gets all current updates for Raspbian). This also handles everything in the Configure_Apache document. If you will not use the webserver option, you can simply stop the apache daemon (`sudo apachectl stop`).
This last command will run for quite some time. 
The latest test took about 90 minutes with a good internet connection for a Raspberry Pi 3 B+ (18 minutes on a Pi 4B). We gave it a lot of things to do so you won't need to do them.
While you are waiting, you could create a splash screen for your event: a 1000x1000 portable network graphics (.png) image in RGB format works great.   

Edit the config.py file with your operating settings. "MyClubCall" is a placeholder. For testing, make the event start time before and the event end time after your current clock time. Other options in the configuration file are helpfully commented.

# Running N1MM_view
There are two programs of interest.  You will want to open a separate terminal window for each.

First, start the collector: `./collector.py` -- the collector will create the database
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

## Optional: How to install the autostart scripts

You can install systemd configuration files on your system to make the
collector and dashboard processes start automatically at boot time. Note this assumes the rpi_install script copied init/*.service to /lib/systemd/system/.

1. `sudo systemctl enable n1mm_view_collector`
1. `sudo systemctl enable n1mm_view_dashboard`

### If running the headless script to generate images, install this service.
3. `sudo systemctl enable n1mm_view_headless`

Upon reboot, the collector and dashboard [and optionally headless] should start automatically.  
Consider this experimental at this time.  It might work. It works for me.

## Challenges, "Gotchas", and Caveat Emptor

My experience is that this all works better if you have static IP addresses
for every computer running N1MM+ and the Raspberry Pi.  Configuration of
static IP is beyond the scope of this document.

