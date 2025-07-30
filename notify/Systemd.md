# SystemD
## Types

simple/exec: Process runs in foreground

Forking: Deamons

One Shot: One time setup 

## Email On Fail
### Email Script

```
#!/bin/bash
echo "Subject: Service restart notice" | \
  sendmail -v your.address@example.com
```


### Notify Service
```
# /etc/systemd/system/notify-restart.service
[Unit]
Description=Send email on service failure

[Service]
Type=oneshot
ExecStart=/usr/local/bin/send-email.sh
```

### Use in your service
```
[Unit]
Description=Your monitored service
OnFailure=notify-restart.service

[Service]
Type=simple
ExecStart=/your/command
Restart=on-failure
```