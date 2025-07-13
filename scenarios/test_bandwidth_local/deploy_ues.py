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
iperf_ip_min = 1
nr_gnb_ip = os.getenv("NR_GNB_IP")
output_yaml = "deploy_ues.yaml"

mongo_host = "localhost"
mongo_port = 27016

scenario_name = "test_bandwidth_local"

docker_local_folder = "/mnt/test_folder" #the path at which this local test folder is mounted at

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

smf_ips=[
   os.getenv('SMF_IP'),
   os.getenv('SMF2_IP'),
   os.getenv('SMF3_IP'),
   os.getenv('SMF4_IP'),
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
            - ./:/mnt/test_folder
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
        image: networkstatic/iperf3
        container_name: iperf_server{i}
        stdin_open: true
        tty: true
        command: -s
        volumes:
            - ./:/mnt/test_folder
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


def test_single_ue_max_bw():
    test_name = "test1"
    ue_name = "nr-eMBB-0"
    iperf_logs_dir = f"logs/iperf/{test_name}"
    
    slice = {
        "sst": 1,
        "sd": "000001",
        "count": 4,
        "apn": "eMBB",
        "slice_name": "eMBB",
        "component_name": "ueransim-ue",
    }
    iperf_server_ip = f"{iperf_ip_base}{iperf_ip_min}"

    os.makedirs(iperf_logs_dir, exist_ok=True)

    return [
        [create_iperf_container_config(0, iperf_server_ip)],
        [
            create_ue_container_config(
                0,
                ue_name,
                slice,
                "/mnt/test_folder/iperf_client.sh",
                f"{iperf_server_ip} /mnt/test_folder/{iperf_logs_dir}/{ue_name}.json {upf_ips[0]} 200M",
            )
        ],
    ]

#2 (or more ) ues in same slice, some ues generate heavy traffic, some ues generate (lighter) critical traffic
# -> measure latency, packet drop, upf load
def test2():
    test_name = "test2"
    
    iperf_logs_dir = f"logs/iperf/{test_name}"
    os.makedirs(iperf_logs_dir, exist_ok=True)

    slice = {
        "sst": 1,
        "sd": "000001",
        "count": 4,
        "apn": "eMBB",
        "slice_name": "eMBB",
        "component_name": "ueransim-ue",
    }
    
    s = []
    u = []
    embb_ue_count = 2
    urllc_ue_count = 1
    ue_index = 0
    
    #create high bw ues
    #TODO remove redundant code
    for i in range(0, embb_ue_count):
        ue_name = f"nr-eMBB-{i}"
        iperf_log_file = f"{docker_local_folder}/logs/iperf/{test_name}/{ue_name}.json"
        
        iperf_server_ip = f"{iperf_ip_base}{iperf_ip_min+ue_index}"
        
        s.append(create_iperf_container_config(ue_index, iperf_server_ip))
        u.append(
            create_ue_container_config(
                ue_index,
                ue_name,
                slice,
                "/mnt/test_folder/iperf_client.sh",
                f"{iperf_server_ip} {iperf_log_file} {upf_ips[0]} 100M {smf_ips[0]}",
            )
        )
        
        ue_index += 1
    
    #create critical ues
    for i in range(0, urllc_ue_count):
        ue_name = f"nr-URLLC-{i}"
        iperf_log_file = f"{docker_local_folder}/logs/iperf/{test_name}/{ue_name}.json"
        
        iperf_server_ip = f"{iperf_ip_base}{iperf_ip_min+ue_index}"
        
        s.append(create_iperf_container_config(ue_index, iperf_server_ip))
        u.append(
            create_ue_container_config(
                ue_index,
                ue_name,
                slice,
                "/mnt/test_folder/iperf_client.sh",
                f"{iperf_server_ip} {iperf_log_file} {upf_ips[0]} 10M {smf_ips[0]}",
            )
        )
        
        ue_index += 1

    return s, u

# eMBB and URLLC ues are in differnt slices
# -> measure latency, packet drop
def test3():
    test_name = "test3"
    
    iperf_logs_dir = f"logs/iperf/{test_name}"
    os.makedirs(iperf_logs_dir, exist_ok=True)

    eMBB_slice = {
        "sst": 1,
        "sd": "000001",
        "count": 2,
        "apn": "eMBB",
        "slice_name": "eMBB",
        "component_name": "ueransim-ue",
    }
    
    URLLC_slice = {
        "sst": 2,
        "sd": "000001",
        "count": 2,
        "apn": "URLLC",
        "slice_name": "URLLC",
        "component_name": "ueransim-ue",
    }
    
    s = []
    u = []
    ue_index = 0
    
    #create high bw ues
    #TODO remove redundant code
    for i in range(0, eMBB_slice["count"]):
        ue_name = f"nr-eMBB-{i}"
        iperf_log_file = f"{docker_local_folder}/logs/iperf/{test_name}/{ue_name}.json"
        
        iperf_server_ip = f"{iperf_ip_base}{iperf_ip_min+ue_index}"
        
        s.append(create_iperf_container_config(ue_index, iperf_server_ip))
        u.append(
            create_ue_container_config(
                ue_index,
                ue_name,
                eMBB_slice,
                "/mnt/test_folder/iperf_client.sh",
                f"{iperf_server_ip} {iperf_log_file} {upf_ips[0]} 100M {smf_ips[0]}",
            )
        )
        
        ue_index += 1
    
    #create critical ues
    for i in range(0, URLLC_slice["count"]):
        ue_name = f"nr-URLLC-{i}"
        iperf_log_file = f"{docker_local_folder}/logs/iperf/{test_name}/{ue_name}.json"
        
        iperf_server_ip = f"{iperf_ip_base}{iperf_ip_min+ue_index}"
        
        s.append(create_iperf_container_config(ue_index, iperf_server_ip))
        u.append(
            create_ue_container_config(
                ue_index,
                ue_name,
                URLLC_slice,
                "/mnt/test_folder/iperf_client.sh",
                f"{iperf_server_ip} {iperf_log_file} {upf_ips[1]} 10M {smf_ips[1]}",
            )
        )
        
        ue_index += 1

    return s, u
    
    
#TODO add script to run iperf with different settings, parse and save to file to analyze

def main():
    print("WARNING !!!! deleting all documents in subscriber collection in 3s")
    sleep(3)
    subscribers.delete_many({})

    #TODO ts looks ass
    """ s, u = test_single_ue_max_bw()
    concat_and_store_compose(s, "test1_server.yaml")
    concat_and_store_compose(u, "test1_ue.yaml")
    
    s, u = test2()
    concat_and_store_compose(s, "test2_server.yaml")
    concat_and_store_compose(u, "test2_ue.yaml") """
    
    s, u = test3()
    concat_and_store_compose(s, "test3_server.yaml")
    concat_and_store_compose(u, "test3_ue.yaml")


if __name__ == "__main__":
    main()
