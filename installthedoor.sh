#!bin/sh
### plenkymans installation script
clear; tput cup 20 8; echo "This installer connects to the internet, downloads and installs files and changes cron and alias entries"
sleep 1
tput cup 21 8; echo "The entire process takes about 20 minutes."
sleep 1
tput cup 25 8; echo "!!! - provided free and without any guarantees - !!!"
sleep 1
tput cup 28 8; echo "!!! - to cancel: Control c in the next 15 seconds - !!!"
sleep 15
clear; tput cup 19 8; echo "*************************************************"
while :
do
	tput cup 20 8;read -p "Set the mysql database root password: " check1
	tput cup 21 8;read -p "Enter the mysql database root password again: " check2
	if [ "$check1" == "$check2" ]
	then
		break
	fi
	tput cup 22 8; echo "passwords do not match!"
done
mysqlroot=$check1
tput cup 23 8;echo "Your recorded root password for mysql is: $check1"
sleep 4
clear; tput cup 20 8; echo "*************************************************"
tput cup 21 8; echo "please provide a password for the RfidDoor database"
while :
do
	tput cup 22 8; read -p "Set a password for RfidDoor: " bcheck1
	tput cup 23 8; read -p "Enter the password for RfidDoor again: " bcheck2
	if [ "$bcheck1" == "$bcheck2" ]
	then
		break
	fi
	tput cup 24 8; echo "passwords do not match!"
done
mysqlthedoor=$bcheck1
tput cup 25 8; echo "Your recorded user password for mysql is: $bcheck1"
sleep 4
wget http://www.plenkyman.com/thedoor.tar.gz
tar -zxvf thedoor.tar.gz
rm thedoor.tar.gz
sudo apt-get update && sudo apt-get -y upgrade
echo mysql-server mysql-server/root_password password $mysqlroot | sudo debconf-set-selections
echo mysql-server mysql-server/root_password_again password $mysqlroot | sudo debconf-set-selections
sudo apt-get install -y mysql-server pypy
sudo pip3 install pymysql
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.50.tar.gz
tar -zxf bcm2835-1.50.tar.gz
cd bcm2835-1.50
./configure
sudo make install
sleep 4
cd ~
rm bcm2835-1.50.tar.gz
sudo apt-get install -y subversion
svn checkout http://rpi-rc522.googlecode.com/svn/trunk/ rpi-rc522-read-only
cd rpi-rc522-read-only/rc522
gcc config.c rfid.c rc522.c main.c -o rc522_reader -lbcm2835
sudo cp RC522.conf /etc/
cd ~
clear; tput cup 20 8; echo "0 - x - updated, upgraded, modules installed - 0 - x"
sleep 4
cd /etc/cron.d/
sudo sh -c 'cat /home/pi/thedoor/system/cron_entries.txt > doorcrons'
cd ~
sudo cat thedoor/system/bash_aliases.txt > ~/.bash_aliases
tput cup 21 8; echo "0 - x - cron and bash aliases installed - x - 0"
cd thedoor/db_backup/
mysql -u root -p$mysqlroot -e "create database RfidDoor"
mysql -D RfidDoor -u root -p$mysqlroot -e "source TheDoor.sql"
mysql -D RfidDoor -u root -p$mysqlroot -e "CREATE USER 'TheDoor'@'localhost' IDENTIFIED BY $mysqlthedoor"
mysql -D RfidDoor -u root -p$mysqlroot -e "GRANT ALL PRIVILEGES ON * . * TO 'TheDoor'@'*'"
mysql -D RfidDoor -u root -p$mysqlroot -e "GRANT ALL PRIVILEGES ON * . * TO 'TheDoor'@'localhost'"
mysql -D RfidDoor -u root -p$mysqlroot -e "flush privileges"
tput cup 22 8; echo "0 - x - database installed and updated - x - 0"
cd ~/thedoor/
sed -i 's/Ux4TyH9llHvcTsQ/'$mysqlthedoor'/' TheDoorConfig.py
sleep 1
cd ~
python3 thedoor/TheDoorConfig.py
sleep 2
tput cup 23 8; echo "x - 0 -  - TheDoor is configured ! -  - 0 - x"
tput cup 24 8; echo "x - 0 - ! ! ! shutdown in one minute ! ! ! - 0 - x"
cd ~
rm installthedoor.sh
sudo shutdown -h +1
