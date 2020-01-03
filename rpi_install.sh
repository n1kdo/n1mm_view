# git clone https://github.com/n1kdo/n1mm_view.git
# cd n1mm_view
# pip install numpy
if [[ $EUID -ne 0 ]]; then
   echo "This part of setup needs full system access."
   echo "You can simply type: "
   echo "    sudo !!"
   echo "at the next prompt.  This allows the script to install the libraries and packages required."
   exit 1
fi

apt-get update
apt-get -y upgrade
apt-get -y install python-dev python-pygame apache2
apt-get install -y git python3-dev python3-pygame python3-matplotlib python3-cartopy python3-pykdtree python3-scipy

# ramdisk and Apache
mkdir -p /mnt/ramdisk
mount -t tmpfs -o rw,size=2G tmpfs /mnt/ramdisk
if [[ $(grep -q "/mnt/ramdisk" "/etc/fstab") ]]
then
    echo "tmpfs /mnt/ramdisk  tmpfs rw,size=2G  0 0" >> /etc/fstab
else
    echo "Warning: Filesystem table already shows ramdisk. Skipping."
fi
mount -a

# Change HTML_DIR in n1mm_view_config.py to /var/ram/n1mm_view/html (or something similar).
mkdir -p /var/ram/n1mm_view/html sudo chgrp -R www-data /var/ram/n1mm_view
cp ./apache2/conf-available/n1mm_view.conf /etc/apache2/conf-available/.
a2enconf n1mm_view
apache2ctl restart

echo
echo "Remember to update your config.py file before starting the collector and dashboard."
echo
