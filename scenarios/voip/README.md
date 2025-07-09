## Deployment description

Slicing with VOIP.

## Additional steps

Most of the steps to be followed are similar to the steps mentioned in the [README in the root folder](../../README.md). However, additional steps mentioned below must be taken into account while deploying this custom deployment scenario.

### Loading environmental variables for custom deployment

**Warning**
For custom deployments, you must modify/use only the [**.custom_env**](.custom_env) file rather than the [**.env** in the root folder](../../.env).

```
set -a
source .custom_env
set +a
```

set -a && source .custom_env && set +a

### Scenario deployment

Deploy the 5G SA network consisting of two slices.

```
cd /scenarios/voip
python3 deploy_slices.py
set -a && source .custom_env && set +a && docker compose -f deploy_slices.yaml up
```

Deploy UERANSIM gNB (RF simulated).

```
set -a && source .custom_env && set +a && docker compose -f nr-gnb.yaml up -d && docker container attach nr_gnb
```

run all generated UEs
```
python3 deploy_ues.py
set -a && source .custom_env && set +a && docker compose -f deploy_ues.yaml up
```

tub5g-srv05:
91.99.142.188
metrics:
http://91.99.142.188:3000


tub5g-srv06:
91.99.20.100