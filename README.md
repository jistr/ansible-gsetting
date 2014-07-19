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
