rhel8stig_supp
===============

A supplemental Ansible role for applying selected RHEL 8 STIG rules and configurations.

Requirements
------------

- Ansible 2.16 or later.
- Target hosts must be Red Hat Enterprise Linux 8.
- Privileged escalation must be available for tasks that modify system security settings.
- Requires the following Ansible collections beyond the built-in core modules:
  - `ansible.posix`
  - `community.general`
  - `community.crypto`

Role Variables
--------------

The role exposes configuration through variables defined in `defaults/main.yml`. Common variables to review or override include:

- `rhel8STIG_allow_system_reboot`: whether the role may reboot the system when required.
- `rhel8STIG_stigrule_authselect_profile`: authselect profile to enforce, default is `sssd`.
- `rhel8STIG_stigrule_authselect_features`: authselect feature list used when enforcing authselect.
- `rhel8STIG_stigrule_logon_DenyAttempts`: maximum failed login attempts before lockout.
- `rhel8STIG_stigrule_login_FailInterval`: login fail interval in seconds.
- `rhel8STIG_stigrule_230234_grub_password` / `rhel8STIG_stigrule_230235_grub_password`: GRUB password settings used by supplemental STIG rules.
- `rhel8STIG_stigrule_230301_exclude_mounts`, `rhel8STIG_stigrule_230301_exclude_fstypes`: mount exclusions for file system checks.
- `rhel8STIG_stigrule_230316_nameservers`, `rhel8STIG_stigrule_230316_cloud`, `rhel8STIG_stigrule_230316_dns_interface`: DNS configuration variables for network checks.
- `rhel8STIG_stigrule_230317_dot_bashrc`: default `.bashrc` content for shell environment remediation.

For a complete list of variables and their defaults, see `roles/rhel8stig_supp/defaults/main.yml`.

Dependencies
------------

This role has no required Galaxy role dependencies. It is a self-contained supplemental STIG role for RHEL 8.

It does require the following collections to be available in your Ansible environment:

- `ansible.posix`
- `community.general`
- `community.crypto`

Example Playbook
----------------

    - hosts: rhel8_servers
      become: true
      roles:
        - role: usmcguy.rhel8stig_supp
          vars:
            rhel8STIG_allow_system_reboot: false
            rhel8STIG_stigrule_authselect_profile: "sssd"
            rhel8STIG_stigrule_230234_grub_password: "ChangeMe_!@12#$34"

License
-------

Apache-2.0

Author Information
------------------

Dave King (USMCguy@gmail.com)
Glenn Mora Rangel