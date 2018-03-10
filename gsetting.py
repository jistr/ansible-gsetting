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

def _get_dbus_bus_address(user):
    try:
        pid = subprocess.check_output(['pgrep', '-u', user, 'gnome-session']).strip()
    except subprocess.CalledProcessError:
       return None

    if pid:
        return subprocess.check_output(
                ['grep', '-z', '^DBUS_SESSION_BUS_ADDRESS', '/proc/' + pid + '/environ']
                ).strip('\0')

def _set_value(schemadir, user, full_key, value):
    schema, single_key = _split_key(full_key)

    dbus_addr = _get_dbus_bus_address(user)
    if not dbus_addr:
        command = ['export `/usr/bin/dbus-launch`', ';']
    else:
        command = ['export', dbus_addr, ';']

    command.append('/usr/bin/gsettings')

    if schemadir:
        command.extend(['--schemadir', schemadir])
    command.extend(['set', schema, single_key,
        "'%s'" % _escape_single_quotes(value)])

    if not dbus_addr:
        command.extend([';',
            'kill $DBUS_SESSION_BUS_PID &> /dev/null'
        ])

    return subprocess.check_output([
        'su', '-', user , '-c', " ".join(command)
    ]).strip()

def _get_value(schemadir, user, full_key):
    schema, single_key = _split_key(full_key)

    dbus_addr = _get_dbus_bus_address(user)
    if not dbus_addr:
        command = ['export `/usr/bin/dbus-launch`', ';']
    else:
        command = ['export', dbus_addr, ';']

    command.append('/usr/bin/gsettings')

    if schemadir:
        command.extend(['--schemadir', schemadir])

    command.extend(['get', schema, single_key])

    if not dbus_addr:
        command.extend([';',
            'kill $DBUS_SESSION_BUS_PID &> /dev/null'
        ])

    return subprocess.check_output([
        'su', '-', user , '-c', " ".join(command)
    ]).strip()

def main():

    module = AnsibleModule(
        argument_spec = {
            'state': { 'choices': ['present'], 'default': 'present' },
            'user': { 'required': True },
            'schemadir': { 'required': False },
            'key': { 'required': True },
            'value': { 'required': True },
        },
        supports_check_mode = True,
    )

    params = module.params
    state = module.params['state']
    user = module.params['user']
    schemadir = module.params['schemadir']
    key = module.params['key']
    value = module.params['value']

    old_value = _get_value(schemadir, user, key)
    changed = old_value != value

    if changed and not module.check_mode:
        _set_value(schemadir, user, key, value)

    print json.dumps({
        'changed': changed,
        'key': key,
        'value': value,
        'old_value': old_value,
    })

main()
