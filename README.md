# n1mm_view

`n1mm_view` is a set of python scripts to display real-time contest QSO statistics for ARRL Field Day.

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

Dependencies:

* python 2.7
* python matplotlib library
* python pygame library
* python sqlite3 library

Components:

* collector.py -- collect contact data from n1mm+ broadcasts
* dashboard.py -- display collected statistics on screen
* n1mm_view_constants.py -- constant values shared by collector and dashboard.  Bands and Modes are defined here.
* replayer.py -- test application, "replays" an old N1MM+ log to test collector and dashboard.
