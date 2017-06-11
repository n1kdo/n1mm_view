Install Apache
sudo apt-get install apache2

Set HTML directory in config file
Create the directory if necessary and allow the www-data group to read the directory:

chgrp -R www-data /var/www

Modify Apache config (one of two ways):
Add virtual directory and Alias statment to apache2.conf
Alias /n1mm_view "/home/pi/n1mm_view/html"
<Virtual Directory...

