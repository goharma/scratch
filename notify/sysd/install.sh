#!/usr/bin/sh


cp notify_email.sh /usr/local/bin/notify_email.sh && 
chmod +x /usr/local/bin/notify_email.sh &&
cp fail-dummy.service /etc/systemd/system/fail-dummy.service &&
cp notify-email@.service /etc/systemd/system/notify-email@.service

# Don't start/enable template service
# systemctl enable notify-email@.service
# systemctl start notify-email@.service

systemctl daemon-reload
systemctl start fail-dummy.service