import os
from pymongo import MongoClient

mcc = "001"
mnc = "01"
imei = "356938035643803"
imeisv = "4370816125816151"
ki = "8baf473f2f8fd09487cccbd7097c6862"
op = "11111111111111111111111111111111"
amf = "8000"
ip_base = "172.22.0."
ip_min = 50
nr_gnb_ip = "172.22.0.23"
output_yaml = "deploy_ues.yaml"

mongo_host = "localhost"
mongo_port = 27016

client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}")
db = client.open5gs
subscribers = db.subscribers

services_yaml = {}

for i in range(0, 2):
    ue_name = f"nr-ue{i}"
    ip = f"{ip_base}{ip_min+i}"
    imsi = f"{mcc}{mnc}{str(i).zfill(10)}"

    if not subscribers.find_one({"imsi": imsi}):
        sim = {
            "imsi": imsi,
            "schema_version": 1,
            "imeisv": imeisv,
            "msisdn": [],
            "mme_host": [],
            "mme_realm": [],
            "purge_flag": [],
            "access_restriction_data": 32,
            "subscriber_status": 0,
            "operator_determined_barring": 0,
            "network_access_mode": 0,
            "subscribed_rau_tau_timer": 12,
            "security": {
                "k": ki,
                "amf": amf,
                "op": op,
                "opc": None
            },
            "slice": [
                {
                    "sst": 1,
                    "default_indicator": True,
                    "pcc_rule": [],
                    "session": [
                        {
                            "name": "internet",
                            "type": 1,
                            "qos": {
                                "index": 9,
                                "arp": {
                                    "priority_level": 8,
                                    "pre_emption_capability": 1,
                                    "pre_emption_vulnerability": 1
                                }
                            },
                            "ambr": {
                                "uplink": {"value": 1, "unit": 3},
                                "downlink": {"value": 1, "unit": 3}
                            }
                        }
                    ]
                }
            ],
            "ambr": {
                "uplink": {"value": 1, "unit": 3},
                "downlink": {"value": 1, "unit": 3}
            }
        }
        subscribers.insert_one(sim)
        print(f"[+] Inserted SIM for IMSI {imsi}")
    else:
        print(f"[-] SIM for IMSI {imsi} already exists")

    services_yaml[ue_name] = f"""
    {ue_name}:
      image: docker_ueransim
      container_name: {ue_name}
      stdin_open: true
      tty: true
      volumes:
        - ./ueransim:/mnt/ueransim
        - /etc/timezone:/etc/timezone:ro
        - /etc/localtime:/etc/localtime:ro
      environment:
        - COMPONENT_NAME=ueransim-ue
        - MNC={mnc}
        - MCC={mcc}
        - UE1_KI={ki}
        - UE1_OP={op}
        - UE1_AMF={amf}
        - UE1_IMEISV={imeisv}
        - UE1_IMEI={imei}
        - UE1_IMSI={imsi}
        - NR_GNB_IP={nr_gnb_ip}
      expose:
        - "4997/udp"
      cap_add:
        - NET_ADMIN
      privileged: true
      networks:
        default:
          ipv4_address: {ip}
""".rstrip()

# Assemble docker-compose YAML
services_combined = "\n".join(services_yaml.values())

compose = f"""version: '3'
services:
{services_combined}
networks:
  default:
    external:
      name: docker_open5gs_default
"""

# Write YAML to file
with open(output_yaml, "w") as out:
    out.write(compose)

print(f"[✔] Docker Compose file '{output_yaml}' generated.")
