#!/bin/sh
# One-time local setup. Both steps need sudo, which is why they are not
# automated: /etc/hosts and the system keychain are outside the containers.
#
# .dev is HSTS-preloaded, so browsers force HTTPS on yetpanda.dev and offer
# no click-through for an untrusted certificate. Local TLS is mandatory.
set -e

echo "1/2  Pointing *.yetpanda.dev at localhost"
printf '\n# YetPanda local development\n127.0.0.1 yetpanda.dev www.yetpanda.dev api.yetpanda.dev\n::1 yetpanda.dev www.yetpanda.dev api.yetpanda.dev\n' \
  | sudo tee -a /etc/hosts > /dev/null

echo "2/2  Trusting Caddy's local certificate authority"
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain caddy/root.crt

echo
echo "Done. Open https://yetpanda.dev"
