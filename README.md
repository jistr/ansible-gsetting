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

    # Embed the schema in the key
    - name: turn off hot corners
      gsetting:
        user: jistr
        key: org.gnome.desktop.interface.enable-hot-corners
        value: "{{'false'|string}}"
        
    # Specify the schema separately
    - name: turn off hot corners
      gsetting:
        user: jistr
        schema: org.gnome.desktop.interface
        key: enable-hot-corners
        value: "{{'false'|string}}"
    
    # Use a relocatable schema
    - name: set custom key binding
      gsetting:
        user: jistr
        schema: org.gnome.settings-daemon.plugins.media-keys.custom-keybinding
        path: /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/
        settings:
          name: Flameshot
          binding: Print
          command: flameshot gui
    
    - name: do not remember mount password
      gsetting:
        user: jistr
        settings:
          org.gnome.shell.remember-mount-password: false
          org.gnome.desktop.wm.keybindings.panel-main-menu: "@as []"
          org.gnome.nautilus.preferences.default-folder-viewer: "'list-view'"

If you want to run Ansible as the user you want to adjust settings
for, you should omit the `user` parameter:

    - name: shortcut panel-main-menu
      gsetting:
        settings:
          org.gnome.desktop.wm.keybindings.panel-main-menu: "@as []"

Be careful with string values, which should be passed into GSetting
single-quoted. You'll need to quote the value twice in YAML:

    - name: nautilus use list view
      gsetting:
        user: jistr
        settings:
          org.gnome.nautilus.preferences.default-folder-viewer: "'list-view'"

    - name: nautilus list view columns
      gsetting:
        user: jistr
        settings:
          org.gnome.nautilus.list-view.default-visible-columns: "['name', 'size', 'date_modified', 'permissions', 'owner', 'group']"
