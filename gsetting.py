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

def _maybe_int(val):
    try:
        return int(val)
    except ValueError:
        return 0

def _get_gnome_version():
    try:
        return tuple(map(_maybe_int, (_check_output_strip(
            ['gnome-shell', '--version']).split(' ')[2].split('.'))))
    except FileNotFoundError:
        return None

def _get_gnome_session_pid(user):
    gnome_ver = _get_gnome_version()
    if gnome_ver and gnome_ver >= (42,):
        # It's actually ghome-session-binary, but pgrep uses /proc/#/status,
        # which truncates the process name at 15 characters.
        #
        # Note that this may _also_ work for GNOME 3.33.90, i.e., the code
        # block below, but I'm preserving that behavior because I don't have
        # earlier GNOME versions to check.
        #
        # Note also that the code block below won't work when the default
        # session named "gnome" isn't used. For example, in recent versions of
        # ubuntu the session name is "ubuntu", i.e., "session=ubuntu" rather
        # than "session=gnome".
        pgrep_cmd = ['pgrep', '-u', user, 'gnome-session-b']
    elif gnome_ver and gnome_ver >= (3, 33, 90):
        # From GNOME 3.33.90 session process has changed
        # https://github.com/GNOME/gnome-session/releases/tag/3.33.90
        pgrep_cmd = ['pgrep', '-u', user, '-f', 'session=gnome']
    else:
        pgrep_cmd = ['pgrep', '-u', user, 'gnome-session']

    try:
        # At least in GNOME 42, there are multiple gnome-session-binary
        # processes, and we only want the first one.
        lines = _check_output_strip(pgrep_cmd)
        return lines.split()[0]
    except subprocess.CalledProcessError:
        return None

def _get_phoc_session_pid(user):
    pgrep_cmd = ['pgrep', '-u', user, 'phoc']

    try:
        return _check_output_strip(pgrep_cmd)
    except subprocess.CalledProcessError:
       return None

def _get_dbus_bus_address(user):
    if user is None:
        if environ.get('DBUS_SESSION_BUS_ADDRESS') is None:
            return None

        return "DBUS_SESSION_BUS_ADDRESS={}".format(environ['DBUS_SESSION_BUS_ADDRESS'])

    pid = _get_gnome_session_pid(user) or _get_phoc_session_pid(user)
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
            'key': { 'required': False },
            'value': { 'required': False },
            'settings': { 'type': 'dict', "required": False, 'default': dict() },
        },
        supports_check_mode = True,
    )

    params = module.params
    state = module.params['state']
    user = module.params['user']
    schemadir = module.params['schemadir']
    key = module.params['key']
    value = module.params['value']
    settings = module.params['settings']
    any_changed = False
    unchanged_settings = list()
    changed_settings = list()

    if key is None and len(settings) == 0:
        module.fail_json(msg="Either a key or a settings dict is required, "
                             "neither was provided.")

    if key is not None:
        settings[key] = value

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


if __name__ == '__main__':
    main()
