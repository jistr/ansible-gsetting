#!/usr/bin/python

import json
import re
import subprocess

from ansible.module_utils.basic import *

def _escape_single_quotes(string):
    return re.sub("'", r"'\''", string)

def _split_key(full_key):
    key_array = full_key.split('.')
    schema = '.'.join(key_array[0:-1])
    single_key = key_array[-1]
    return (schema, single_key)

def _set_value(user, full_key, value):

    schema, single_key = _split_key(full_key)
    command = " ".join([
        'export `/usr/bin/dbus-launch`',
        ';',
        '/usr/bin/gsettings set', schema, single_key,
        "'%s'" % _escape_single_quotes(value),
        ';',
        'kill $DBUS_SESSION_BUS_PID &> /dev/null'
    ])

    return subprocess.check_output([
        'su', '-', user , '-c', command
    ]).strip()

def _get_value(user, full_key):

    schema, single_key = _split_key(full_key)
    command = " ".join([
        'export `/usr/bin/dbus-launch`',
        ';',
        '/usr/bin/gsettings get', schema, single_key,
        ';',
        'kill $DBUS_SESSION_BUS_PID &> /dev/null'
    ])

    return subprocess.check_output([
        'su', '-', user , '-c', command
    ]).strip()

def main():

    module = AnsibleModule(
        argument_spec = {
            'state': { 'choices': ['present'], 'default': 'present' },
            'user': { 'required': True },
            'key': { 'required': True },
            'value': { 'required': True },
        },
        supports_check_mode = True,
    )

    params = module.params
    state = module.params['state']
    user = module.params['user']
    key = module.params['key']
    value = module.params['value']

    old_value = _get_value(user, key)
    changed = old_value != value

    if changed and not module.check_mode:
        _set_value(user, key, value)

    print json.dumps({
        'changed': changed,
        'key': key,
        'value': value,
        'old_value': old_value,
    })

main()
