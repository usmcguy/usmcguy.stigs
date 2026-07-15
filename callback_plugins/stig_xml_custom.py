from __future__ import absolute_import, division, print_function

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
    CALLBACK_NAME = "stig_xml"

    CALLBACK_NEEDS_WHITELIST = True

    def _get_role_files_dir(self, task):
        if task is None or not hasattr(task, 'get_path'):
            return None

        task_path = task.get_path()
        if task_path is None:
            return None

        task_path = os.path.abspath(task_path)
        parts = task_path.split(os.sep)
        if 'roles' not in parts:
            return None

        roles_index = parts.index('roles')
        if roles_index + 1 >= len(parts):
            return None

        role_path = os.path.join(*parts[: roles_index + 2])
        files_dir = os.path.join(role_path, 'files')
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
        if self.stig_path is None:
            self.stig_path = self._get_STIG_path()
        self._display.display("Using STIG_PATH: {}".format(self.stig_path))
        if self.XML_path is None:
            self.XML_path = tempfile.mkdtemp() + '/xccdf-results.xml'
        self._display.display("Using XML_PATH: {}".format(self.XML_path))

        print("Writing: {}".format(self.XML_path))
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
        bm.set(
            'href',
            'xccdf_mil.disa.stig_testresult_scap_mil.disa_comp_{}'.format(STIG_name),
        )
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
        if m:
            nid = m.group('id')
        else:
            return
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
