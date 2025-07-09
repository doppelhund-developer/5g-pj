from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent / ".custom_env"
load_dotenv(dotenv_path=env_path)


output_yaml = "deploy_slices.yaml"

services_yaml = {}

#sliceing:
slice_names = [
   os.getenv('SLICE_NAME_1'),
   os.getenv('SLICE_NAME_2'),
   os.getenv('SLICE_NAME_3'),
   os.getenv('SLICE_NAME_4'),
]
#upf
upf_ips = [
   os.getenv('UPF_IP'),
   os.getenv('UPF2_IP'),
   os.getenv('UPF3_IP'),
   os.getenv('UPF4_IP'),
]

#smf
smf_ips=[
   os.getenv('SMF_IP'),
   os.getenv('SMF2_IP'),
   os.getenv('SMF3_IP'),
   os.getenv('SMF4_IP'),
]

smf_dns = [
   os.getenv('SMF_DNS1'),
   os.getenv('SMF_DNS2'),
   os.getenv('SMF_DNS3'),
   os.getenv('SMF_DNS4'),
]

upf_advertise_ips = [
   os.getenv('UPF_ADVERTISE_IP'),
   os.getenv('UPF2_ADVERTISE_IP'),
   os.getenv('UPF3_ADVERTISE_IP'),
   os.getenv('UPF4_ADVERTISE_IP'),
]

ipv6_subnet_parts=[
   os.getenv('IPV6_SUBNET_PART_1'),
   os.getenv('IPV6_SUBNET_PART_2'),
   os.getenv('IPV6_SUBNET_PART_3'),
   os.getenv('IPV6_SUBNET_PART_4'),
   
]

ue_ipv4_subnet_ranges = [
   os.getenv('UE_IPV4_EMBB'),
   os.getenv('UE_IPV4_URLLC'),
   os.getenv('UE_IPV4_MIOT'),
   os.getenv('UE_IPV4_PRIVATE'),
   ]



for slice in slice_names:
  idx = slice_names.index(slice)
  sst = idx + 1
  #smf
  services_yaml["smf"+str(sst)] = f"""  {"smf" + str(sst)}:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
      - amf
    container_name: smf{sst}
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=smf
      - DEPLOY_MODE=5G
      - SST={sst}
      - SLICE_NAME={slice}
      - SMF_IP_={smf_ips[idx]}
      - UPF_IP_={upf_ips[idx]}
      - UE_IPV4_INTERNET_={ue_ipv4_subnet_ranges[idx]}
      - IPV6_SUBNET_PART={ipv6_subnet_parts[idx]}
    volumes:
      - ./smf:/mnt/smf
      - ./log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "3868/udp"
      - "3868/tcp"
      - "3868/sctp"
      - "5868/udp"
      - "5868/tcp"
      - "5868/sctp"
      - "8805/udp"
      - "2123/udp"
      - "7777/tcp"
      - "9091/tcp"
    networks:
      default:
        ipv4_address: {smf_ips[idx]} 
        """.rstrip()

  #upf
  services_yaml["upf"+str(sst)] = f"""  {"upf" + str(sst)}:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
      - smf{sst}
    container_name: upf{sst}
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=upf
      - DEPLOY_MODE=5G
      - SST={sst}
      - SLICE_NAME={slice}
      - SMF_IP_={smf_ips[idx]}
      - UPF_IP_={upf_ips[idx]}
      - UPF_ADVERTISE_IP_={upf_advertise_ips[idx]}
      - UE_IPV4_INTERNET_={ue_ipv4_subnet_ranges[idx]}
      - IPV6_SUBNET_PART={ipv6_subnet_parts[idx]}
    volumes:
      - ./upf:/mnt/upf
      - ./log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "2152/udp"
      - "8805/udp"
      - "9091/tcp"
    # ports:
    #   - "2152:2152/udp"
    cap_add:
      - NET_ADMIN
    privileged: true
    sysctls:
      - net.ipv4.ip_forward=1
      #- net.ipv6.conf.all.disable_ipv6=0
    networks:
      default:
        ipv4_address: {upf_ips[idx]} 
        """.rstrip()

