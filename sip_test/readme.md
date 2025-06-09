# config data for pyHSS
provision data through pyHSS interactive console: [localhost:8080/docs](localhost:8080/docs)
populate apn and auc first, then subscriber and ims_subscriber

- apn:
    ```json
    {
        "apn_id": 0,
        "apn": "ims",                           
        "ip_version": 4,
        "pgw_address": "172.22.0.8",
        "sgw_address": "172.22.0.8",           
        "charging_characteristics": "0800",    
        "apn_ambr_dl": 100000000,          
        "apn_ambr_ul": 100000000,           
        "qci": 5,                         
        "arp_priority": 1,                      
        "arp_preemption_capability": true,
        "arp_preemption_vulnerability": false,
        "charging_rule_list": "",        
        "nbiot": false,
        "nidd_scef_id": "",
        "nidd_scef_realm": "",
        "nidd_mechanism": 0,
        "nidd_rds": 0,
        "nidd_preferred_data_mode": 0
    }
    
- subscriber:
    ```json
    {
        "subscriber_id": 1,
        "imsi": "001011234567895",
        "enabled": true,
        "auc_id": 1,
        "default_apn": 1,
        "apn_list": "[0]",
        "msisdn": "1234567890",
        "ue_ambr_dl": 100000000,
        "ue_ambr_ul": 50000000,
        "nam": 1,
        "roaming_enabled": false,
        "roaming_rule_list": "",
        "subscribed_rau_tau_timer": 60,
        "serving_mme": "",
        "serving_mme_timestamp": "2025-06-09 00:00:00",
        "serving_mme_realm": "",
        "serving_mme_peer": ""
    }
- auc:
    ```json
    {
        "auc_id": 1,
        "ki": "8baf473f2f8fd09487cccbd7097c6862",
        "opc": "8e27b6af0e692e750f32667a3b14605d",
        "amf": "8000",
        "sqn": 16,
        "iccid": "8988211000000000000",
        "imsi": "001011234567895",
        "batch_name": "test-batch",
        "sim_vendor": "test-vendor",
        "esim": false,
        "lpa": "",
        "pin1": "1234",
        "pin2": "5678",
        "puk1": "87654321",
        "puk2": "12345678",
        "kid": "",
        "psk": "",
        "des": "",
        "adm1": "",
        "misc1": "",
        "misc2": "",
        "misc3": "",
        "misc4": ""
    }


- ims_subscriber:
    ```json
    {
        "ims_subscriber_id": 1,
        "msisdn": "1234567890",
        "msisdn_list": "[\"1234567890\"]",
        "imsi": "001011234567895",
        "ifc_path": "/etc/kamailio/ifc/test_ifc.xml",
        "pcscf": "pcscf.ims.mnc001.mcc001.3gppnetwork.org",
        "pcscf_realm": "ims.mnc001.mcc001.3gppnetwork.org",
        "pcscf_active_session": "1",
        "pcscf_timestamp": "2025-06-09 13:52:45",
        "pcscf_peer": "pcscf",
        "xcap_profile": "",
        "sh_profile": "",
        "scscf": "scscf.ims.mnc001.mcc001.3gppnetwork.org",
        "scscf_timestamp": "2025-06-09 13:52:45",
        "scscf_realm": "ims.mnc001.mcc001.3gppnetwork.org",
        "scscf_peer": "scscf",
        "sh_template_path": "/etc/kamailio/sh_templates/default.xml"
    }

# run scenarios using sipp
- OPTIONS call: `sipp -sf options.xml -i 172.22.0.24 -p 5060 172.22.0.21 -s 001010123456789 -trace_msg -m 10`