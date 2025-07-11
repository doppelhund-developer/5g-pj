1. create slice config
set -a && source .custom_env && set +a && python3 deploy_slices.py


2. deploy core network
```
set -a && source .custom_env && set +a && python3 deploy_slices.py
set -a && source .custom_env && set +a && docker compose -f deploy_slices.yaml up
```

3. deploy gnb
```
set -a && source .custom_env && set +a && docker compose -f nr-gnb.yaml up -d && docker container attach nr_gnb
```

4. 
create ue config
```
set -a && source .custom_env && set +a && python3 deploy_ues.py
```

5. run iperf server
set -a && source .custom_env && set +a && docker compose -f test1_server.yaml up

6. run ue
set -a && source .custom_env && set +a && docker compose -f test1_ue.yaml up

7. results
logs/iperf: iperf results
logs/monitor_log.txt: upf container system resources

tub5g-srv05:
91.99.142.188
metrics:
http://91.99.142.188:3000


tub5g-srv06:
91.99.20.100

tub5g-srv03:
49.13.235.12