import os
import shutil


imsis = [
    "001011234567890",
    "001011234567891",
    "001011234567892"
]


base_ip = 172220035  # 172.22.0.35 → expressed as integer

for i in range(1, 2):  # 5 UEs for example
    imsi = imsis[i-1]
    ki = "8baf473f2f8fd09487cccbd7097c6862"
    op = "11111111111111111111111111111111"
    ip = f"172.22.0.{35 + i}"

    ue_name = f"ue_5g_zmq{i}"
    conf_file = f"srslte/{ue_name}.conf"
    yaml_file = f"{ue_name}.yaml"

    # Step 1: Create config file from template
    with open("srslte/ue_5g_zmq_template.conf", "r") as template:
        config = template.read()
        config = config.replace("IMSI_PLACEHOLDER", imsi)
        config = config.replace("KI_PLACEHOLDER", ki)
        config = config.replace("OP_PLACEHOLDER", op)
        config = config.replace("UE_IP_PLACEHOLDER", ip)

    with open(conf_file, "w") as out:
        out.write(config)

    # Step 2: Write Docker Compose file
    compose = f"""
version: '3'
services:
  {ue_name}:
    image: docker_srsran
    container_name: {ue_name}
    stdin_open: true
    tty: true
    privileged: true
    volumes:
      - ./srsran:/mnt/srslte
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    env_file:
      - .env
    environment:
      - COMPONENT_NAME={ue_name}
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
    os.system(f"docker compose -f {yaml_file} up -d")
