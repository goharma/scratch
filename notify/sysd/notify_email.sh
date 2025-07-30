#!/bin/bash
SERVICE_NAME="$1"
TO="root@monkeyturd.localdomain"
SUBJECT="Systemd Alert: $SERVICE_NAME triggered"
BODY="The service $SERVICE_NAME has triggered an alert."

sendmail -t <<EOF
To: $TO
Subject: $SUBJECT

$BODY
EOF
