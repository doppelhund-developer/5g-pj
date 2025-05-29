## container startup
- run open5gs container: `docker compose -f sa-deploy.yaml up`
- srsRAN ZMQ gNB (RF simulated): `docker compose -f srsgnb_zmq.yaml up -d && docker container attach srsgnb_zmq`
- srsRAN ZMQ 5G UE (RF simulated): `docker compose -f srsue_5g_zmq.yaml up -d && docker container attach srsue_5g_zmq`

## management
- add subscriber using command line (default values, USIM Type: OP !! if not hex value): `sudo docker exec -it hss misc/db/open5gs-dbctl add 001011234567895 8baf473f2f8fd09487cccbd7097c6862 11111111111111111111111111111111`

## container config
- run commands within ue context: `docker exec -it srsue_5g_zmq bash`