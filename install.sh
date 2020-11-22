#!/usr/bin/env bash

if [[ $(id -u) -ne 0 ]] ; then echo "Please run with sudo or as root" ; exit 1 ; fi

mkdir -p /var/log/pihole-stats/
touch /var/log/pihole-stats/pihole-stats.log
chown -R pi:pi /var/log/pihole-stats

cp pihole-stats.service /etc/systemd/system/
cp pihole-stats.timer /etc/systemd/system/
cp pihole-stats.logrotate /etc/logrotate.d/

systemctl daemon-reload
systemctl start pihole-stats.timer
systemctl enable pihole-stats.timer