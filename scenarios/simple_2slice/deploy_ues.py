import os
from pymongo import MongoClient
from operator import itemgetter
from time import sleep

mcc = "001"
mnc = "01"
imei = "356938035643803"
imeisv = "4370816125816151"
ki = "8baf473f2f8fd09487cccbd7097c6862"
op = "11111111111111111111111111111111"
amf = "8000"
ip_base = "172.22.0."
ip_min = 50
nr_gnb_ip = "91.99.20.100"
output_yaml = "deploy_ues.yaml"

mongo_host = "91.99.142.188"
mongo_port = 27016

client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}")
db = client.open5gs
subscribers = db.subscribers

services_yaml = {}

ue_slice_config = [
    {
        "sst": 1,
        "sd": "000001",
        "count": 5,
        "apn": "internet",
        "entry_point": "/mnt/simple_2slice/video_streaming.sh",
        "slice_name": "eMBB",
        "component_name": "ueransim-ue",
    },
    {
        "sst": 2,
        "sd": "000001",
        "count": 5,
        "apn": "private",
        "entry_point": "python3 /mnt/simple_2slice/urllc_ue1.py",
        "slice_name": "URLLC",
        "component_name": "ueransim-ue2",
    },
]


def create_ue_container_config(i, ue_name, slice_config):
    ip = f"{ip_base}{ip_min+i}"
    imsi = f"{mcc}{mnc}{str(i).zfill(10)}"

    sst, sd, component_name, apn, entry_point = itemgetter(
        "sst", "sd", "component_name", "apn", "entry_point"
    )(slice_config)

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
            "security": {"k": ki, "amf": amf, "op": op, "opc": None},
            "slice": [
                {
                    "sst": sst,
                    "sd": sd,
                    "default_indicator": True,
                    "pcc_rule": [],
                    "session": [
                        {
                            "name": apn,
                            "type": 1,
                            "qos": {
                                "index": 9,
                                "arp": {
                                    "priority_level": 8,
                                    "pre_emption_capability": 1,
                                    "pre_emption_vulnerability": 1,
                                },
                            },
                            "ambr": {
                                "uplink": {"value": 1, "unit": 3},
                                "downlink": {"value": 1, "unit": 3},
                            },
                        }
                    ],
                }
            ],
            "ambr": {
                "uplink": {"value": 1, "unit": 3},
                "downlink": {"value": 1, "unit": 3},
            },
        }
        subscribers.insert_one(sim)
        print(f"[+] Inserted SIM for IMSI {imsi}")
    else:
        print(f"[-] SIM for IMSI {imsi} already exists")

    # TODO use template file for better formatting
    container = f"""    {ue_name}:
        image: docker_ueransim
        container_name: {ue_name}
        stdin_open: true
        tty: true
        volumes:
            - ./ueransim:/mnt/ueransim
            - ./:/mnt/simple_2slice
            - /etc/timezone:/etc/timezone:ro
            - /etc/localtime:/etc/localtime:ro
        environment:
            - COMPONENT_NAME={component_name}
            - MNC={mnc}
            - MCC={mcc}
            - UE_KI={ki}
            - UE_OP={op}
            - UE_AMF={amf}         
            - UE_IMEISV={imeisv}
            - UE_IMEI={imei}
            - UE_IMSI={imsi}
            - NR_GNB_IP={nr_gnb_ip}
            - ENTRY_POINT={entry_point}
        expose:
            - "4997/udp"
        cap_add:
            - NET_ADMIN
        privileged: true
        networks:
            default:
                ipv4_address: {ip}
""".rstrip()

    return container


def main():
    print("WARNING !!!! deleting all documents in subscriber collection in 3s")
    sleep(3)
    subscribers.delete_many({})

    containers = []

    i = 0
    for slice in ue_slice_config:
        for _ in range(0, slice["count"]):
            ue_name = f"nr-{slice["slice_name"]}-ue{i}"
            containers.append(create_ue_container_config(i, ue_name, slice))
            i += 1

    services_combined = "\n".join(containers)
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


if __name__ == "__main__":
    main()
