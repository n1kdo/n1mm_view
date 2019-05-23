Install Apache
   sudo apt-get install -y apache2

   Disk Writing considerations

   While the SD card in a Pi lasts a long time, it's write cycles are not limitless. One option would be to write the PNG files to a RAM disk. As the nature of these files are temporary, losing the files at boot time is not a major issue since when dashboard.py runs, it regenerates all the files.

   To do this, assume you want to call the RAM drive /var/ram
   ```bash
   sudo mkdir /var/ram
   sudo nano /etc/fstab
   add a line that reads (these are TAB characters, not spaces):

   tmpfs  /var/ram tmpfs nodev,nosuid,size=2M 0 0

   Save and exit the file
   sudo mount -a
   df
   Filesystem     1K-blocks    Used Available Use% Mounted on
   /dev/root       30571612 5103532  24167736  18% /
   devtmpfs          468152       0    468152   0% /dev
   tmpfs             472760       0    472760   0% /dev/shm
   tmpfs             472760    6452    466308   2% /run
   tmpfs               5120       4      5116   1% /run/lock
      tmpfs             472760       0    472760   0% /sys/fs/cgroup
      tmpfs               2048       0      2048   0% /var/ram
      /dev/mmcblk0p1     41322   21384     19938  52% /boot
      tmpfs              94552       0     94552   0% /run/user/1000
      tmpfs              94552       0     94552   0% /run/user/1001
   ```
   Change HTML_DIR in n1mm_view_config.py to /var/ram/n1mm_view/html (or something similar).

Set HTML directory in config file
Create the directory if necessary and allow the www-data group to read the directory:

   mkdir -p /var/ram/n1mm_view/html
   sudo chgrp -R www-data /var/ram/n1mm_view

Modify Apache config (one of two ways):
Add virtual directory and Alias statement to apache2.conf or create n1mm_view.conf in /etc/apache2/conf-available
```ApacheConf
Alias /n1mm_view "/var/ram/n1mm_view/html/"
<Directory "/var/ram/n1mm_view/html/">
   Options Indexes FollowSymLinks
   AllowOverride None
   Require all granted
</Directory>

```
If you want to add it as a conf-available, then enter:
   sudo nano /etc/apache2/conf-available/n1mm_view.conf
   Add above lines
   sudo a2enconf n1mm_view
   sudo service apache2 reload
