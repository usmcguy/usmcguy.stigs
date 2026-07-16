# Copyright (c) 2026 Dave King
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
name: stig_xml_custom
type: aggregate
short_description: Generate STIG results xml
extends_documentation_fragment:
  - ansible.builtin.default_callback
description:
  - When play completes, a xccdf-results.xml is created in a sub-folder under /tmp
"""

__metaclass__ = type

import os
import platform
import re
import tempfile
import xml.dom.minidom
import xml.etree.ElementTree as ET
from time import gmtime, strftime

from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "xml"
    CALLBACK_NAME = "usmcguy.stigs.stig_xml_custom"

    CALLBACK_NEEDS_WHITELIST = True

    def _get_role_files_dir(self, task):
        if task is None or not hasattr(task, 'get_path'):
            self._display.warning("no task / no get_path")
            return None

        task_path = task.get_path()
        self._display.warning("raw get_path: {!r}".format(task_path))
        if task_path is None:
            return None

        task_path = task_path.split(':')[0]
        task_path = os.path.abspath(task_path)
        parts = task_path.split(os.sep)
        self._display.warning("parts: {}".format(parts))
        if 'roles' not in parts:
            self._display.warning("'roles' not in path")
            return None

        roles_index = parts.index('roles')
        if roles_index + 1 >= len(parts):
            return None

        role_path = os.path.join(os.sep, *parts[: roles_index + 2])
        files_dir = os.path.join(role_path, 'files')
        self._display.warning("checking files_dir: {} exists={}".format(
            files_dir, os.path.isdir(files_dir)))
        return files_dir if os.path.isdir(files_dir) else None

    def _get_STIG_path(self, task=None):
        if task is not None:
            files_dir = self._get_role_files_dir(task)
            if files_dir:
                candidates = [
                    os.path.join(files_dir, fname)
                    for fname in os.listdir(files_dir)
                    if fname.lower().endswith('.xml') and 'xccdf' in fname.lower()
                ]
                if candidates:
                    return sorted(candidates)[0]

        cwd = os.path.abspath('.')
        for dirpath, dirs, files in os.walk(cwd):
            if os.path.basename(dirpath) == 'files':
                for fname in files:
                    if fname.lower().endswith('.xml') and 'xccdf' in fname.lower():
                        return os.path.join(dirpath, fname)

        return None

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.rules = {}
        self.stig_path = os.environ.get('STIG_PATH')
        self.XML_path = os.environ.get('XML_PATH')
        if self.XML_path is None:
            self.XML_path = os.path.join(tempfile.mkdtemp(), 'xccdf-results.xml')
        self._display.display("Using XML_PATH: {}".format(self.XML_path))
        self.tr = None
        self._initialized = False

    def _ensure_stig_path(self, task=None):
        if self.stig_path is None:
            self.stig_path = self._get_STIG_path(task)
            #self._display.display("Using STIG_PATH: {}".format(self.stig_path))
        return self.stig_path

    def _init_tree(self):
        if self._initialized:
            return
        if not self.stig_path:
            return
        self._initialized = True
        self._display.display("Using STIG_PATH: {}".format(self.stig_path))
        STIG_name = os.path.basename(self.stig_path)
        ET.register_namespace('', 'http://checklists.nist.gov/xccdf/1.2')
        self.tr = ET.Element('{http://checklists.nist.gov/xccdf/1.2}TestResult')
        self.tr.set(
            'id',
            'xccdf_mil.disa.stig_testresult_scap_mil.disa_comp_{}'.format(STIG_name),
        )
        endtime = strftime('%Y-%m-%dT%H:%M:%S', gmtime())
        self.tr.set('end-time', endtime)
        bm = ET.SubElement(self.tr, '{http://checklists.nist.gov/xccdf/1.2}benchmark')
        bm.set('href', 'xccdf_mil.disa.stig_testresult_scap_mil.disa_comp_{}'.format(STIG_name))
        tg = ET.SubElement(self.tr, '{http://checklists.nist.gov/xccdf/1.2}target')
        tg.text = platform.node()

    def _get_rev(self, nid, task=None):
        stig_path = self.stig_path or self._get_STIG_path(task)
        if not stig_path:
            raise RuntimeError('Unable to resolve STIG_PATH for task {}'.format(task))

        with open(stig_path, 'r') as f:
            r = r'SV-{}r(?P<rev>\d+)_rule'.format(nid)
            m = re.search(r, f.read())
        if m:
            rev = m.group('rev')
        else:
            rev = '0'
        return rev

    def v2_runner_on_ok(self, result):
        name = result._task.get_name()
        m = re.search(r'stigrule_(?P<id>\d+)', name, re.IGNORECASE)
        if not m:
            return
        self._ensure_stig_path(result._task)
        self._init_tree()
        if self.tr is None:
            return
        nid = m.group('id')
        rev = self._get_rev(nid, result._task)
        key = '{}r{}'.format(nid, rev)
        if self.rules.get(key, 'Unknown') is not False:
            self.rules[key] = result.is_changed()

    def v2_playbook_on_stats(self, stats):
        for rule, changed in self.rules.items():
            state = 'fail' if changed else 'pass'
            rr = ET.SubElement(
                self.tr, '{http://checklists.nist.gov/xccdf/1.2}rule-result'
            )
            rr.set('idref', 'xccdf_mil.disa.stig_rule_SV-{}_rule'.format(rule))
            rs = ET.SubElement(rr, '{http://checklists.nist.gov/xccdf/1.2}result')
            rs.text = state
        passing = len(self.rules) - sum(self.rules.values())
        sc = ET.SubElement(self.tr, '{http://checklists.nist.gov/xccdf/1.2}score')
        sc.set('maximum', str(len(self.rules)))
        sc.set('system', 'urn:xccdf:scoring:flat-unweighted')
        sc.text = str(passing)
        with open(self.XML_path, 'wb') as f:
            out = ET.tostring(self.tr)
            pretty = xml.dom.minidom.parseString(out).toprettyxml(encoding='utf-8')
            f.write(pretty)
