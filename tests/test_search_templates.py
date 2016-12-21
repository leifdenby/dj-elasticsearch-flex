#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import six
import pyfakefs.fake_filesystem_unittest as fake_fs_unittest

from django.test import TestCase

from elasticsearch_flex.search_templates import SearchTemplate

JSON_SRC = '''{
    "foo": "bar",
    "fop": ["baz", "bat"],
    "baz": {
        "bar": "#[awesome]"
    }
}'''
AWESOME_SCR = '''String answer = "42";
    for(key <String>: params) {
        if (key == answer) {
            return true;
        }
    }
'''


class TestSearchTemplate(fake_fs_unittest.TestCase, TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.fs.CreateDirectory('/var/templates')
        self.fs.CreateFile('/var/templates/uno.json', contents=JSON_SRC)
        self.fs.CreateFile('/var/templates/awesome.java', contents=AWESOME_SCR)

    def test_prerender(self):
        tpl = SearchTemplate('foo', '/var/templates/uno.json')
        assert type(tpl.template) is six.text_type
        render = json.loads(tpl.template)
        assert render['foo'] == 'bar'
        assert render['fop'] == ['baz', 'bat']
        assert render['baz']['bar'] == "String answer = \"42\";\n for(key <String>: params) {\n if (key == answer) {\n return true;\n }\n } "
