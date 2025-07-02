#!/bin/bash
echo "Copying config to Kamailio directory..."

cp /mnt/kamailio_voip/kamailio.cfg /usr/local/etc/kamailio/kamailio.cfg
cp /mnt/kamailio_voip/kamctlrc /usr/local/etc/kamailio/kamctlrc

echo "Starting Kamailio..."
/usr/local/sbin/kamailio -DD -E