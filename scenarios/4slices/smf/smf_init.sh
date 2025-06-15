#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export IP_ADDR=$(awk 'END{print $1}' /etc/hosts)
export IF_NAME=$(ip r | awk '/default/ { print $5 }')

[ ${#MNC} == 3 ] && EPC_DOMAIN="epc.mnc${MNC}.mcc${MCC}.3gppnetwork.org" || EPC_DOMAIN="epc.mnc0${MNC}.mcc${MCC}.3gppnetwork.org"

UE_IPV4_INTERNET_TUN_IP=$(python3 /mnt/smf/ip_utils.py --ip_range $UE_IPV4_INTERNET_)
UE_IPV4_IMS_TUN_IP=$(python3 /mnt/smf/ip_utils.py --ip_range $UE_IPV4_IMS)

cp /mnt/smf/smf.yaml install/etc/open5gs
if [[ ${DEPLOY_MODE} == 4G ]];
then
    echo "Error: Invalid deployment mode for SMF: '$DEPLOY_MODE'"
    exit 1
fi

sed -i 's|SMF_IP|'$SMF_IP_'|g' install/etc/open5gs/smf.yaml
sed -i 's|SCP_IP|'$SCP_IP'|g' install/etc/open5gs/smf.yaml
sed -i 's|NRF_IP|'$NRF_IP'|g' install/etc/open5gs/smf.yaml
sed -i 's|UPF_IP|'$UPF_IP_'|g' install/etc/open5gs/smf.yaml
sed -i 's|SST|'$SST'|g' install/etc/open5gs/smf.yaml
sed -i 's|SLICE_NAME|'$SLICE_NAME'|g' install/etc/open5gs/smf.yaml
sed -i 's|IPV6_SUBNET_PART|'$IPV6_SUBNET_PART'|g' install/etc/open5gs/smf.yaml
sed -i 's|SMF_DNS1|'$SMF_DNS1'|g' install/etc/open5gs/smf.yaml
sed -i 's|SMF_DNS2|'$SMF_DNS2'|g' install/etc/open5gs/smf.yaml
sed -i 's|SMF_DNS3|'$SMF_DNS3'|g' install/etc/open5gs/smf.yaml
sed -i 's|SMF_DNS4|'$SMF_DNS4'|g' install/etc/open5gs/smf.yaml
sed -i 's|UE_IPV4_INTERNET_TUN_IP|'$UE_IPV4_INTERNET_TUN_IP'|g' install/etc/open5gs/smf.yaml
sed -i 's|UE_IPV4_INTERNET_SUBNET|'$UE_IPV4_INTERNET_'|g' install/etc/open5gs/smf.yaml
sed -i 's|UE_IPV4_IMS_TUN_IP|'$UE_IPV4_IMS_TUN_IP'|g' install/etc/open5gs/smf.yaml
sed -i 's|UE_IPV4_IMS_SUBNET|'$UE_IPV4_IMS'|g' install/etc/open5gs/smf.yaml
sed -i 's|PCSCF_IP|'$PCSCF_IP'|g' install/etc/open5gs/smf.yaml
sed -i 's|MAX_NUM_UE|'$MAX_NUM_UE'|g' install/etc/open5gs/smf.yaml

# Sync docker time
#ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
