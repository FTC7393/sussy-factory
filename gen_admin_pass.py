#!/usr/bin/env python3
import json
import werkzeug.security

print('enter new admin password:')
admin_password = input()
admin_password_hash = werkzeug.security.generate_password_hash(admin_password, method='sha256')

with open('data/config.json', 'r') as f:
    config = json.load(f)

config['admin_password_hash'] = admin_password_hash

with open('data/config.json', 'w') as f:
    json.dump(config, f, indent=2)
