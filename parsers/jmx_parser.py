"""
JMX Parser Module

Parses JMeter JMX files and extracts test plan components including:
- Test plan configuration
- Thread groups
- HTTP samplers
- Headers, cookies, assertions
- Extractors (regex, JSON)
- Timers and controllers
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from utils.constants import JMETER_ELEMENTS, ERROR_CODES


class JMXParser:
    """Parser for JMeter JMX files"""

    def __init__(self):
        """Initialize the JMX parser"""
        self.root = None
        self.test_plan_data = {}

    def parse(self, jmx_content: str) -> Dict[str, Any]:
        """
        Parse JMX content and extract all components

        Args:
            jmx_content: JMX file content as string

        Returns:
            Dictionary containing parsed test plan data
        """
        try:
            self.root = ET.fromstring(jmx_content)
        except ET.ParseError as e:
            return {
                'success': False,
                'error': f"{ERROR_CODES['INVALID_XML']}: Failed to parse JMX - {str(e)}",
                'data': None
            }

        # Extract test plan elements
        test_plan = self._extract_test_plan()
        thread_groups = self._extract_thread_groups()
        user_variables = self._extract_user_variables()

        self.test_plan_data = {
            'success': True,
            'test_plan': test_plan,
            'thread_groups': thread_groups,
            'user_variables': user_variables
        }

        return self.test_plan_data

    def _extract_test_plan(self) -> Dict[str, Any]:
        """
        Extract test plan configuration

        Returns:
            Dictionary with test plan info
        """
        test_plan_elem = self.root.find(f'.//{JMETER_ELEMENTS["TEST_PLAN"]}')

        if test_plan_elem is None:
            return {'name': 'Unknown Test Plan', 'properties': {}}

        name = test_plan_elem.get('testname', 'Unknown Test Plan')
        enabled = test_plan_elem.get('enabled', 'true') == 'true'

        return {
            'name': name,
            'enabled': enabled,
            'properties': self._extract_properties(test_plan_elem)
        }

    def _extract_thread_groups(self) -> List[Dict[str, Any]]:
        """
        Extract all thread groups with their samplers and config

        Returns:
            List of thread group dictionaries
        """
        thread_groups = []
        thread_group_elems = self.root.findall(f'.//{JMETER_ELEMENTS["THREAD_GROUP"]}')

        for tg_elem in thread_group_elems:
            thread_group = self._parse_thread_group(tg_elem)
            thread_groups.append(thread_group)

        return thread_groups

    def _parse_thread_group(self, elem: ET.Element) -> Dict[str, Any]:
        """
        Parse a single thread group element

        Args:
            elem: ThreadGroup XML element

        Returns:
            Dictionary with thread group data
        """
        name = elem.get('testname', 'Thread Group')
        enabled = elem.get('enabled', 'true') == 'true'

        # Extract thread group properties
        num_threads = self._get_string_prop(elem, 'ThreadGroup.num_threads', '1')
        ramp_time = self._get_string_prop(elem, 'ThreadGroup.ramp_time', '1')
        loops = self._get_string_prop(elem, 'LoopController.loops', '1')
        duration = self._get_string_prop(elem, 'ThreadGroup.duration', '')
        delay = self._get_string_prop(elem, 'ThreadGroup.delay', '')

        # Find the hashTree following this thread group
        parent = self._find_parent(self.root, elem)
        hash_tree = None

        if parent is not None:
            for i, child in enumerate(parent):
                if child == elem and i + 1 < len(parent):
                    next_elem = parent[i + 1]
                    if next_elem.tag == 'hashTree':
                        hash_tree = next_elem
                        break

        # Extract samplers and config elements from hashTree
        samplers = []
        headers = []
        cookies = []
        extractors = []
        assertions = []
        timers = []
        controllers = []

        if hash_tree is not None:
            samplers = self._extract_samplers(hash_tree)
            headers = self._extract_headers(hash_tree)
            cookies = self._extract_cookies(hash_tree)
            extractors = self._extract_extractors(hash_tree)
            assertions = self._extract_assertions(hash_tree)
            timers = self._extract_timers(hash_tree)
            controllers = self._extract_controllers(hash_tree)

        return {
            'name': name,
            'enabled': enabled,
            'num_threads': num_threads,
            'ramp_time': ramp_time,
            'loops': loops,
            'duration': duration,
            'delay': delay,
            'samplers': samplers,
            'headers': headers,
            'cookies': cookies,
            'extractors': extractors,
            'assertions': assertions,
            'timers': timers,
            'controllers': controllers
        }

    def _extract_samplers(self, hash_tree: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract HTTP samplers from hashTree

        Args:
            hash_tree: hashTree XML element

        Returns:
            List of sampler dictionaries
        """
        samplers = []
        sampler_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["HTTP_SAMPLER"]}')

        for sampler_elem in sampler_elems:
            sampler = self._parse_http_sampler(sampler_elem)
            samplers.append(sampler)

        return samplers

    def _parse_http_sampler(self, elem: ET.Element) -> Dict[str, Any]:
        """
        Parse HTTP sampler element

        Args:
            elem: HTTPSamplerProxy XML element

        Returns:
            Dictionary with sampler data
        """
        name = elem.get('testname', 'HTTP Request')
        enabled = elem.get('enabled', 'true') == 'true'

        # Extract HTTP request details
        method = self._get_string_prop(elem, 'HTTPSampler.method', 'GET')
        domain = self._get_string_prop(elem, 'HTTPSampler.domain', '')
        port = self._get_string_prop(elem, 'HTTPSampler.port', '')
        protocol = self._get_string_prop(elem, 'HTTPSampler.protocol', 'https')
        path = self._get_string_prop(elem, 'HTTPSampler.path', '/')
        content_encoding = self._get_string_prop(elem, 'HTTPSampler.contentEncoding', '')

        # Extract parameters
        arguments = self._extract_arguments(elem)

        # Extract body data
        post_body = self._get_string_prop(elem, 'Argument.value', '')

        return {
            'name': name,
            'enabled': enabled,
            'method': method,
            'domain': domain,
            'port': port,
            'protocol': protocol,
            'path': path,
            'content_encoding': content_encoding,
            'arguments': arguments,
            'post_body': post_body
        }

    def _extract_arguments(self, elem: ET.Element) -> List[Dict[str, str]]:
        """
        Extract arguments/parameters from element

        Args:
            elem: XML element containing arguments

        Returns:
            List of argument dictionaries
        """
        arguments = []
        args_elem = elem.find('.//elementProp[@name="HTTPsampler.Arguments"]')

        if args_elem is not None:
            for arg in args_elem.findall('.//elementProp'):
                name = self._get_string_prop(arg, 'Argument.name', '')
                value = self._get_string_prop(arg, 'Argument.value', '')
                metadata = self._get_string_prop(arg, 'Argument.metadata', '=')

                if name:  # Only add if name exists
                    arguments.append({
                        'name': name,
                        'value': value,
                        'metadata': metadata
                    })

        return arguments

    def _extract_headers(self, hash_tree: ET.Element) -> List[Dict[str, str]]:
        """
        Extract header managers

        Args:
            hash_tree: hashTree XML element

        Returns:
            List of header dictionaries
        """
        headers = []
        header_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["HEADER_MANAGER"]}')

        for header_elem in header_elems:
            coll_prop = header_elem.find('.//collectionProp[@name="HeaderManager.headers"]')
            if coll_prop is not None:
                for elem_prop in coll_prop.findall('.//elementProp'):
                    name = self._get_string_prop(elem_prop, 'Header.name', '')
                    value = self._get_string_prop(elem_prop, 'Header.value', '')

                    if name:
                        headers.append({'name': name, 'value': value})

        return headers

    def _extract_cookies(self, hash_tree: ET.Element) -> List[Dict[str, str]]:
        """
        Extract cookie managers

        Args:
            hash_tree: hashTree XML element

        Returns:
            List of cookie dictionaries
        """
        cookies = []
        cookie_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["COOKIE_MANAGER"]}')

        for cookie_elem in cookie_elems:
            coll_prop = cookie_elem.find('.//collectionProp[@name="CookieManager.cookies"]')
            if coll_prop is not None:
                for elem_prop in coll_prop.findall('.//elementProp'):
                    name = self._get_string_prop(elem_prop, 'Cookie.name', '')
                    value = self._get_string_prop(elem_prop, 'Cookie.value', '')
                    domain = self._get_string_prop(elem_prop, 'Cookie.domain', '')

                    if name:
                        cookies.append({'name': name, 'value': value, 'domain': domain})

        return cookies

    def _extract_extractors(self, hash_tree: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract correlation extractors (regex, JSON)

        Args:
            hash_tree: hashTree XML element

        Returns:
            List of extractor dictionaries
        """
        extractors = []

        # Regex extractors
        regex_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["REGEX_EXTRACTOR"]}')
        for regex_elem in regex_elems:
            extractor = {
                'type': 'regex',
                'name': regex_elem.get('testname', 'RegEx Extractor'),
                'refname': self._get_string_prop(regex_elem, 'RegexExtractor.refname', ''),
                'regex': self._get_string_prop(regex_elem, 'RegexExtractor.regex', ''),
                'template': self._get_string_prop(regex_elem, 'RegexExtractor.template', '$1$'),
                'match_no': self._get_string_prop(regex_elem, 'RegexExtractor.match_number', '1'),
                'default': self._get_string_prop(regex_elem, 'RegexExtractor.default', '')
            }
            extractors.append(extractor)

        # JSON extractors
        json_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["JSON_EXTRACTOR"]}')
        for json_elem in json_elems:
            extractor = {
                'type': 'json',
                'name': json_elem.get('testname', 'JSON Extractor'),
                'refname': self._get_string_prop(json_elem, 'JSONPostProcessor.referenceNames', ''),
                'jsonpath': self._get_string_prop(json_elem, 'JSONPostProcessor.jsonPathExprs', ''),
                'match_no': self._get_string_prop(json_elem, 'JSONPostProcessor.match_numbers', '1'),
                'default': self._get_string_prop(json_elem, 'JSONPostProcessor.defaultValues', '')
            }
            extractors.append(extractor)

        return extractors

    def _extract_assertions(self, hash_tree: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract response assertions

        Args:
            hash_tree: hashTree XML element

        Returns:
            List of assertion dictionaries
        """
        assertions = []
        assertion_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["RESPONSE_ASSERTION"]}')

        for assertion_elem in assertion_elems:
            name = assertion_elem.get('testname', 'Response Assertion')
            test_field = self._get_string_prop(assertion_elem, 'Assertion.test_field', 'Assertion.response_data')
            test_type = self._get_string_prop(assertion_elem, 'Assertion.test_type', '2')

            # Extract test strings
            test_strings = []
            coll_prop = assertion_elem.find('.//collectionProp[@name="Asserion.test_strings"]')
            if coll_prop is not None:
                for string_prop in coll_prop.findall('.//stringProp'):
                    test_strings.append(string_prop.text or '')

            assertions.append({
                'name': name,
                'test_field': test_field,
                'test_type': test_type,
                'test_strings': test_strings
            })

        return assertions

    def _extract_timers(self, hash_tree: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract constant timers

        Args:
            hash_tree: hashTree XML element

        Returns:
            List of timer dictionaries
        """
        timers = []
        timer_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["CONSTANT_TIMER"]}')

        for timer_elem in timer_elems:
            name = timer_elem.get('testname', 'Constant Timer')
            delay = self._get_string_prop(timer_elem, 'ConstantTimer.delay', '0')

            timers.append({
                'name': name,
                'delay': delay
            })

        return timers

    def _extract_controllers(self, hash_tree: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract controllers (Loop, If, While, Transaction)

        Args:
            hash_tree: hashTree XML element

        Returns:
            List of controller dictionaries
        """
        controllers = []

        # Transaction controllers
        trans_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["TRANSACTION_CONTROLLER"]}')
        for trans_elem in trans_elems:
            name = trans_elem.get('testname', 'Transaction')
            parent_flag = self._get_bool_prop(trans_elem, 'TransactionController.parent', True)

            controllers.append({
                'type': 'transaction',
                'name': name,
                'parent': parent_flag
            })

        # Loop controllers
        loop_elems = hash_tree.findall(f'.//{JMETER_ELEMENTS["LOOP_CONTROLLER"]}')
        for loop_elem in loop_elems:
            name = loop_elem.get('testname', 'Loop Controller')
            loops = self._get_string_prop(loop_elem, 'LoopController.loops', '1')

            controllers.append({
                'type': 'loop',
                'name': name,
                'loops': loops
            })

        return controllers

    def _extract_user_variables(self) -> Dict[str, str]:
        """
        Extract user defined variables from test plan

        Returns:
            Dictionary of variable name-value pairs
        """
        variables = {}
        args_elem = self.root.find('.//Arguments')

        if args_elem is not None:
            for arg in args_elem.findall('.//elementProp'):
                name = self._get_string_prop(arg, 'Argument.name', '')
                value = self._get_string_prop(arg, 'Argument.value', '')

                if name:
                    variables[name] = value

        return variables

    def _extract_properties(self, elem: ET.Element) -> Dict[str, str]:
        """
        Extract all properties from element

        Args:
            elem: XML element

        Returns:
            Dictionary of properties
        """
        properties = {}

        for string_prop in elem.findall('.//stringProp'):
            name = string_prop.get('name', '')
            value = string_prop.text or ''
            if name:
                properties[name] = value

        for bool_prop in elem.findall('.//boolProp'):
            name = bool_prop.get('name', '')
            value = bool_prop.text or 'false'
            if name:
                properties[name] = value

        return properties

    def _get_string_prop(self, elem: ET.Element, prop_name: str, default: str = '') -> str:
        """
        Get stringProp value from element

        Args:
            elem: XML element
            prop_name: Property name
            default: Default value if not found

        Returns:
            Property value
        """
        prop_elem = elem.find(f'.//stringProp[@name="{prop_name}"]')
        return prop_elem.text if prop_elem is not None and prop_elem.text else default

    def _get_bool_prop(self, elem: ET.Element, prop_name: str, default: bool = False) -> bool:
        """
        Get boolProp value from element

        Args:
            elem: XML element
            prop_name: Property name
            default: Default value if not found

        Returns:
            Property value as boolean
        """
        prop_elem = elem.find(f'.//boolProp[@name="{prop_name}"]')
        if prop_elem is not None and prop_elem.text:
            return prop_elem.text.lower() == 'true'
        return default

    def _find_parent(self, tree: ET.Element, child: ET.Element) -> Optional[ET.Element]:
        """
        Find parent element of a child

        Args:
            tree: Root element to search from
            child: Child element to find parent of

        Returns:
            Parent element or None
        """
        for parent in tree.iter():
            if child in parent:
                return parent
        return None