services_yaml["rest"] = r"""  mongo:
    image: mongo:6.0
    container_name: mongo
    command: --bind_ip 0.0.0.0
    env_file:
      - .custom_env
    volumes:
      - mongodbdata:/data/db
      - mongodbdata:/data/configdb
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "27017/udp"
      - "27017/tcp"
    ports:
      - "27016:27017"
    networks:
      default:
        ipv4_address: ${MONGO_IP}
  webui:
    image: docker_open5gs
    container_name: webui
    depends_on:
      - mongo
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=webui
    volumes:
      - ../../webui:/mnt/webui
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "9999/tcp"
    ports:
      - "9999:9999/tcp"
    networks:
      default:
        ipv4_address: ${WEBUI_IP}
  nrf:
    image: docker_open5gs
    container_name: nrf
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=nrf
    volumes:
      - ../../nrf:/mnt/nrf
      - ../../log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "7777/tcp"
    networks:
      default:
        ipv4_address: ${NRF_IP}
  scp:
    image: docker_open5gs
    depends_on:
      - nrf
    container_name: scp
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=scp
    volumes:
      - ../../scp:/mnt/scp
      - ../../log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "7777/tcp"
    networks:
      default:
        ipv4_address: ${SCP_IP}
  ausf:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
    container_name: ausf
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=ausf
    volumes:
      - ../../ausf:/mnt/ausf
      - ../../log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "7777/tcp"
    networks:
      default:
        ipv4_address: ${AUSF_IP}
  udr:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
      - mongo
    container_name: udr
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=udr
    volumes:
      - ../../udr:/mnt/udr
      - ../../log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "7777/tcp"
    networks:
      default:
        ipv4_address: ${UDR_IP}
  udm:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
    container_name: udm
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=udm
    volumes:
      - ../../udm:/mnt/udm
      - ../../log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "7777/tcp"
    networks:
      default:
        ipv4_address: ${UDM_IP}
  amf:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
      - ausf
      - udm
      - udr
      - pcf
      - bsf
    container_name: amf
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=amf
    volumes:
      - ./amf:/mnt/amf
      - ./log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "38412/sctp"
      - "7777/tcp"
      - "9091/tcp"
    ports:
      - "38412:38412/sctp"
    networks:
      default:
        ipv4_address: ${AMF_IP}
  pcf:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
      - mongo
    container_name: pcf
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=pcf
    volumes:
      - ../../pcf:/mnt/pcf
      - ../../log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "7777/tcp"
      - "9091/tcp"
    networks:
      default:
        ipv4_address: ${PCF_IP}
  bsf:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
      - mongo
    container_name: bsf
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=bsf
    volumes:
      - ../../bsf:/mnt/bsf
      - ../../log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "7777/tcp"
    networks:
      default:
        ipv4_address: ${BSF_IP}
  nssf:
    image: docker_open5gs
    depends_on:
      - nrf
      - scp
      - mongo
    container_name: nssf
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=nssf
    volumes:
      - ./nssf:/mnt/nssf
      - ./log:/open5gs/install/var/log/open5gs
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "7777/tcp"
    networks:
      default:
        ipv4_address: ${NSSF_IP}
  kamailio:
    image: kamailio_voip
    container_name: kamailio
    env_file:
      - .custom_env
    environment:
      - COMPONENT_NAME=kamailio
    volumes:
      - ../../kamailio_voip/kamailio_init.sh:/kamailio_init.sh
      - ../../kamailio_voip/:/mnt/kamailio_voip
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "5060/tcp"
    ports:
      - "5060:5060"
    networks:
      default:
        ipv4_address: ${KAMAILIO_IP}
  db:
    image: mysql:8.0.42
    command: mysqld --default-authentication-plugin=mysql_native_password
    container_name: mysql
    expose:
      - "3306/tcp"
      - "3306/udp"
    ports:
      - "3307:3306"
    volumes:
      - type: tmpfs
        target: /var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=1234
    networks:
      default:
        ipv4_address: ${MYSQL_IP}
  metrics:
    build: ../../metrics
    image: docker_metrics
    container_name: metrics
    env_file:
      - .custom_env
    volumes:
      - ../../metrics:/mnt/metrics
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    expose:
      - "9090/tcp"
    ports:
      - "9090:9090/tcp"
    networks:
      default:
        ipv4_address: ${METRICS_IP}
  grafana:
    image: grafana/grafana:11.3.0
    container_name: grafana
    env_file:
      - .custom_env
    volumes:
      - grafana_data:/var/lib/grafana
      - ../../grafana/:/etc/grafana/provisioning/
      - ../../grafana:/mnt/grafana
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USERNAME}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      #- GF_INSTALL_PLUGINS=${GRAFANA_INSTALL_PLUGINS}
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
      - GF_PATHS_DATA=/var/lib/grafana
      - METRICS_IP=${METRICS_IP}
    expose:
      - "3000/tcp"
    ports:
      - "3000:3000/tcp"
    networks:
      default:
        ipv4_address: ${GRAFANA_IP}
networks:
  default:
    name: docker_open5gs_default
    ipam:
      config:
        - subnet: ${TEST_NETWORK}
volumes:
  grafana_data:
    name: grafana_data
  mongodbdata:
    name: docker_open5gs_mongodbdata
"""

# Assemble docker-compose YAML
services_combined = "\n".join(services_yaml.values())

compose = f"""services:
{services_combined}
"""

# Write YAML to file
with open(output_yaml, "w") as out:
    out.write(compose)

print(f"[✔] Docker Compose file '{output_yaml}' generated.")
