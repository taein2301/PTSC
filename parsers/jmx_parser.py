"""
JMeter JMX Parser

This module provides functionality to parse JMeter JMX files and extract
test plan elements, thread groups, samplers, and other components.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Any
import logging

from utils.validators import validate_jmx_format
from utils.helpers import read_file, format_error_message
from utils.constants import (
    JMETER_HASH_TREE,
    JMETER_TEST_PLAN,
    JMETER_USER_DEFINED_VARIABLES
)


class JMXParser:
    """
    Parser for JMeter JMX files.

    This class handles loading and parsing JMeter JMX files, extracting
    test plan structure, thread groups, samplers, and other elements.

    Attributes:
        file_path: Path to the JMX file
        root: XML root element
        test_plan: Parsed test plan data
        errors: List of parsing errors
        warnings: List of parsing warnings
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize JMXParser.

        Args:
            file_path: Optional path to JMX file to load immediately
        """
        self.file_path = file_path
        self.root: Optional[ET.Element] = None
        self.test_plan: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.logger = logging.getLogger(__name__)

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Load and parse a JMX file.

        Args:
            file_path: Path to the JMX file

        Returns:
            Tuple of (success, error_message)

        Example:
            >>> parser = JMXParser()
            >>> success, error = parser.load_file("test.jmx")
            >>> if success:
            ...     print("File loaded successfully")
        """
        self.file_path = file_path
        self.errors.clear()
        self.warnings.clear()

        try:
            # Read file with encoding detection
            success, content, error = read_file(file_path)

            if not success:
                error_msg = format_error_message("FileReadError", error)
                self.errors.append(error_msg)
                return False, error_msg

            # Validate JMX format
            is_valid, validation_error = validate_jmx_format(content)
            if not is_valid:
                error_msg = format_error_message("ValidationError", validation_error)
                self.errors.append(error_msg)
                return False, error_msg

            # Parse XML
            success, error = self._parse_xml(content)
            if not success:
                return False, error

            self.logger.info(f"Successfully loaded JMX file: {file_path}")
            return True, ""

        except Exception as e:
            error_msg = format_error_message("ParseError", str(e))
            self.errors.append(error_msg)
            self.logger.error(f"Failed to load JMX file: {error_msg}")
            return False, error_msg

    def _parse_xml(self, content: str) -> Tuple[bool, str]:
        """
        Parse XML content into ElementTree.

        Args:
            content: XML content as string

        Returns:
            Tuple of (success, error_message)
        """
        try:
            self.root = ET.fromstring(content)

            # Verify root element
            if self.root.tag != 'jmeterTestPlan':
                error_msg = format_error_message(
                    "InvalidFormat",
                    f"Expected 'jmeterTestPlan' root element, got '{self.root.tag}'"
                )
                self.errors.append(error_msg)
                return False, error_msg

            return True, ""

        except ET.ParseError as e:
            error_msg = format_error_message("XMLParseError", str(e))
            self.errors.append(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = format_error_message("UnexpectedError", str(e))
            self.errors.append(error_msg)
            return False, error_msg

    def parse(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Parse the loaded JMX file and extract all components.

        Returns:
            Tuple of (success, parsed_data)

        The parsed_data dictionary contains:
        - test_plan: Test plan metadata
        - thread_groups: List of thread groups
        - variables: Global variables
        - elements: List of all test elements

        Example:
            >>> parser = JMXParser("test.jmx")
            >>> success, data = parser.parse()
            >>> if success:
            ...     print(f"Found {len(data['thread_groups'])} thread groups")
        """
        if self.root is None:
            error_msg = "No JMX file loaded. Call load_file() first."
            self.errors.append(error_msg)
            return False, {}

        try:
            self.test_plan = {
                'test_plan': {},
                'thread_groups': [],
                'variables': {},
                'elements': []
            }

            # Parse test plan metadata
            self._parse_test_plan_metadata()

            # Parse main structure
            self._parse_hash_tree(self.root)

            self.logger.info("JMX parsing completed successfully")
            return True, self.test_plan

        except Exception as e:
            error_msg = format_error_message("ParseError", str(e))
            self.errors.append(error_msg)
            self.logger.error(f"JMX parsing failed: {error_msg}")
            return False, {}

    def _parse_test_plan_metadata(self) -> None:
        """
        Parse test plan metadata from root element.

        Extracts:
        - JMeter version information
        - TestPlan element properties (name, comments, etc.)
        - User defined variables
        """
        if self.root is None:
            return

        # Get JMeter version info
        self.test_plan['test_plan'] = {
            'version': self.root.get('version', '1.2'),
            'properties': self.root.get('properties', '5.0'),
            'jmeter': self.root.get('jmeter', '5.5'),
            'name': '',
            'comments': '',
            'enabled': True,
            'functional_mode': False,
            'serialize_threadgroups': False
        }

        # Find TestPlan element
        test_plan_elem = self.root.find(f".//{JMETER_TEST_PLAN}")
        if test_plan_elem is not None:
            self._extract_test_plan_properties(test_plan_elem)

            # Find and parse user defined variables
            self._extract_user_variables(test_plan_elem)

    def _extract_test_plan_properties(self, test_plan_elem: ET.Element) -> None:
        """
        Extract properties from TestPlan element.

        Args:
            test_plan_elem: TestPlan XML element
        """
        # Extract test plan name
        name_prop = test_plan_elem.find(".//stringProp[@name='TestPlan.name']")
        if name_prop is None:
            name_prop = test_plan_elem.find(".//stringProp[@name='TestElement.name']")
        if name_prop is not None and name_prop.text:
            self.test_plan['test_plan']['name'] = name_prop.text
        else:
            # Fallback to testname attribute
            self.test_plan['test_plan']['name'] = test_plan_elem.get('testname', 'Test Plan')

        # Extract comments
        comments_prop = test_plan_elem.find(".//stringProp[@name='TestPlan.comments']")
        if comments_prop is not None and comments_prop.text:
            self.test_plan['test_plan']['comments'] = comments_prop.text

        # Extract enabled status
        enabled_prop = test_plan_elem.find(".//boolProp[@name='TestElement.enabled']")
        if enabled_prop is not None and enabled_prop.text:
            self.test_plan['test_plan']['enabled'] = enabled_prop.text.lower() == 'true'

        # Extract functional mode
        functional_prop = test_plan_elem.find(".//boolProp[@name='TestPlan.functional_mode']")
        if functional_prop is not None and functional_prop.text:
            self.test_plan['test_plan']['functional_mode'] = functional_prop.text.lower() == 'true'

        # Extract serialize threadgroups
        serialize_prop = test_plan_elem.find(".//boolProp[@name='TestPlan.serialize_threadgroups']")
        if serialize_prop is not None and serialize_prop.text:
            self.test_plan['test_plan']['serialize_threadgroups'] = serialize_prop.text.lower() == 'true'

        self.logger.debug(f"Extracted TestPlan: {self.test_plan['test_plan']['name']}")

    def _extract_user_variables(self, test_plan_elem: ET.Element) -> None:
        """
        Extract user defined variables from TestPlan.

        Args:
            test_plan_elem: TestPlan XML element
        """
        # Find Arguments (UserDefinedVariables) element
        arguments_elem = test_plan_elem.find(f".//{JMETER_USER_DEFINED_VARIABLES}")
        if arguments_elem is None:
            return

        # Find collection of arguments
        collection = arguments_elem.find(".//collectionProp[@name='Arguments.arguments']")
        if collection is None:
            return

        # Extract each variable
        for arg_elem in collection.findall(".//elementProp"):
            var_name_prop = arg_elem.find(".//stringProp[@name='Argument.name']")
            var_value_prop = arg_elem.find(".//stringProp[@name='Argument.value']")

            if var_name_prop is not None and var_name_prop.text:
                var_name = var_name_prop.text
                var_value = var_value_prop.text if var_value_prop is not None else ''

                self.test_plan['variables'][var_name] = var_value
                self.logger.debug(f"Extracted variable: {var_name} = {var_value}")

    def _parse_hash_tree(self, element: ET.Element, parent_type: str = '') -> None:
        """
        Parse hashTree elements recursively.

        JMeter uses hashTree elements to represent hierarchical structure.
        Each element is followed by a hashTree containing its children.

        Args:
            element: Current XML element
            parent_type: Type of parent element for context
        """
        for child in element:
            if child.tag == JMETER_HASH_TREE:
                # Process children of hashTree
                self._parse_hash_tree(child, parent_type)
            else:
                # Process actual test element
                element_type = self._get_element_type(child)

                if element_type:
                    self._process_element(child, element_type)

                    # Find and process its hashTree (children)
                    next_elem = self._get_next_sibling(element, child)
                    if next_elem is not None and next_elem.tag == JMETER_HASH_TREE:
                        self._parse_hash_tree(next_elem, element_type)

    def _get_element_type(self, element: ET.Element) -> Optional[str]:
        """
        Get the type of a JMeter element.

        Args:
            element: XML element

        Returns:
            Element type string or None
        """
        # Check testclass attribute
        test_class = element.get('testclass', '')
        if test_class:
            return test_class

        # Check guiclass attribute
        gui_class = element.get('guiclass', '')
        if gui_class:
            # Extract class name from GUI class
            # e.g., "ThreadGroupGui" -> "ThreadGroup"
            return gui_class.replace('Gui', '')

        return None

    def _get_next_sibling(self, parent: ET.Element, current: ET.Element) -> Optional[ET.Element]:
        """
        Get the next sibling element.

        Args:
            parent: Parent element
            current: Current element

        Returns:
            Next sibling element or None
        """
        children = list(parent)
        try:
            current_index = children.index(current)
            if current_index + 1 < len(children):
                return children[current_index + 1]
        except ValueError:
            pass

        return None

    def _process_element(self, element: ET.Element, element_type: str) -> None:
        """
        Process a test element based on its type.

        Args:
            element: XML element
            element_type: Type of element
        """
        # Store element info
        element_info = {
            'type': element_type,
            'name': self._get_element_name(element),
            'enabled': self._get_element_enabled(element),
            'properties': self._extract_properties(element)
        }

        self.test_plan['elements'].append(element_info)

        self.logger.debug(f"Processed element: {element_type} - {element_info['name']}")

    def _get_element_name(self, element: ET.Element) -> str:
        """
        Get the name of an element.

        Args:
            element: XML element

        Returns:
            Element name
        """
        name_prop = element.find(".//stringProp[@name='TestElement.name']")
        if name_prop is not None and name_prop.text:
            return name_prop.text

        # Fallback to testname attribute
        return element.get('testname', 'Unnamed')

    def _get_element_enabled(self, element: ET.Element) -> bool:
        """
        Check if an element is enabled.

        Args:
            element: XML element

        Returns:
            True if enabled, False otherwise
        """
        enabled_prop = element.find(".//boolProp[@name='TestElement.enabled']")
        if enabled_prop is not None and enabled_prop.text:
            return enabled_prop.text.lower() == 'true'

        # Default to enabled
        return element.get('enabled', 'true').lower() == 'true'

    def _extract_properties(self, element: ET.Element) -> Dict[str, Any]:
        """
        Extract all properties from an element.

        Args:
            element: XML element

        Returns:
            Dictionary of properties
        """
        properties: Dict[str, Any] = {}

        # Extract string properties
        for prop in element.findall('.//stringProp'):
            name = prop.get('name', '')
            if name:
                properties[name] = prop.text or ''

        # Extract boolean properties
        for prop in element.findall('.//boolProp'):
            name = prop.get('name', '')
            if name:
                bool_value = prop.text and prop.text.lower() == 'true'
                properties[name] = bool(bool_value)

        # Extract integer properties
        for prop in element.findall('.//intProp'):
            name = prop.get('name', '')
            if name:
                try:
                    int_value = int(prop.text or '0')
                    properties[name] = int_value
                except ValueError:
                    properties[name] = 0

        # Extract long properties
        for prop in element.findall('.//longProp'):
            name = prop.get('name', '')
            if name:
                try:
                    long_value = int(prop.text or '0')
                    properties[name] = long_value
                except ValueError:
                    properties[name] = 0

        return properties

    def get_test_plan(self) -> Dict[str, Any]:
        """
        Get the parsed test plan data.

        Returns:
            Dictionary containing parsed test plan
        """
        return self.test_plan

    def get_errors(self) -> List[str]:
        """
        Get list of parsing errors.

        Returns:
            List of error messages
        """
        return self.errors

    def get_warnings(self) -> List[str]:
        """
        Get list of parsing warnings.

        Returns:
            List of warning messages
        """
        return self.warnings

    def has_errors(self) -> bool:
        """
        Check if there were any parsing errors.

        Returns:
            True if errors occurred, False otherwise
        """
        return len(self.errors) > 0
