"""
Tests for JMX Parser
"""

import pytest
import tempfile
import os
from parsers.jmx_parser import JMXParser


# Sample JMX content for testing
SAMPLE_JMX = """<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.5">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Test Plan" enabled="true">
      <stringProp name="TestElement.name">Simple Test Plan</stringProp>
      <boolProp name="TestElement.enabled">true</boolProp>
      <stringProp name="TestPlan.comments">Sample test plan</stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <intProp name="ThreadGroup.num_threads">1</intProp>
        <intProp name="ThreadGroup.ramp_time">1</intProp>
        <longProp name="ThreadGroup.duration">0</longProp>
      </ThreadGroup>
      <hashTree/>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
"""

INVALID_JMX = """<?xml version="1.0" encoding="UTF-8"?>
<notAJMeterPlan>
  <test>Invalid</test>
</notAJMeterPlan>
"""


class TestJMXParser:
    """Test cases for JMXParser class"""

    def test_parser_init_without_file(self):
        """Test initializing parser without a file"""
        parser = JMXParser()
        assert parser.file_path is None
        assert parser.root is None
        assert len(parser.errors) == 0

    def test_parser_init_with_invalid_file(self):
        """Test initializing parser with non-existent file"""
        parser = JMXParser("nonexistent.jmx")
        assert parser.has_errors()

    def test_load_valid_jmx_file(self):
        """Test loading a valid JMX file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jmx', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_JMX)
            temp_file = f.name

        try:
            parser = JMXParser()
            success, error = parser.load_file(temp_file)

            assert success is True
            assert error == ""
            assert parser.root is not None
            assert parser.root.tag == 'jmeterTestPlan'
        finally:
            os.unlink(temp_file)

    def test_load_invalid_jmx_file(self):
        """Test loading an invalid JMX file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jmx', delete=False, encoding='utf-8') as f:
            f.write(INVALID_JMX)
            temp_file = f.name

        try:
            parser = JMXParser()
            success, error = parser.load_file(temp_file)

            assert success is False
            assert error != ""
            assert parser.has_errors()
        finally:
            os.unlink(temp_file)

    def test_parse_without_loading(self):
        """Test parsing without loading a file first"""
        parser = JMXParser()
        success, data = parser.parse()

        assert success is False
        assert len(data) == 0
        assert parser.has_errors()

    def test_parse_valid_jmx(self):
        """Test parsing a valid JMX file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jmx', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_JMX)
            temp_file = f.name

        try:
            parser = JMXParser()
            parser.load_file(temp_file)
            success, data = parser.parse()

            assert success is True
            assert 'test_plan' in data
            assert 'thread_groups' in data
            assert 'variables' in data
            assert 'elements' in data
            assert data['test_plan']['version'] == '1.2'
        finally:
            os.unlink(temp_file)

    def test_get_test_plan(self):
        """Test getting test plan data"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jmx', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_JMX)
            temp_file = f.name

        try:
            parser = JMXParser()
            parser.load_file(temp_file)
            parser.parse()

            test_plan = parser.get_test_plan()
            assert test_plan is not None
            assert isinstance(test_plan, dict)
        finally:
            os.unlink(temp_file)

    def test_get_errors(self):
        """Test getting error list"""
        parser = JMXParser("nonexistent.jmx")
        errors = parser.get_errors()

        assert isinstance(errors, list)
        assert len(errors) > 0

    def test_get_warnings(self):
        """Test getting warning list"""
        parser = JMXParser()
        warnings = parser.get_warnings()

        assert isinstance(warnings, list)

    def test_extract_properties(self):
        """Test property extraction from elements"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jmx', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_JMX)
            temp_file = f.name

        try:
            parser = JMXParser()
            parser.load_file(temp_file)
            parser.parse()

            # Check that elements were extracted
            assert len(parser.test_plan['elements']) > 0

            # Check first element properties
            first_element = parser.test_plan['elements'][0]
            assert 'type' in first_element
            assert 'name' in first_element
            assert 'enabled' in first_element
            assert 'properties' in first_element
        finally:
            os.unlink(temp_file)

    def test_element_name_extraction(self):
        """Test extracting element names"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jmx', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_JMX)
            temp_file = f.name

        try:
            parser = JMXParser()
            parser.load_file(temp_file)
            parser.parse()

            # Find TestPlan element
            test_plan_elem = next(
                (e for e in parser.test_plan['elements'] if e['type'] == 'TestPlan'),
                None
            )

            assert test_plan_elem is not None
            assert test_plan_elem['name'] == 'Simple Test Plan'
        finally:
            os.unlink(temp_file)

    def test_element_enabled_extraction(self):
        """Test extracting element enabled status"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jmx', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_JMX)
            temp_file = f.name

        try:
            parser = JMXParser()
            parser.load_file(temp_file)
            parser.parse()

            # All elements in sample are enabled
            for element in parser.test_plan['elements']:
                assert element['enabled'] is True
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
