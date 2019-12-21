# How to install n1mm_view on Windows

#### _Preliminary_ Python 3 version...

1. Fetch _miniconda_ from https://docs.conda.io/en/latest/miniconda.html and install it.  
Select a Python 3 version.  
You will need to reboot after, so that conda gets picked up by the system path.

1. open a "conda window" and run these commands
    ```
    conda create -n n1mm_view python=3.5
    activate n1mm_view
    conda install --channel https://conda.anaconda.org CogSci pygame
    conda install matplotlib
    conda install cartopy
    ```

1. Either clone n1mm_view with git or fetch the zip of _n1mm_view_ from https://github.com/n1kdo/n1mm_view/archive/master.zip and unpack it.

1. to run the various scripts

    ```
    conda activate n1mm_view
    python collector.py
   ```
   etc.
   
#### Python 2.7 Windows Installation Instructions courtesy of Sheldon, VE1GPY/VE1SL 

1. Install Python 2.7.13 from python.org https://www.python.org/downloads/ “Download Python 2.7.13”.  
(Note: this is a link to the current-latest 64-bit build of Python for Windows: https://www.python.org/ftp/python/2.7.13/python-2.7.13.amd64.msi)

1. Open a command window using Start/Run `cmd`

1. Pip and setuptools are included in Python 2.7 but they’ll need to be updated to the latest version.  Use this command in the cmd window:
`python –m pip install –U pip setuptools`

1. Create a Python Virtual Environment using virtualenv.
This will provide a stable environment for n1mm_view and isolate it from changes made to the Python environment for other applications. Use this command in the cmd window:
`virtualenv C:\n1mm_view` -- where C:\n1mm_view is a directory to place the new virtual environment.

1. Activate the new Python virtual environment by running the activate script. Use this command in the cmd window:
`C:\n1mm_view\Scripts\activate.bat`

1. Install required packages in the virtual environment, using these commands in the cmd window:    
`pip install matplotlib`  
`pip install numpy`  
`pip install pygame`

1. Download Microsoft Visual C++ Compiler for Python 2.7 from http://aka.ms/vcpython27. And install it by running the .msi file.  This will be required to install the basemap packages’ wheel file.

1. Download the basemap package from http://www.lfd.uci.edu/~gohlke/pythonlibs/ web site.  Even though I’m using 64-bit Windows, the file that worked for me was: basemap-1.1.0-cp27-cp27m-win32.whl.  
(Note: this depends on whether you have 32- or 64-bit install of _Python_.)

1. Install the newly downloaded basemap package using this command in the cmd window: `pip install “C:\Users\<your user name>\Downloads\basemap-1.1.0-cp27-cp27m-win32.whl`

1. Create a new sub-directory in C:\n1mm_view called User files, using this command in the cmd window: `mkdir C:\n1mm_view\User_files`

1. Download the latest n1mm_view source code from `https://github.com/n1kdo/n1mm_view`.  Use the “Clone or Download” button to download a zip file.  Unzip the entire contents of the downloaded zip file, including subdirectories, into the newly-created C:\n1mm_view\User_files directory.

1. Edit the `C:\n1mm_view\User_files\n1mm_view_config.py` configuration file.  Update as necessary for your situation.

1. Download Windows tee command from http://www.westmesatech.com/sst.html.  We’ll use it in the start_collector.cmd file.  Place tee.exe in the C:\n1mm_view\User_files directory.

1. Create a command script in the C:\n1mm_view directory called `start_collector.cmd`.  Edit the file to include these commands:  
`cd /d C:\n1mm_view\user_files`  
`call ..\Scripts\activate.bat`  
`echo To stop the collector, close this window`  
`..\Scripts\python collector.py 2>&1 | tee START_collector.log`

1. Create a command script in the C:\n1mm_view directory called start_dashboard.cmd.  Edit the file to include these commands:  
`cd /d C:\n1mm_view\user_files`  
`call ..\Scripts\activate.bat`  
`..\Scripts\python dashboard.py 1>START_dashboard.log 2>&1`

END
 
