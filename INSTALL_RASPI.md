# How to install n1mm_view on Raspberry Pi

1. install Raspian
1. log in 
1. open terminal window
1. `$ sudo apt-get update` -- this takes about 2 minutes
1. `$ sudo apt-get upgrade` -- this takes a while minutes.  Get a beer.
1. `$ sudo apt-get install python27-dev` -- this takes a short minute.
1. `$ sudo apt-get install python-pygame`
1. `$ sudo pip install numpy` -- beer time again.  :beer:  There will likely be some compile warnings.
Warnings are OK.  Errors are not.  This takes a while.
1. `$ sudo pip install matplotlib` -- n1mm_view needs 1.5.0 or 1.5.1, so this has to be installed the hard way.
Get another beer.  :beer:
1. `$ sudo bash`
1. `$ wget http://iweb.dl.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.tar.gz `
1. `$ tar xf basemap-1.0.7.tar.gz`
1. `$ cd basemap-1.0.7/geos-3.3.3`
1. `$ export GEOS_DIR=/usr/local`
1. `$ ./configure --prefix=$GEOS_DIR`
1. `$ make ; make install` -- beer time again.  :beer:
1. `$ cd ..`
1/ `$ python setup.py install`  -- again, you might see more warnings.  relax and have another beer.  :beer:
1. `$ exit` -- this logs you out of the root account.
1. `$ git clone https://github.com/n1kdo/n1mm_view.git`
1. `$ cd n1mm_view`
1. `$ ls`

After you enter the `ls` command, you should see that the n1mm_view files have been installed.

Now you can run the programs.

There are two programs of interest.  You will want to open a terminal window for each.

First, start the collector: `$ ./collector.py` -- the collector will create the database 
`n1mm_view.db` if it is not present.

After the collector has started, use your other terminal window and start the dashboard: 
`./dashboard.py`.  As the QSOs are collected by the collector, the dashboard will show 
statistics.

The collector can be stopped with control-c.  

The dashboard responds to two keystrokes: 
* 'n' -- show the next display page
* 'q' -- exit the dashboard

You can flush the collected statistics (perhaps immediately before the contest starts) 
by shutting down the collector and dashboard and then deleting the database: 
`$ rm n1mm_view.db` -- then restart the collector immediately.

