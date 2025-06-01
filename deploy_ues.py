import os
import shutil


mcc = "001"
mnc = "01"
ki = "8baf473f2f8fd09487cccbd7097c6862"
op = "11111111111111111111111111111111"
amf = "8000"
ip_base = "172.22.0."
ip_min = 50

nr_gnb_ip = "172.22.0.23"

output_yaml = "deploy_ues.yaml"

#TODO add UE program entry point to excute after creation, modify the init shell script

services = ""

for i in range(0, 2):
    ue_name = f"nr-ue{i}"
    ip = f"{ip_base}{ip_min+i}"
    imsi = f"{mcc}{mnc}{str(i).zfill(10)}"

    service = f"""
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
    - UE1_IMEISV=4370816125816151
    - UE1_IMEI=356938035643803
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
""".strip()
    services += service


compose = f"""
version: '3'
services:
  {services}
networks:
  default:
    external:
      name: docker_open5gs_default
""".strip()

with open(output_yaml, "w") as out:
    out.write(compose)

    # Step 3: Launch container
    #os.system(f"docker compose -f {yaml_file} up -d && docker container attach srsue_5g_zmq")
