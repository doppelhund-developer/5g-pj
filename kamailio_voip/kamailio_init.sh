#!/bin/bash

echo "Copying config to Kamailio directory..."
cp /mnt/kamailio_voip/kamailio.cfg /usr/local/etc/kamailio/kamailio.cfg
cp /mnt/kamailio_voip/kamctlrc /usr/local/etc/kamailio/kamctlrc

# Start Kamailio in background
echo "Starting Kamailio..."
/usr/local/sbin/kamailio -DD -E &

# Wait briefly to ensure MySQL is up

DBPORT="${DBPORT:-3306}"

echo "Waiting for MySQL at $MYSQL_IP:$DBPORT..."

for i in {1..30}; do
    if (echo > /dev/tcp/$MYSQL_IP/$DBPORT) >/dev/null 2>&1; then
        echo "MySQL is accepting TCP connections!"
        break
    fi
    echo "MySQL not available yet... ($i/30), retrying in 2s"
    sleep 2
done


echo "Running kamdbctl create..."
if kamdbctl create; then
    echo "kamdbctl create succeeded."
else
    echo "kamdbctl create failed. Trying kamdbctl reinit..."
    if kamdbctl reinit; then
        echo "kamdbctl reinit succeeded."
    else
        echo "kamdbctl reinit also failed. Exiting..."
        exit 1
    fi
fi

# Add test users
echo "Adding users..."
kamctl add 1001 gg
kamctl add 1002 gg

# Wait on background Kamailio
wait
