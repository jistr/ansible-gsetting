#!/usr/bin/python

import json
import re
import subprocess

from ansible.module_utils.basic import *

def _set_value(schema, key, value):
    return subprocess.check_output([
        '/usr/bin/gsettings', 'set', schema, key, value
    ]).strip()

def _get_value(schema, key):
    return subprocess.check_output([
        '/usr/bin/gsettings', 'get', schema, key
    ]).strip()

def main():

    module = AnsibleModule(
        argument_spec = {
            'state': { 'choices': ['present'], 'default': 'present' },
            'schema': { 'required': True },
            'key': { 'required': True },
            'value': { 'required': True }
        },
        supports_check_mode = True,
    )

    params = module.params
    state = module.params['state']
    schema = module.params['schema']
    key = module.params['key']
    value = module.params['value']

    old_value = _get_value(schema, key)
    changed = old_value != value

    if changed and not module.check_mode:
        _set_value(schema, key, value)

    print json.dumps({
        'changed': changed,
        'key': key,
        'value': value,
        'old_value': old_value,
    })

main()
