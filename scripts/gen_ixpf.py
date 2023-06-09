#!/bin/python3
import datetime
import json
import requests
import ipaddress
import yaml
import os
from bird_parser import get_bird_session

GITHUB_WORKSPACE = os.environ['GITHUB_WORKSPACE']

client = yaml.safe_load( open(GITHUB_WORKSPACE + "/clients_all.yml").read())
yaml.SafeDumper.ignore_aliases = lambda self, data: True

RS1_birdc = requests.get("http://[2a0a:280:f000:3::1]:3234/bird?q=show+protocols+all").text
RS1_info  = get_bird_session(birdc_output=RS1_birdc)
RS1_estab = set(map(lambda x:x["as"]["remote"],filter(lambda x:x["state"] == "Established" and x["route"]["ipv6"]["imported"] > 0 ,RS1_info)))

# prepare ixp_list data
ixp_list = [{
    "ixp_id": 0,
    "ixf_id": 0,
    "shortname": "MOEIX-SEA",
    "vlan": [
        {"id": 0}
    ],
    "switch": [
        {
            "id": 1,
            "name": "main switch",
            "colo": "",
            "city": "US",
            "country": "US",
            "manufacturer": "unknown",
            "model": "unknown"
        }
    ]
}]

# prepare member_list data
member_list = [
  {
    "asnum": 210979,
    "connection_list": [
      {
        "ixp_id": 0,
        "state": "active",
        "if_list": [
          {
            "if_speed": 250,
            "switch_id": 1
          }
        ],
        "vlan_list": [
          {
            "vlan_id": 0,
            "ipv6": {
              "address": "2a0a:280:f000:3::1",
              "as_macro": "",
              "routeserver": True
            }
          },
          {
            "vlan_id": 0,
            "ipv6": {
              "address": "2a0a:280:f000:3::2",
              "as_macro": "",
              "routeserver": True
            }
          },
          {
            "vlan_id": 0,
            "ipv6": {
              "address": "2a0a:280:f000:3::2",
              "as_macro": "",
              "routeserver": True
            }
          }
        ]
      }
    ]
  }
]

member_dict = {}
for ci in range(len(client["clients"])):
    asnum = client["clients"][ci]["asn"]
    as_macros = client["clients"][ci]["cfg"]["filtering"]["irrdb"]["as_sets"]
    as_macro = as_macros[0] if len(as_macros) > 0 else ""
    routeserver = asnum in RS1_estab
    state = "active" if routeserver else "inactive"
    af = "error"
    if type(ipaddress.ip_address(client["clients"][ci]["ip"])) == ipaddress.IPv4Address:
      af = "ipv4"
    if type(ipaddress.ip_address(client["clients"][ci]["ip"])) == ipaddress.IPv6Address:
      af = "ipv6"
    connection_item = {
        "ixp_id": 0,
        "state": state,
        "if_list": [
            {
                "if_speed": 250,
                "switch_id": 1
            }
        ],
        "vlan_list": [
            {
                "vlan_id": 0,
                af: {
                    "address": client["clients"][ci]["ip"],
                    "as_macro": as_macro,
                    "routeserver": routeserver
                }
            }
        ]
    }
    member_item = {
        "asnum": asnum,
        "connection_list": [connection_item]
    }
    if asnum not in member_dict:
        member_dict[asnum] = member_item
    else:
        found_in_vlan_list = False
        for vlan_item in member_dict[asnum]["connection_list"][0]["vlan_list"]:
           if af not in vlan_item:
              vlan_item[af] = connection_item["vlan_list"][0][af]
              found_in_vlan_list = True
              break
        if not found_in_vlan_list: 
          member_dict[asnum]["connection_list"][0]["vlan_list"] += connection_item["vlan_list"]

member_list.append(list(member_dict.values()))

# prepare the JSON structure
data_dict = {
    "version": "1.0",
#    "timestamp": datetime.datetime.utcnow().isoformat() + 'Z',
    "ixp_list": ixp_list,
    "member_list": member_list,
}

# convert to JSON
json_data = json.dumps(data_dict, indent=2)
print(json_data)
