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
ip_min = 50
nr_gnb_ip = os.getenv('172.22.0.23')
output_yaml = "deploy_ues.yaml"

mongo_host = "localhost"
mongo_port = 27016

scenario_name = "voip"

sip_password = "gg"
sip_domain = os.getenv('KAMAILIO_IP')
baresip_config_template_dir = "baresip_config_template"
baresip_configs_dir = "baresip_configs"

client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}")
db = client.open5gs
subscribers = db.subscribers

services_yaml = {}

ue_slice_config = [
    {
        "sst": 1,
        "sd": "000001",
        "count": 2,
        "apn": "eMBB",
        "entry_point": f"/mnt/{scenario_name}/video_streaming.sh",
        "entry_args": "https://www.youtube.com/watch?v=wkAp5x3Z_gc",
        "slice_name": "eMBB",
        "component_name": "ueransim-ue",
    },
    {
        "sst": 2,
        "sd": "000001",
        "count": 2,
        "apn": "URLLC",
        "entry_point": "/usr/bin/python3.10",
        "entry_args": f"/mnt/{scenario_name}/urllc_ue1.py",
        "slice_name": "URLLC",
        "component_name": "ueransim-ue",
    },
]

voip_ue_config = [
    {
        "sst": 1,
        "sd": "000001",
        "pair_count": 15,
        "apn": "eMBB",
        "slice_name": "eMBB",
        "component_name": "ueransim-ue"
    },
]


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
        "sst", "sd", "component_name", "apn",
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
            - ./:/mnt/voip
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


def add_sip_user(user, password):
    os.system(f"docker exec kamailio kamctl add {user} {password}")

def add_baresip_config(user, password, sip_domain, script_text):

    if not os.path.isdir(baresip_configs_dir):
        os.mkdir(baresip_configs_dir)

    shutil.copytree(baresip_config_template_dir, f"{baresip_configs_dir}/{user}")
    
    with open(f"{baresip_configs_dir}/{user}/accounts", "r+") as f:
        t = f.read()
        f.seek(0)
        
        c = t.replace("$BARESIP_ACCOUNT_CONFIG", f"sip:{user}@{sip_domain};auth_pass={password};answermode=auto;audio_source=aufile,/mnt/voip/baresip_configs/{user}/audio_source.wav")
        
        f.write(c)
        f.truncate()
    
    with open(f"{baresip_configs_dir}/{user}/uuid", "w") as f:
        u = uuid.uuid4()
        f.write(str(u))

    if script_text:
        with open(f"{baresip_configs_dir}/{user}/baresip_init.sh", "a") as f:
            f.write(script_text)
    

def main():
    print("WARNING !!!! deleting all documents in subscriber collection in 3s")
    sleep(3)
    subscribers.delete_many({})

    containers = []

    i = 0
    for slice in ue_slice_config:
        for _ in range(0, slice["count"]):
            ue_name = f"nr-{slice["slice_name"]}-ue{i}"
            containers.append(create_ue_container_config(i, ue_name, slice, slice["entry_point"], slice["entry_args"]))
            i += 1
   
    if os.path.isdir(baresip_configs_dir):
        shutil.rmtree(baresip_configs_dir)


    for voip_ue_slice in voip_ue_config:
        for _ in range(0, voip_ue_slice["pair_count"]):
            n1 = f"voip_listener{i}"
            containers.append(create_ue_container_config(i, n1, voip_ue_slice, f"/usr/local/bin/baresip", f"-f /mnt/voip/{baresip_configs_dir}/{n1}"))
            add_sip_user(n1, sip_password)
            add_baresip_config(n1, sip_password, sip_domain, None)
            i += 1
            
            n2 = f"voip_caller{i}"
            containers.append(create_ue_container_config(i, n2, voip_ue_slice, f"/mnt/voip/{baresip_configs_dir}/{n2}/baresip_init.sh", ""))
            add_sip_user(n2, sip_password)
            add_baresip_config(n2, sip_password, sip_domain, "/usr/local/bin/baresip" + f" -f /mnt/voip/{baresip_configs_dir}/{n2} -e '/dial sip:{n1}@{sip_domain}'")
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
