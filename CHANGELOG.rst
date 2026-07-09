===========================
usmcguy.stigs Release Notes
===========================

.. contents:: Topics

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
