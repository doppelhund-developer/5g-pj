### Scenario deployment

Deploy the 5G SA and split it dynamically into 4 slices.

Navigate to this directory
```
cd ./scenarios/variable_slices
```

```
python3 deploy_slices.py
set -a && source .custom_env && set +a && docker compose -f deploy_slices.yaml up
```

Deploy UERANSIM gNB (RF simulated).

```
set -a && source .custom_env && set +a && docker compose -f nr-gnb.yaml up -d && docker container attach nr_gnb
```

Deploy UERANSIM UEs
```
python3 deploy_ues.py
set -a && source .custom_env && set +a && docker compose -f deploy_ues.yaml up
```

tub5g-srv05:
91.99.142.188

tub5g-srv06:
91.99.20.100