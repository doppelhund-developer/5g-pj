import os
import shutil


imsis = [
    "001011234567890",
    "001011234567891",
    "001011234567892"
]

compose_yaml_template = "srsue_5g_zmq_template.yaml"
ue_env_template = ".ue-env-template"


for i in range(1, 3):  # 5 UEs for example
    imsi = imsis[i-1]
    ip = f"172.22.0.{40 + i}"

    ue_env = f".ue{i}-env"
    ue_container_yaml = f"srsue{i}_5g_zmq.yaml"

    # Step 1: Create config file from template
    with open(ue_env, "r") as env_template:
        config = env_template.read()
        config = config.replace("IMSI_PLACEHOLDER", imsi)

    with open(conf_file, "w") as out:
        out.write(config)

    # Step 2: Write Docker Compose file
    compose = f"""
version: '3'
services:
  srs{ue_name}:
    image: docker_srslte
    container_name: srs{ue_name}
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
      - .env
    environment:
      - COMPONENT_NAME={ue_name}
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

    with open(yaml_file, "w") as out:
        out.write(compose)

    # Step 3: Launch container
    os.system(f"docker compose -f {yaml_file} up -d && docker container attach srsue_5g_zmq")
