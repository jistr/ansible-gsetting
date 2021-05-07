#!/usr/bin/python

from os import environ
import re
import subprocess

from ansible.module_utils.basic import *

def _check_output_strip(command):
    return subprocess.check_output(command).decode('utf-8').strip()

def _escape_single_quotes(string):
    return re.sub("'", r"'\''", string)

def _split_key(full_key):
    key_array = full_key.split('.')
    schema = '.'.join(key_array[0:-1])
    single_key = key_array[-1]
    return (schema, single_key)

def _get_gnome_version():
    return tuple(map(int, (_check_output_strip(
        ['gnome-shell', '--version']).split(' ')[2].split('.'))))

def _get_dbus_bus_address(user):
    if user is None:
        if environ.get('DBUS_SESSION_BUS_ADDRESS') is None:
            return None

        return "DBUS_SESSION_BUS_ADDRESS={}".format(environ['DBUS_SESSION_BUS_ADDRESS'])

    pgrep_cmd = ['pgrep', '-u', user, 'gnome-session']
    gnome_ver = _get_gnome_version()
    if (gnome_ver >= (3, 33, 90)):
        # From GNOME 3.33.90 session process has changed
        # https://github.com/GNOME/gnome-session/releases/tag/3.33.90
        pgrep_cmd = ['pgrep', '-u', user, '-f', 'session=gnome']

    try:
        pid = _check_output_strip(pgrep_cmd)
    except subprocess.CalledProcessError:
       return None

    if pid:
        return _check_output_strip(
            ['grep', '-z', '^DBUS_SESSION_BUS_ADDRESS',
             '/proc/{}/environ'.format(pid)]).strip('\0')

def _run_cmd_with_dbus(user, cmd, dbus_addr):
    if not dbus_addr:
        command = ['dbus-run-session', '--']
    else:
        command = ['export', dbus_addr, ';']
    command.extend(cmd)

    if user is None:
        return _check_output_strip(['/bin/sh', '-c', " ".join(command)])

    return _check_output_strip(['su', '-', user , '-c', " ".join(command)])

def _set_value(schemadir, user, full_key, value, dbus_addr):
    schema, single_key = _split_key(full_key)

    command = ['/usr/bin/gsettings']
    if schemadir:
        command.extend(['--schemadir', schemadir])
    command.extend(['set', schema, single_key,
        "'%s'" % _escape_single_quotes(value)])

    return _run_cmd_with_dbus(user, command, dbus_addr)

def _get_value(schemadir, user, full_key, dbus_addr):
    schema, single_key = _split_key(full_key)

    command = ['/usr/bin/gsettings']
    if schemadir:
        command.extend(['--schemadir', schemadir])
    command.extend(['get', schema, single_key])

    return _run_cmd_with_dbus(user, command, dbus_addr)

def main():

    module = AnsibleModule(
        argument_spec = {
            'state': { 'choices': ['present'], 'default': 'present' },
            'user': { 'default': None },
            'schemadir': { 'required': False },
            'settings': { 'type': 'dict', "required": True },
        },
        supports_check_mode = True,
    )

    params = module.params
    state = module.params['state']
    user = module.params['user']
    schemadir = module.params['schemadir']
    settings = module.params['settings']
    any_changed = False
    unchanged_settings = list()
    changed_settings = list()

    dbus_addr = _get_dbus_bus_address(user)

    for key, value in settings.items():
        old_value = _get_value(schemadir, user, key, dbus_addr)
        result = { 'key': key, 'value': old_value }
        changed = old_value != value
        any_changed = any_changed or changed

        if changed and not module.check_mode:
            _set_value(schemadir, user, key, value, dbus_addr)
            result['new_value'] = value
            changed_settings.append(result)
        else:
            unchanged_settings.append(result)

    module.exit_json(**{
        'changed': any_changed,
        'unchanged_settings': unchanged_settings,
        'changed_settings': changed_settings,
    })


main()
