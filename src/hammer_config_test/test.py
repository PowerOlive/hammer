#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unit tests for the hammer_config module.
#
#  Copyright 2017 Edward Wang <edward.c.wang@compdigitec.com>

import hammer_config

import unittest

class HammerDatabaseTest(unittest.TestCase):

    def test_overriding(self):
        """
        Test that we can add a project first and technology after and still have it override.
        """
        db = hammer_config.HammerDatabase()
        db.update_project([{"tech.x": "foo"}])
        self.assertEqual(db.get_setting("tech.x"), "foo")
        db.update_technology([{"tech.x": "bar"}])
        self.assertEqual(db.get_setting("tech.x"), "foo")

    def test_unpacking(self):
        """
        Test that input configs get unpacked.
        """
        db = hammer_config.HammerDatabase()
        config = hammer_config.load_config_from_string("""
foo:
    bar:
        adc: "yes"
        dac: "no"
""", is_yaml=True)
        db.update_core([config])
        self.assertEqual(db.get_setting("foo.bar.adc"), "yes")
        self.assertEqual(db.get_setting("foo.bar.dac"), "no")

    def test_meta_subst(self):
        """
        Test that the meta attribute "subst" works.
        """
        db = hammer_config.HammerDatabase()
        base = hammer_config.load_config_from_string("""
foo:
    flash: "yes"
    one: "1"
    two: "2"
""", is_yaml=True)
        meta = hammer_config.load_config_from_string("""
{
  "foo.pipeline": "${foo.flash}man",
  "foo.pipeline_meta": "subst",
  "foo.uint": ["${foo.one}", "${foo.two}"],
  "foo.uint_meta": "subst"
}
""", is_yaml=False)
        db.update_core([base, meta])
        self.assertEqual(db.get_setting("foo.flash"), "yes")
        self.assertEqual(db.get_setting("foo.pipeline"), "yesman")
        self.assertEqual(db.get_setting("foo.uint"), ["1", "2"])

    def test_meta_dynamicsubst(self):
        """
        Test that the meta attribute "dynamicsubst" works.
        """
        db = hammer_config.HammerDatabase()
        base = hammer_config.load_config_from_string("""
foo:
    flash: "yes"
    one: "1"
    two: "2"
""", is_yaml=True)
        meta = hammer_config.load_config_from_string("""
{
  "foo.pipeline": "${foo.flash}man",
  "foo.pipeline_meta": "subst",
  "foo.reg": "Wire",
  "foo.reginit": "${foo.reg}Init",
  "foo.reginit_meta": "dynamicsubst",
  "foo.later": "${later}",
  "foo.later_meta": "dynamicsubst"
}
""", is_yaml=False)
        project = hammer_config.load_config_from_string("""
{
  "later": "later"
}
""", is_yaml=False)
        db.update_core([base, meta])
        db.update_project([project])
        self.assertEqual(db.get_setting("foo.flash"), "yes")
        self.assertEqual(db.get_setting("foo.pipeline"), "yesman")
        self.assertEqual(db.get_setting("foo.reginit"), "WireInit")
        self.assertEqual(db.get_setting("foo.later"), "later")

    def test_meta_dynamicsubst_other_dynamicsubst(self):
        """
        Check that a dynamicsubst which references other dynamicsubst errors for now.
        """
        """
        Test that the meta attribute "dynamicsubst" works.
        """
        db = hammer_config.HammerDatabase()
        base = hammer_config.load_config_from_string("""
foo:
    flash: "yes"
    one: "1"
    two: "2"
    lolcat: ""
    twelve: "${lolcat}"
    twelve_meta: dynamicsubst
""", is_yaml=True)
        project = hammer_config.load_config_from_string("""
{
  "lolcat": "whatever",
  "later": "${foo.twelve}",
  "later_meta": "dynamicsubst"
}
""", is_yaml=False)
        db.update_core([base])
        db.update_project([project])
        with self.assertRaises(ValueError):
            print(db.get_config())

    def test_meta_append(self):
        """
        Test that the meta attribute "append" works.
        """
        db = hammer_config.HammerDatabase()
        base = hammer_config.load_config_from_string("""
foo:
    bar:
        adc: "yes"
        dac: "no"
        dsl: ["scala"]
""", is_yaml=True)
        meta = hammer_config.load_config_from_string("""
{
  "foo.bar.dsl": ["python"],
  "foo.bar.dsl_meta": "append",
  "foo.bar.dac": "current_weighted"
}
""", is_yaml=False)
        db.update_core([base, meta])
        self.assertEqual(db.get_setting("foo.bar.dac"), "current_weighted")
        self.assertEqual(db.get_setting("foo.bar.dsl"), ["scala", "python"])

    def test_meta_append_bad(self):
        """
        Test that the meta attribute "append" catches bad inputs.
        """
        base = hammer_config.load_config_from_string("""
foo:
    bar:
        adc: "yes"
        dac: "no"
        dsl: "scala"
""", is_yaml=True)
        meta = hammer_config.load_config_from_string("""
{
  "foo.bar.dsl": ["python"],
  "foo.bar.dsl_meta": "append",
  "foo.bar.dac": "current_weighted"
}
""", is_yaml=False)
        with self.assertRaises(ValueError):
            hammer_config.combine_configs([base, meta])

        meta = hammer_config.load_config_from_string("""
{
  "foo.bar.dsl": "c++",
  "foo.bar.dsl_meta": "append",
  "foo.bar.dac": "current_weighted"
}
""", is_yaml=False)
        with self.assertRaises(ValueError):
            hammer_config.combine_configs([base, meta])

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()