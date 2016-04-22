# n1mm_view

`n1mm_view` is a set of python scripts to display real-time contest QSO statistics for :zap: N4N ARRL Field Day.

It listens to N1MM+ "Contact Info" UDP broadcasts 
(see the [N1MM+ documentation](http://n1mm.hamdocs.com/tiki-index.php?page=UDP+Broadcasts))
and collects the contact info into a database.  The contact info data is used to create useful data screens that 
are rotated through.

It was built to run on a Raspberry Pi and to display the statistics on a large television screen.  It should 
run anywhere its dependencies can be installed on, meaning it should work on Linux, Windows, and OS X.

Currently, it supports the following displays:

* QSOs by Operator pie chart
* QSO by Band Pie chart
* QSOs by Mode Pie chart
* QSOs by Station Pie chart
* QSOs Summary Table
* QSO/Hour Rate Table

### Dependencies:

* python 2.7
* python matplotlib library
* python pygame library
* python sqlite3 library

### Components:

* collector.py -- collect contact data from n1mm+ broadcasts
* dashboard.py -- display collected statistics on screen
* n1mm_view_constants.py -- constant values shared by collector and dashboard.  Bands and Modes are defined here.
* n1mm_view_config.py -- configuration data.  in theory, the only part you should need to edit to configure n1mm_view for your environment.
* replayer.py -- test application, "replays" an old N1MM+ log to test collector and dashboard.

### Installation

See [INSTALL_RASPI.md](INSTALL_RASPI.md) for information to install n1mm_view on a Raspberry Pi.

### License:

This software is licensed under the terms of the "Simplified BSD license", see [LICENSE](LICENSE).

Copyright 2016, Jeffrey B. Otterson, N1KDO  
All Rights Reserved

### To Do

There's always more to do.  This project is still in late-prototype stage.

* fix colors of matplotlib pie charts.  A white slice with white text is unreadable.
* add command-line options
* somebody might want to support other contests besides field day
  * choropleth map to show areas worked
  * multipliers table
* the `qso_log` table could be exported to ADIF.
* drink beer :beer:
