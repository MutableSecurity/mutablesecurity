is_ids=`cat /opt/mutablesecurity/suricata.conf | grep -c "mode: ids"`
if [ $is_ips = "1" ]; then
    suricata-update
else
    echo -n "re:. ^alert drop" > /tmp/suricata-modify.conf
    suricata-update --modify-conf /tmp/suricata-modify.conf
fi