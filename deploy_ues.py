import os
import shutil


imsis = [
    "001011234567895",
    "001011234567891",
    "001011234567892"
]

kis = [
    "8baf473f2f8fd09487cccbd7097c6862",
    "8baf473f2f8fd09487cccbd7097c6864",
    "8baf473f2f8fd09487cccbd7097c6865"
]

ops = [
    "11111111111111111111111111111111",
    "11111111111111111111111111111113",
    "11111111111111111111111111111114"
]

ips = [
    "172.22.0.34",
    "172.22.0.40",
    "172.22.0.41"
]

compose_yaml_template = "srsue_5g_zmq_template.yaml"
ue_env_template = ".ue-env-template"


for i in range(0, 2):  # 5 UEs for example
    imsi = imsis[i]
    ki = kis[i]
    op = ops[i]
    ip = ips[i]
    ue_name = f"ue{i}"

    ue_env = f".ue{i}-env"
    ue_container_yaml = f"srsue{i}_5g_zmq.yaml"

    # Step 1: Create config file from template
    with open(ue_env_template, "r") as env_template:
        config = env_template.read()
        config = config.replace("$UE_IMSI", imsi)
        config = config.replace("$UE_KI", ki)
        config = config.replace("$UE_OP", op)
        config = config.replace("$UE_IP", ip)

    with open(ue_env, "w") as out:
        out.write(config)

    # Step 2: Write Docker Compose file
    compose = f"""
version: '3'
services:
  srs{ue_name}_5g_zmq:
    image: docker_srslte
    container_name: srs{ue_name}_5g_zmq
    stdin_open: true
    tty: true
    cap_add:
      - NET_ADMIN
    privileged: true
    volumes:
      - ./srslte:/mnt/srslte
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    env_file:
      - {ue_env}
    environment:
      - COMPONENT_NAME=ue_5g_zmq
    expose:
      - "2000/tcp"
      - "2001/tcp"
    networks:
      default:
        ipv4_address: {ip}
networks:
  default:
    external:
      name: docker_open5gs_default
""".strip()

    with open(ue_container_yaml, "w") as out:
        out.write(compose)

    # Step 3: Launch container
    #os.system(f"docker compose -f {yaml_file} up -d && docker container attach srsue_5g_zmq")
