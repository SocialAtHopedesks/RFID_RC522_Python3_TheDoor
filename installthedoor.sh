#!bin/sh
echo "This installer connects to the internet, downloads and installs files and changes cron and alias entries"
sleep 4
echo "!!! - !!! - !!! - !!! - !!! - provided free and without any guarantees - !!! - !!! - !!! - !!! - !!! - !!!"
sleep 4
echo "!!! - !!! - !!! - !!! - !!! - to cancel: Control c in the next 15 seconds - !!! - !!! - !!! - !!! - !!! - !!!"
sleep 15
wget http://www.plenkyman.com/thedoor.tar.gz
tar -zxvf thedoor.tar.gz
sleep 4
rm thedoor.tar.gz
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install mysql-server pypy --fix-missing
sudo pip3 install pymysql
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.50.tar.gz
tar -zxf bcm2835-1.50.tar.gz
cd bcm2835-1.50
./configure
sudo make install
sleep 4
cd ~
rm bcm2835-1.50.tar.gz
sudo apt-get install subversion
svn checkout http://rpi-rc522.googlecode.com/svn/trunk/ rpi-rc522-read-only
cd rpi-rc522-read-only/rc522
gcc config.c rfid.c rc522.c main.c -o rc522_reader -lbcm2835
sudo cp RC522.conf /etc/
cd ~
echo "x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - updated, upgraded, modules installed - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x"
sleep 4
cd /etc/cron.d/
sudo sh -c 'cat /home/pi/thedoor/system/cron_entries.txt > doorcrons'
cd ~
sudo cat thedoor/system/bash_aliases.txt > ~/.bash_aliases
echo "x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - cron and bash aliases installed - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x"
cd thedoor/db_backup
read -p "Enter the database root password again: " dbpasstemp
mysql -u root -p$dbpasstemp -e "create database RfidDoor"
mysql -D RfidDoor -u root -p$dbpasstemp -e "source TheDoor.sql"
mysql -D RfidDoor -u root -p$dbpasstemp -e "CREATE USER 'TheDoor'@'localhost' IDENTIFIED BY 'Schmilblick'"
mysql -D RfidDoor -u root -p$dbpasstemp -e "GRANT ALL PRIVILEGES ON * . * TO 'TheDoor'@'*'"
mysql -D RfidDoor -u root -p$dbpasstemp -e "GRANT ALL PRIVILEGES ON * . * TO 'TheDoor'@'localhost'"
mysql -D RfidDoor -u root -p$dbpasstemp -e "flush privileges"
echo "x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - database installed and updated - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x"
sleep 4
cd ~
python3 thedoor/TheDoorConfig.py
echo "x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - : < - TheDoor is configured ! - > : - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x"
echo "x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - ! ! ! shutdown in one minute ! ! ! - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x - 0 - x"
cd ~
rm installthedoor.sh
sudo shutdown -h +1
