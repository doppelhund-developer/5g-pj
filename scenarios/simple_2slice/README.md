## Deployment description

This custom deployment showcases a slicing scenario by deploying two instances of open5gs SMF and UPF each handling an individual slice configuration.

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
cd custom_deployments/slicing
set -a && source .custom_env && set +a && docker compose -f sa-deploy.yaml up
```

Deploy UERANSIM gNB (RF simulated).

```
set -a && source .custom_env && set +a && docker compose -f nr-gnb.yaml up -d && docker container attach nr_gnb
```

Deploy UERANSIM NR-UE (RF simulated) for first slice.

```
set -a && source .custom_env && set +a && docker compose -f nr-ue.yaml up -d && docker container attach nr_ue
```

Deploy UERANSIM NR-UE (RF simulated) for second slice.

```
set -a && source .custom_env && set +a && docker compose -f nr-ue2.yaml up -d && docker container attach nr_ue2
```

tub5g-srv05:
91.99.142.188

tub5g-srv06:
91.99.20.100