# TODO
- upf_monitor.py: push data to prometheus - DONE
- grafana graphs for resource usage of UPF & SMF - DONE
- run different slicing setups and ue bandwidths and compare results
    - multi ue, same slice
    - multi ue, different slices
    
- port local version to server
- dynamic instantiation of new slices under heavy load?
    - slice instatiation time (how long till new slice online and ready)
    - how are slices under load relieved (check upf_monitor.py stats)

- PCF & UDR sometimes fail to init because of mongodb timeout, causes ue registration to fail (containers started before mongodb is ready)

# KPIs
- throughput/bandwidth: done (iperf logs)
- latency: done (iperf logs)
- jitter: done (iperf logs)
- packet loss: done (iperf logs)
- resource utilization (cpu, memory): done (upf_monitor.py)
- (slice setup time)


1. create slice config
set -a && source .custom_env && set +a && python3 deploy_slices.py


2. deploy core network
```
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

5. run iperf server (one file at a time)
set -a && source .custom_env && set +a && docker compose -f test1_server.yaml up
or
set -a && source .custom_env && set +a && docker compose -f test2_server.yaml up
or
set -a && source .custom_env && set +a && docker compose -f test3_server.yaml up


6. run ue (one file at a time)
set -a && source .custom_env && set +a && docker compose -f test1_ue.yaml up
or
set -a && source .custom_env && set +a && docker compose -f test2_ue.yaml up
or
set -a && source .custom_env && set +a && docker compose -f test3_ue.yaml up



7. results
logs/iperf: iperf results
logs/upfx: upf container x system resources

tub5g-srv05:
91.99.142.188
metrics:
http://91.99.142.188:3000


tub5g-srv06:
91.99.20.100

tub5g-srv03:
49.13.235.12