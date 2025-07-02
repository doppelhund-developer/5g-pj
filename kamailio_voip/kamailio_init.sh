#!/bin/bash
echo "Copying config to Kamailio directory..."

cp /mnt/kamailio_voip/kamailio.cfg /usr/local/etc/kamailio/kamailio.cfg
cp /mnt/kamailio_voip/kamctlrc /usr/local/etc/kamailio/kamctlrc

sleep 3

mysql -uroot -p1234 -h 172.22.0.17 -e "ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '1234'; FLUSH PRIVILEGES;"

echo "Starting Kamailio..."
/usr/local/sbin/kamailio -DD -E