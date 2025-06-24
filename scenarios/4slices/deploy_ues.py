from pymongo import MongoClient
from operator import itemgetter
from time import sleep
from dotenv import load_dotenv
import os
from pathlib import Path
import mysql.connector
import requests
import json
env_path = Path(__file__).parent / ".custom_env"
load_dotenv(dotenv_path=env_path)

mcc = "001"
mnc = "01"
imei = "356938035643803"
#imeisv = "4370816125816151"
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

#pyhss api
base_url = 'http://localhost:8080'
headers = {"Content-Type": "application/json"}

mysql_config = {
    'user': 'pyhss',
    'password': 'ims_db_pass',
    'host': os.getenv('MYSQL_IP'),# todo replace
    'database': 'ims_hss_db',
    'raise_on_warnings': True,
}

services_yaml = {}

slice_names = [
   os.getenv('SLICE_NAME_1'),
   os.getenv('SLICE_NAME_2'),
   os.getenv('SLICE_NAME_3'),
   os.getenv('SLICE_NAME_4'),
]

ue_slice_config = [
    {
        "sst": 1,
        "sd": "000001",
        "count": 2,
        "apn": slice_names[0],
        "entry_point": "",
        "slice_name": slice_names[0],
        "component_name": "ueransim-ue",
    },
    {
        "sst": 2,
        "sd": "000001",
        "count": 2,
        "apn": slice_names[1],
        "entry_point": "",
        "slice_name": slice_names[1],
        "component_name": "ueransim-ue",
    },
    {
        "sst": 3,
        "sd": "000001",
        "count": 2,
        "apn": slice_names[2],
        "entry_point": "",
        "slice_name": slice_names[2],
        "component_name": "ueransim-ue",
    },
    {
        "sst": 4,
        "sd": "000001",
        "count": 2,
        "apn": slice_names[3],
        "entry_point": "",
        "slice_name": slice_names[3],
        "component_name": "ueransim-ue",
    },
]


def create_ue_container_config(i, ue_name, slice_config, slice_number):
    ip = f"{ip_base}{ip_min+i}"
    imsi = f"{mcc}{mnc}{str(i).zfill(10)}"
    
    sst, sd, component_name, apn = itemgetter("sst", "sd", "component_name", "apn")(slice_config)
    imeisv = str(slice_number) + (str(i).zfill(12))
    msisdn = str(slice_number) + (str(i).zfill(10))
    if not subscribers.find_one({"imsi": imsi}):
        sim = {
            "imsi": imsi,
            "schema_version": 1,
            "imeisv": imeisv,
            "msisdn": [msisdn],
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
            - /etc/timezone:/etc/timezone:ro
            - /etc/localtime:/etc/localtime:ro
        environment:
            - COMPONENT_NAME=ueransim-ue
            - MNC={mnc}
            - MCC={mcc}
            - UE_KI={ki}
            - UE_OP={op}
            - UE_AMF={amf}         
            - UE_IMEISV={imeisv}
            - UE_IMEI={imei}
            - UE_IMSI={imsi}
            - NR_GNB_IP={nr_gnb_ip}
            - NR_GNB_IP={nr_gnb_ip}
            - SST={sst}
            - SLICE_NAME={apn}
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

def pyhss_inject(i, slice_config, apn_ids, slice_number):
    imsi = f"{mcc}{mnc}{str(i).zfill(10)}"
    
    sst, sd, component_name, apn = itemgetter("sst", "sd", "component_name", "apn")(slice_config)
    imeisv = str(slice_number) + (str(i).zfill(12))
    msisdn = str(slice_number) + (str(i).zfill(10))

    data = {
        "ki": ki,
        "opc": op,#??
        "amf": "8000",
        "sqn": 0,
        "imsi": imsi
    }
    response = requests.put(str(base_url) + '/auc/', data=json.dumps(data), headers=headers)
    print(response)
    auc_id = response.json()["auc_id"]
    print(imsi, msisdn)
    data = {
        "imsi": imsi,
        "enabled": True,
        "auc_id": int(auc_id),
        "default_apn": str(apn_ids[apn]),
        "apn_list": f"{apn_ids[apn]},{apn_ids["ims"]}",
        "msisdn": msisdn, # dont know of this works
        "ue_ambr_dl": 0,
        "ue_ambr_ul": 0
    }
    
    response = requests.put(str(base_url) + '/subscriber/', data=json.dumps(data), headers=headers)
    print(response)



    data = {
        "imsi": imsi,
        "msisdn": msisdn,
        "sh_profile": "string",
        "scscf_peer": "scscf.ims.mnc001.mcc001.3gppnetwork.org",
        "msisdn_list": f"[{msisdn}]",
        "ifc_path": "default_ifc.xml",
        "scscf": "sip:scscf.ims.mnc001.mcc001.3gppnetwork.org:6060",
        "scscf_realm": "ims.mnc001.mcc001.3gppnetwork.org"
    }
    
    response = requests.put(str(base_url) + '/ims_subscriber/', data=json.dumps(data), headers=headers)
    print(response)




def main():
    #print("WARNING !!!! deleting all documents in subscriber collection in 3s")
    sleep(3)
    subscribers.delete_many({})

    #delete pyhss data
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        # Example query
        cursor.execute("DELETE FROM ims_subscriber;")
        cursor.execute("DELETE FROM subscriber;")
        cursor.execute("DELETE FROM auc;")
        cursor.execute("DELETE FROM apn;")
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    #create ims apn:
    data = {
        "apn": "ims",
        "apn_ambr_dl": 0,
        "apn_ambr_ul": 0
    }
    response = requests.put(str(base_url) + '/apn/', data=json.dumps(data), headers=headers)
    apn_ids = {
        "ims": response.json()["apn_id"]
    }
    
    containers = []

    i = 0
    for slice in ue_slice_config:

        #create slice apn:
        data = {
            "apn": slice["slice_name"],
            "apn_ambr_dl": 0,
            "apn_ambr_ul": 0
        }
        response = requests.put(str(base_url) + '/apn/', data=json.dumps(data), headers=headers)
        apn_ids.update({slice["slice_name"]: response.json()["apn_id"]})

        for _ in range(0, slice["count"]):
            ue_name = f"nr-{slice["slice_name"]}-ue{i}"
            print(ue_name)
            containers.append(
                create_ue_container_config(
                    i, ue_name, slice, ue_slice_config.index(slice)
                )
            )
            i+=1

            #inject subscriber data
            pyhss_inject(i, slice, apn_ids, ue_slice_config.index(slice))


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
