# usmcguy.rhel8

An Ansible collection for Red Hat Enterprise Linux 8 roles focused on supplemental STIG hardening, smartcard authentication, and access control configuration.

This collection is intended to provide RHEL 8-specific roles that support system hardening and access workflows. The STIG-related role content is organized under `roles/rhel8stig_supp`, and additional roles may be added for smartcard authentication and SSH/sudo access workflows.

> [!WARNING]
> These roles can make significant system changes and may have unintended consequences if applied without review or testing.
>
> Always back up the target system before applying these roles or running associated playbooks.
>
> Always review any code downloaded from the internet before executing it in your environment.
>
> [!CAUTION]
> Use this content at your own risk. No responsibility is accepted for any damage, outage, data loss, or other harm caused by execution of this playbook.

## What this collection contains

- `roles/rhel8stig_supp`
  - Supplemental RHEL 8 STIG remediation and configuration tasks.
  - Intended to support STIG-related hardening, policy enforcement, and access control hardening.
- Future roles to include:
  - `smartcard` — enable smartcard authentication and policy configuration.
  - SSH/sudo access roles for SSH key-based sudo workflows.

## Requirements

- Ansible 2.16 or later.
- Target hosts must be Red Hat Enterprise Linux 8.
- Privilege escalation must be available for tasks that modify system security settings.
- The collection depends on collections such as:
  - `ansible.posix`
  - `community.general`
  - `community.crypto`

## Usage

Use the collection from a playbook like this:

```yaml
- hosts: rhel8_servers
  become: true
  collections:
    - usmcguy.rhel8
  roles:
    - role: rhel8stig_supp
      vars:
        rhel8STIG_allow_system_reboot: false
        rhel8STIG_stigrule_authselect_profile: "sssd"
        rhel8STIG_stigrule_230234_grub_password: "ChangeMe_!@12#$34"
```

## Before you apply these roles

- Review the role contents and any example playbooks carefully.

- Test in a non-production environment first.
- Test in a non-production environment first.
- Confirm the configuration values match your OS version, environment, and local security requirements.
- Make sure any STIG-specific variables are reviewed and customized before running.

## Disclaimer

- This project is not affiliated with, endorsed by, or sponsored by the Defense Information Systems Agency (DISA), the Department of Defense (DoD), or any U.S. government entity.
- Official STIG guidance, validation, and compliance determinations must be obtained through authorized DISA resources.
- This collection is provided as-is, without warranty.
- The STIG content here is intended to supplement DISA guidance, not replace official DISA STIG documentation or validation procedures.
- Operators are responsible for reviewing, testing, and safely executing the content.

## Contributors

- Dave K [usmcguy](https://github.com/usmcguy) <br>
  [![usmcguy](https://avatars.githubusercontent.com/u/761929?v=4&s=48)](https://github.com/usmcguy)
- Glenn Mora Rangel [glennmora](https://github.com/glennmora) <br>
  [![glennmora](https://avatars.githubusercontent.com/u/108555140?v=4&s=48)](https://github.com/glennmora)
