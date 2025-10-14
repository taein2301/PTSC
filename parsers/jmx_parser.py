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
    JMETER_USER_DEFINED_VARIABLES,
    JMETER_THREAD_GROUP,
    JMETER_HTTP_SAMPLER,
    JMETER_HTTP_SAMPLER_OLD,
    JMETER_HEADER_MANAGER
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

    def _parse_thread_group(self, thread_group_elem: ET.Element) -> None:
        """
        Parse ThreadGroup element and extract its properties.

        Args:
            thread_group_elem: ThreadGroup XML element

        Extracts:
        - Thread count (num_threads)
        - Ramp-up time (ramp_time)
        - Loop count (loops)
        - Duration and delay (scheduler settings)
        - On sample error action
        """
        thread_group = {
            'name': self._get_element_name(thread_group_elem),
            'enabled': self._get_element_enabled(thread_group_elem),
            'num_threads': 1,
            'ramp_time': 1,
            'loops': 1,
            'continue_forever': False,
            'scheduler': False,
            'duration': 0,
            'delay': 0,
            'on_sample_error': 'continue',
            'comments': '',
            'samplers': []
        }

        # Extract number of threads
        num_threads_prop = thread_group_elem.find(".//stringProp[@name='ThreadGroup.num_threads']")
        if num_threads_prop is not None and num_threads_prop.text:
            try:
                thread_group['num_threads'] = int(num_threads_prop.text)
            except ValueError:
                self.warnings.append(f"Invalid num_threads value: {num_threads_prop.text}")

        # Extract ramp-up time
        ramp_time_prop = thread_group_elem.find(".//stringProp[@name='ThreadGroup.ramp_time']")
        if ramp_time_prop is not None and ramp_time_prop.text:
            try:
                thread_group['ramp_time'] = int(ramp_time_prop.text)
            except ValueError:
                self.warnings.append(f"Invalid ramp_time value: {ramp_time_prop.text}")

        # Extract loop controller settings
        loop_controller = thread_group_elem.find(".//elementProp[@name='ThreadGroup.main_controller']")
        if loop_controller is not None:
            # Check if continue forever
            continue_forever_prop = loop_controller.find(".//boolProp[@name='LoopController.continue_forever']")
            if continue_forever_prop is not None and continue_forever_prop.text:
                thread_group['continue_forever'] = continue_forever_prop.text.lower() == 'true'

            # Extract loop count
            loops_prop = loop_controller.find(".//stringProp[@name='LoopController.loops']")
            if loops_prop is not None and loops_prop.text:
                try:
                    # Handle special value "-1" for infinite
                    if loops_prop.text == '-1':
                        thread_group['loops'] = -1
                        thread_group['continue_forever'] = True
                    else:
                        thread_group['loops'] = int(loops_prop.text)
                except ValueError:
                    self.warnings.append(f"Invalid loops value: {loops_prop.text}")

        # Extract scheduler settings
        scheduler_prop = thread_group_elem.find(".//boolProp[@name='ThreadGroup.scheduler']")
        if scheduler_prop is not None and scheduler_prop.text:
            thread_group['scheduler'] = scheduler_prop.text.lower() == 'true'

        # Extract duration
        duration_prop = thread_group_elem.find(".//stringProp[@name='ThreadGroup.duration']")
        if duration_prop is not None and duration_prop.text:
            try:
                thread_group['duration'] = int(duration_prop.text)
            except ValueError:
                self.warnings.append(f"Invalid duration value: {duration_prop.text}")

        # Extract delay
        delay_prop = thread_group_elem.find(".//stringProp[@name='ThreadGroup.delay']")
        if delay_prop is not None and delay_prop.text:
            try:
                thread_group['delay'] = int(delay_prop.text)
            except ValueError:
                self.warnings.append(f"Invalid delay value: {delay_prop.text}")

        # Extract on sample error action
        on_error_prop = thread_group_elem.find(".//stringProp[@name='ThreadGroup.on_sample_error']")
        if on_error_prop is not None and on_error_prop.text:
            thread_group['on_sample_error'] = on_error_prop.text

        # Extract comments
        comments_prop = thread_group_elem.find(".//stringProp[@name='TestElement.comments']")
        if comments_prop is not None and comments_prop.text:
            thread_group['comments'] = comments_prop.text

        self.test_plan['thread_groups'].append(thread_group)
        self.logger.info(f"Parsed ThreadGroup: {thread_group['name']} "
                         f"({thread_group['num_threads']} threads, "
                         f"{thread_group['ramp_time']}s ramp-up, "
                         f"{thread_group['loops']} loops)")

    def _parse_http_sampler(self, sampler_elem: ET.Element) -> Dict[str, Any]:
        """
        Parse HTTP Sampler element and extract its properties.

        Args:
            sampler_elem: HTTPSamplerProxy XML element

        Returns:
            Dictionary containing sampler information

        Extracts:
        - HTTP method (GET, POST, PUT, DELETE, etc.)
        - Protocol (http/https)
        - Domain/server
        - Port
        - Path
        - Parameters (query string or POST data)
        - Body data
        - Follow redirects settings
        - Use keepalive settings
        """
        sampler = {
            'type': 'HTTPSampler',
            'name': self._get_element_name(sampler_elem),
            'enabled': self._get_element_enabled(sampler_elem),
            'method': 'GET',
            'protocol': 'http',
            'domain': '',
            'port': '',
            'path': '/',
            'parameters': [],
            'body': '',
            'encoding': 'UTF-8',
            'follow_redirects': True,
            'auto_redirects': False,
            'use_keepalive': True,
            'do_multipart_post': False,
            'connect_timeout': '',
            'response_timeout': '',
            'comments': ''
        }

        # Extract HTTP method
        method_prop = sampler_elem.find(".//stringProp[@name='HTTPSampler.method']")
        if method_prop is not None and method_prop.text:
            sampler['method'] = method_prop.text.upper()

        # Extract protocol
        protocol_prop = sampler_elem.find(".//stringProp[@name='HTTPSampler.protocol']")
        if protocol_prop is not None and protocol_prop.text:
            sampler['protocol'] = protocol_prop.text.lower()

        # Extract domain
        domain_prop = sampler_elem.find(".//stringProp[@name='HTTPSampler.domain']")
        if domain_prop is not None and domain_prop.text:
            sampler['domain'] = domain_prop.text

        # Extract port
        port_prop = sampler_elem.find(".//stringProp[@name='HTTPSampler.port']")
        if port_prop is not None and port_prop.text:
            sampler['port'] = port_prop.text

        # Extract path
        path_prop = sampler_elem.find(".//stringProp[@name='HTTPSampler.path']")
        if path_prop is not None and path_prop.text:
            sampler['path'] = path_prop.text

        # Extract encoding
        encoding_prop = sampler_elem.find(".//stringProp[@name='HTTPSampler.contentEncoding']")
        if encoding_prop is not None and encoding_prop.text:
            sampler['encoding'] = encoding_prop.text

        # Extract connect timeout
        connect_timeout_prop = sampler_elem.find(".//stringProp[@name='HTTPSampler.connect_timeout']")
        if connect_timeout_prop is not None and connect_timeout_prop.text:
            sampler['connect_timeout'] = connect_timeout_prop.text

        # Extract response timeout
        response_timeout_prop = sampler_elem.find(".//stringProp[@name='HTTPSampler.response_timeout']")
        if response_timeout_prop is not None and response_timeout_prop.text:
            sampler['response_timeout'] = response_timeout_prop.text

        # Extract follow redirects
        follow_redirects_prop = sampler_elem.find(".//boolProp[@name='HTTPSampler.follow_redirects']")
        if follow_redirects_prop is not None and follow_redirects_prop.text:
            sampler['follow_redirects'] = follow_redirects_prop.text.lower() == 'true'

        # Extract auto redirects
        auto_redirects_prop = sampler_elem.find(".//boolProp[@name='HTTPSampler.auto_redirects']")
        if auto_redirects_prop is not None and auto_redirects_prop.text:
            sampler['auto_redirects'] = auto_redirects_prop.text.lower() == 'true'

        # Extract use keepalive
        use_keepalive_prop = sampler_elem.find(".//boolProp[@name='HTTPSampler.use_keepalive']")
        if use_keepalive_prop is not None and use_keepalive_prop.text:
            sampler['use_keepalive'] = use_keepalive_prop.text.lower() == 'true'

        # Extract do multipart post
        do_multipart_prop = sampler_elem.find(".//boolProp[@name='HTTPSampler.DO_MULTIPART_POST']")
        if do_multipart_prop is not None and do_multipart_prop.text:
            sampler['do_multipart_post'] = do_multipart_prop.text.lower() == 'true'

        # Extract comments
        comments_prop = sampler_elem.find(".//stringProp[@name='TestElement.comments']")
        if comments_prop is not None and comments_prop.text:
            sampler['comments'] = comments_prop.text

        # Extract parameters (Arguments)
        self._extract_http_arguments(sampler_elem, sampler)

        # Extract POST body
        self._extract_http_body(sampler_elem, sampler)

        self.logger.debug(f"Parsed HTTP Sampler: {sampler['method']} {sampler['path']}")

        return sampler

    def _extract_http_arguments(self, sampler_elem: ET.Element, sampler: Dict[str, Any]) -> None:
        """
        Extract HTTP arguments (query parameters or POST parameters).

        Args:
            sampler_elem: HTTPSampler XML element
            sampler: Sampler dictionary to update
        """
        # Find Arguments element
        arguments_elem = sampler_elem.find(".//elementProp[@name='HTTPsampler.Arguments']")
        if arguments_elem is None:
            return

        # Find collection of arguments
        collection = arguments_elem.find(".//collectionProp[@name='Arguments.arguments']")
        if collection is None:
            return

        # Extract each parameter
        for arg_elem in collection.findall(".//elementProp"):
            param_name_prop = arg_elem.find(".//stringProp[@name='Argument.name']")
            param_value_prop = arg_elem.find(".//stringProp[@name='Argument.value']")
            param_metadata_prop = arg_elem.find(".//stringProp[@name='Argument.metadata']")

            if param_name_prop is not None:
                param = {
                    'name': param_name_prop.text or '',
                    'value': param_value_prop.text if param_value_prop is not None else '',
                    'metadata': param_metadata_prop.text if param_metadata_prop is not None else '='
                }
                sampler['parameters'].append(param)

    def _extract_http_body(self, sampler_elem: ET.Element, sampler: Dict[str, Any]) -> None:
        """
        Extract HTTP request body data.

        Args:
            sampler_elem: HTTPSampler XML element
            sampler: Sampler dictionary to update
        """
        # Check for postBodyRaw (raw body data)
        post_body_raw = sampler_elem.find(".//boolProp[@name='HTTPSampler.postBodyRaw']")
        if post_body_raw is not None and post_body_raw.text and post_body_raw.text.lower() == 'true':
            # Extract raw body from Arguments
            arguments_elem = sampler_elem.find(".//elementProp[@name='HTTPsampler.Arguments']")
            if arguments_elem is not None:
                collection = arguments_elem.find(".//collectionProp[@name='Arguments.arguments']")
                if collection is not None:
                    # In raw mode, the first argument contains the body
                    first_arg = collection.find(".//elementProp")
                    if first_arg is not None:
                        value_prop = first_arg.find(".//stringProp[@name='Argument.value']")
                        if value_prop is not None and value_prop.text:
                            sampler['body'] = value_prop.text

    def _parse_header_manager(self, header_elem: ET.Element) -> Dict[str, Any]:
        """
        Parse HeaderManager element and extract HTTP headers.

        Args:
            header_elem: HeaderManager XML element

        Returns:
            Dictionary containing header manager information

        Extracts:
        - Header name-value pairs
        - Multiple headers support
        """
        headers_list: List[Dict[str, str]] = []
        header_manager: Dict[str, Any] = {
            'type': 'HeaderManager',
            'name': self._get_element_name(header_elem),
            'enabled': self._get_element_enabled(header_elem),
            'headers': headers_list,
            'comments': ''
        }

        # Extract comments
        comments_prop = header_elem.find(".//stringProp[@name='TestElement.comments']")
        if comments_prop is not None and comments_prop.text:
            header_manager['comments'] = comments_prop.text

        # Find collection of headers
        collection = header_elem.find(".//collectionProp[@name='HeaderManager.headers']")
        if collection is not None:
            # Extract each header
            for header_prop in collection.findall(".//elementProp"):
                name_prop = header_prop.find(".//stringProp[@name='Header.name']")
                value_prop = header_prop.find(".//stringProp[@name='Header.value']")

                if name_prop is not None:
                    header: Dict[str, str] = {
                        'name': name_prop.text or '',
                        'value': value_prop.text or '' if value_prop is not None else ''
                    }
                    headers_list.append(header)

        self.logger.debug(f"Parsed HeaderManager with {len(headers_list)} headers")

        return header_manager

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
        # Handle ThreadGroup specially
        if element_type == JMETER_THREAD_GROUP:
            self._parse_thread_group(element)
            return

        # Handle HTTP Sampler specially
        if element_type in [JMETER_HTTP_SAMPLER, JMETER_HTTP_SAMPLER_OLD]:
            sampler = self._parse_http_sampler(element)
            self.test_plan['elements'].append(sampler)
            return

        # Handle Header Manager specially
        if element_type == JMETER_HEADER_MANAGER:
            header_manager = self._parse_header_manager(element)
            self.test_plan['elements'].append(header_manager)
            return

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
