ansible-gsetting
================

Ansible module for setting GSettings entries.

See also
[ansible-dconf](https://github.com/jistr/ansible-dconf).

Installation
------------

    curl https://raw.githubusercontent.com/jistr/ansible-gsetting/master/gsetting.py > ~/ansible_dir/library/gsetting

Usage examples
--------------

    - name: do not remember mount password
      gsetting: user=jistr
                key=org.gnome.shell.remember-mount-password
                value=false

    - name: shortcut panel-main-menu
      gsetting: user=jistr
                key=org.gnome.desktop.wm.keybindings.panel-main-menu
                value="@as []"


Or explicitly define schema and key instead of using dash to seperate them, useful when the schema name includeds dashes.

    - name: do not remember mount password
      gsetting: user=jistr
                schema=org.gnome.shell.remember
                key=mount-password
                value=false

    - name: change dash to dock klick action
      gsetting: user=jistr
                schema=org.gnome.shell.extensions.dash-to-dock
                key=click-action
                value="previews"

Be careful with string values, which should be passed into GSetting
single-quoted. You'll need to quote the value twice in YAML:

    - name: nautilus use list view
      gsetting: user=jistr
                key=org.gnome.nautilus.preferences.default-folder-viewer
                value="'list-view'"

    - name: nautilus list view columns
      gsetting: user=jistr
                key=org.gnome.nautilus.list-view.default-visible-columns
                value="['name', 'size', 'date_modified', 'permissions', 'owner', 'group']"
