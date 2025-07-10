"""
generates one compose file per test case
"""

import os, uuid, shutil
from pymongo import MongoClient
from operator import itemgetter
from time import sleep
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".custom_env"
load_dotenv(dotenv_path=env_path)

mcc = "001"
mnc = "01"
imei = "356938035643803"
imeisv = "4370816125816151"
ki = "8baf473f2f8fd09487cccbd7097c6862"
op = "11111111111111111111111111111111"
amf = "8000"
ip_base = "172.22.0."
iperf_ip_base = "172.22.1."
ip_min = 50
iperf_ip_min = 0
nr_gnb_ip = os.getenv("NR_GNB_IP")
output_yaml = "deploy_ues.yaml"

mongo_host = "localhost"
mongo_port = 27016

scenario_name = "test_bandwidth_local"

client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}")
db = client.open5gs
subscribers = db.subscribers

services_yaml = {}

upf_ips = [
    os.getenv("UPF_IP"),
    os.getenv("UPF2_IP"),
    os.getenv("UPF3_IP"),
    os.getenv("UPF4_IP"),
]

ue_slice_config = []


def insert_sim_details(imsi, imeisv, sst, sd, apn):
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


def create_ue_container_config(i, ue_name, slice_config, entry_point, entry_args):
    ip = f"{ip_base}{ip_min+i}"
    imsi = f"{mcc}{mnc}{str(i).zfill(10)}"

    sst, sd, component_name, apn = itemgetter(
        "sst",
        "sd",
        "component_name",
        "apn",
    )(slice_config)

    insert_sim_details(imsi, imeisv, sst, sd, apn)

    # TODO use template file for better formatting
    container = f"""    {ue_name}:
        image: docker_ueransim
        container_name: {ue_name}
        stdin_open: true
        tty: true
        volumes:
            - ./ueransim:/mnt/ueransim
            - ./:/mnt/{scenario_name}
            - ../../venv:/mnt/venv
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
            - SST={sst}
            - SLICE_NAME={apn}
            - NR_GNB_IP={nr_gnb_ip}
            - ENTRY_POINT={entry_point}
            - ENTRY_ARGS={entry_args}
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


def create_iperf_container_config(i, ip):
    # TODO use template file for better formatting
    container = f"""    iperf_server{i}:
        image: docker_ueransim
        container_name: iperf_server{i}
        stdin_open: true
        tty: true
        command: -s
        volumes:
            - ./:/mnt/{scenario_name}
            - /etc/timezone:/etc/timezone:ro
            - /etc/localtime:/etc/localtime:ro
        privileged: true
        networks:
            default:
                ipv4_address: {ip}
""".rstrip()

    return container


def concat_and_store_compose(container_configs, output):
    services_combined = "\n".join(container_configs)
    compose = f"""version: '3'
services:
{services_combined}
networks:
    default:
        external:
            name: docker_open5gs_default
  """

    # Write YAML to file
    with open(output, "w") as out:
        out.write(compose)

    print(f"[✔] Docker Compose file '{output}' generated.")


def test_single_ue_max_bw(i):
    ue_name = "nr-eMBB-0"
    iperf_logs_dir = f"iperf_logs/{ue_name}"
    slice = {
        "sst": 1,
        "sd": "000001",
        "count": 4,
        "apn": "eMBB",
        "slice_name": "eMBB",
        "component_name": "ueransim-ue",
    }
    iperf_ip = f"{iperf_ip_base}{iperf_ip_min+i}"

    os.makedirs(iperf_logs_dir, exist_ok=True)

    return [
        [create_iperf_container_config(i, iperf_ip)],
        [
            create_ue_container_config(
                0,
                ue_name,
                slice,
                "/usr/bin/iperf3",
                f"-c {iperf_ip} -u -t 10 -b 10M -J /mnt/{scenario_name}/{iperf_logs_dir}/log.json",
            )
        ],
    ]


def main():
    print("WARNING !!!! deleting all documents in subscriber collection in 3s")
    sleep(3)
    subscribers.delete_many({})

    i = 0
    s, u = test_single_ue_max_bw(i)
    concat_and_store_compose(s, "test1_server.yaml")
    concat_and_store_compose(u, "test1_ue.yaml")
    i += 1


if __name__ == "__main__":
    main()
