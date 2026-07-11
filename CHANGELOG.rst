===========================
usmcguy.stigs Release Notes
===========================

.. contents:: Topics

v1.0.2
======

Release Summary
---------------

- minor document updates
- updated tasks to allign with DISA release V2R8

Minor Changes
-------------

- roles/rhel8stig_supp/README.md - removed whitespace from raw table
- roles/rhel8stig_supp/tasks/rules.yml - removed leftover debug task
- roles/rhel8stig_supp/tasks/rules.yml - removed unused variables
- roles/rhel8stig_supp/tasks/rules.yml - updated V-230471 to comply with DISA release V2R8.
- roles/rhel8stig_supp/tasks/rules.yml - updated V-244546 to allow deny option to follow with DISA release V2R8.
- roles/rhel8stig_supp/templates - organize templates folder.

v1.0.1
======

Bugfixes
--------

- U_RHEL_8_STIG_V2R7_Manual-xccdf.xml - replaced unicode characters with ASCII
- stig_xml.py - changed conditional logic on line 78 from '!=' to 'is not'.
- stig_xml.py - on lines 61 and 71 set the regex to be a raw string with 'r'.

v1.0.0
======

Release Summary
---------------

Initial release of usmcguy.stigs collection

Major Changes
-------------

- Intial release - Tested execution on a fresh install of RHEL 8 with Server GUI
