#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export IP_ADDR=$(awk 'END{print $1}' /etc/hosts)
export IF_NAME=$(ip r | awk '/default/ { print $5 }')

python3 /mnt/upf/tun_if.py --tun_ifname ogstun --ipv4_range $UE_IPV4_INTERNET_ --ipv6_range 2001:230:cafe::/48

UE_IPV4_INTERNET_TUN_IP=$(python3 /mnt/upf/ip_utils.py --ip_range $UE_IPV4_INTERNET_)

cp /mnt/upf/upf.yaml install/etc/open5gs
sed -i 's|UPF_IP|'$UPF_IP_'|g' install/etc/open5gs/upf.yaml
sed -i 's|SMF_IP|'$SMF_IP_'|g' install/etc/open5gs/upf.yaml
sed -i 's|SST|'$SST'|g' install/etc/open5gs/upf.yaml
sed -i 's|SLICE_NAME|'$SLICE_NAME'|g' install/etc/open5gs/upf.yaml
sed -i 's|IPV6_SUBNET_PART|'$IPV6_SUBNET_PART'|g' install/etc/open5gs/upf.yaml
sed -i 's|UE_IPV4_INTERNET_TUN_IP|'$UE_IPV4_INTERNET_TUN_IP'|g' install/etc/open5gs/upf.yaml
sed -i 's|UE_IPV4_INTERNET_SUBNET|'$UE_IPV4_INTERNET_'|g' install/etc/open5gs/upf.yaml
sed -i 's|UE_IPV4_IMS_TUN_IP|'$UE_IPV4_IMS_TUN_IP'|g' install/etc/open5gs/upf.yaml
sed -i 's|UE_IPV4_IMS_SUBNET|'$UE_IPV4_IMS'|g' install/etc/open5gs/upf.yaml
sed -i 's|UPF_ADVERTISE_IP|'$UPF_ADVERTISE_IP_'|g' install/etc/open5gs/upf.yaml
sed -i 's|MAX_NUM_UE|'$MAX_NUM_UE'|g' install/etc/open5gs/upf.yaml

# Sync docker time
#ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
