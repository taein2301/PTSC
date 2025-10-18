"""
JMX Generator Module

Generates valid JMeter JMX files from parsed LoadRunner data.
Creates proper XML structure with TestPlan, ThreadGroups, HTTPSamplers, etc.
"""

import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from typing import Dict, Any
from utils.helpers import StringHelper
from utils.constants import JMETER_ELEMENTS


class JMXGenerator:
    """Generator for JMeter JMX files"""

    def __init__(self):
        """Initialize the JMX generator"""
        self.string_helper = StringHelper()
        self.test_plan_version = "1.2"
        self.jmeter_version = "5.6.3"
        self.jmeter_props = "5.0"

    def generate(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate complete JMX file from parsed LoadRunner data

        Args:
            parsed_data: Parsed LoadRunner script data

        Returns:
            Complete JMX XML as string
        """
        # Create root element
        root = ET.Element('jmeterTestPlan', {
            'version': self.test_plan_version,
            'properties': self.jmeter_props,
            'jmeter': self.jmeter_version
        })

        # Create hashTree root
        root_hashtree = ET.SubElement(root, 'hashTree')

        # Create TestPlan
        test_plan = self._create_test_plan(parsed_data)
        root_hashtree.append(test_plan)

        # Create TestPlan hashTree
        test_plan_hashtree = ET.SubElement(root_hashtree, 'hashTree')

        # Create ThreadGroup
        thread_group = self._create_thread_group(parsed_data)
        test_plan_hashtree.append(thread_group)

        # Create ThreadGroup hashTree with samplers
        thread_group_hashtree = ET.SubElement(test_plan_hashtree, 'hashTree')
        self._add_samplers_to_hashtree(thread_group_hashtree, parsed_data)

        # Convert to string with improved formatting
        return self._format_xml(root)

    def _create_test_plan(self, parsed_data: Dict[str, Any]) -> ET.Element:
        """
        Create TestPlan element

        Args:
            parsed_data: Parsed data

        Returns:
            TestPlan XML element
        """
        test_plan = ET.Element(JMETER_ELEMENTS['TEST_PLAN'], {
            'guiclass': 'TestPlanGui',
            'testclass': JMETER_ELEMENTS['TEST_PLAN'],
            'testname': 'LoadRunner Converted Test Plan',
            'enabled': 'true'
        })

        # Add string properties
        self._add_string_prop(test_plan, 'TestPlan.comments', 'Converted from LoadRunner C script')
        self._add_bool_prop(test_plan, 'TestPlan.functional_mode', False)
        self._add_bool_prop(test_plan, 'TestPlan.serialize_threadgroups', False)

        # Add element property for user defined variables
        variables = parsed_data.get('variables', {})
        if variables:
            elem_prop = ET.SubElement(test_plan, 'elementProp', {
                'name': 'TestPlan.user_defined_variables',
                'elementType': 'Arguments',
                'guiclass': 'ArgumentsPanel',
                'testclass': 'Arguments',
                'enabled': 'true'
            })

            coll_prop = ET.SubElement(elem_prop, 'collectionProp', {'name': 'Arguments.arguments'})

            for var_name, var_value in variables.items():
                self._add_argument(coll_prop, var_name, var_value)

        return test_plan

    def _create_thread_group(self, parsed_data: Dict[str, Any]) -> ET.Element:
        """
        Create ThreadGroup element

        Args:
            parsed_data: Parsed data

        Returns:
            ThreadGroup XML element
        """
        thread_group = ET.Element(JMETER_ELEMENTS['THREAD_GROUP'], {
            'guiclass': 'ThreadGroupGui',
            'testclass': JMETER_ELEMENTS['THREAD_GROUP'],
            'testname': 'Thread Group',
            'enabled': 'true'
        })

        # Thread group properties
        self._add_string_prop(thread_group, 'ThreadGroup.on_sample_error', 'continue')

        # Thread properties - element property
        thread_prop = ET.SubElement(thread_group, 'elementProp', {
            'name': 'ThreadGroup.main_controller',
            'elementType': 'LoopController',
            'guiclass': 'LoopControlPanel',
            'testclass': 'LoopController',
            'testname': 'Loop Controller',
            'enabled': 'true'
        })

        self._add_bool_prop(thread_prop, 'LoopController.continue_forever', False)
        self._add_string_prop(thread_prop, 'LoopController.loops', '1')

        # Thread configuration
        self._add_string_prop(thread_group, 'ThreadGroup.num_threads', '1')
        self._add_string_prop(thread_group, 'ThreadGroup.ramp_time', '1')
        self._add_bool_prop(thread_group, 'ThreadGroup.scheduler', False)
        self._add_string_prop(thread_group, 'ThreadGroup.duration', '')
        self._add_string_prop(thread_group, 'ThreadGroup.delay', '')

        return thread_group

    def _add_samplers_to_hashtree(self, hashtree: ET.Element, parsed_data: Dict[str, Any]) -> None:
        """
        Add HTTP samplers and other elements to threadgroup hashtree

        Args:
            hashtree: ThreadGroup hashTree element
            parsed_data: Parsed data
        """
        http_requests = parsed_data.get('http_requests', [])
        correlations = parsed_data.get('correlations', [])
        think_times = parsed_data.get('think_times', [])
        transactions = parsed_data.get('transactions', [])
        headers = parsed_data.get('headers', [])

        # Add HeaderManager if headers exist
        if headers:
            header_manager = self._create_header_manager(headers)
            hashtree.append(header_manager)
            ET.SubElement(hashtree, 'hashTree')

        # Add CookieManager
        cookie_manager = self._create_cookie_manager()
        hashtree.append(cookie_manager)
        ET.SubElement(hashtree, 'hashTree')

        # Track transaction state
        in_transaction = False
        current_transaction = None

        # Process requests
        for idx, request in enumerate(http_requests):
            # Check for transaction start
            if transactions:
                for trans in transactions:
                    if trans['type'] == 'start' and not in_transaction:
                        # Start transaction controller
                        trans_controller = self._create_transaction_controller(trans['name'])
                        hashtree.append(trans_controller)
                        current_transaction = ET.SubElement(hashtree, 'hashTree')
                        in_transaction = True
                        break

            # Add correlations before the request
            if correlations and idx < len(correlations):
                correlation = correlations[idx]
                extractor = self._create_extractor(correlation)
                if in_transaction and current_transaction is not None:
                    current_transaction.append(extractor)
                    ET.SubElement(current_transaction, 'hashTree')
                else:
                    hashtree.append(extractor)
                    ET.SubElement(hashtree, 'hashTree')

            # Create HTTP sampler
            sampler = self._create_http_sampler(request)

            if in_transaction and current_transaction is not None:
                current_transaction.append(sampler)
                ET.SubElement(current_transaction, 'hashTree')
            else:
                hashtree.append(sampler)
                ET.SubElement(hashtree, 'hashTree')

            # Add think time if present
            if think_times and idx < len(think_times):
                think_time = think_times[idx]
                timer = self._create_constant_timer(think_time['duration_ms'])
                if in_transaction and current_transaction is not None:
                    current_transaction.append(timer)
                    ET.SubElement(current_transaction, 'hashTree')
                else:
                    hashtree.append(timer)
                    ET.SubElement(hashtree, 'hashTree')

            # Check for transaction end
            if transactions:
                for trans in transactions:
                    if trans['type'] == 'end' and in_transaction:
                        in_transaction = False
                        current_transaction = None
                        break

    def _create_http_sampler(self, request: Dict[str, Any]) -> ET.Element:
        """
        Create HTTPSamplerProxy element

        Args:
            request: HTTP request data

        Returns:
            HTTPSamplerProxy XML element
        """
        sampler = ET.Element(JMETER_ELEMENTS['HTTP_SAMPLER'], {
            'guiclass': 'HttpTestSampleGui',
            'testclass': JMETER_ELEMENTS['HTTP_SAMPLER'],
            'testname': request.get('name', 'HTTP Request'),
            'enabled': 'true'
        })

        # Add HTTP sampler properties
        self._add_string_prop(sampler, 'HTTPSampler.domain', request.get('domain', ''))
        self._add_string_prop(sampler, 'HTTPSampler.port', request.get('port', ''))
        self._add_string_prop(sampler, 'HTTPSampler.protocol', request.get('protocol', 'https'))
        self._add_string_prop(sampler, 'HTTPSampler.contentEncoding', '')
        self._add_string_prop(sampler, 'HTTPSampler.path', request.get('path', '/'))
        self._add_string_prop(sampler, 'HTTPSampler.method', request.get('method', 'GET'))
        self._add_bool_prop(sampler, 'HTTPSampler.follow_redirects', True)
        self._add_bool_prop(sampler, 'HTTPSampler.auto_redirects', False)
        self._add_bool_prop(sampler, 'HTTPSampler.use_keepalive', True)
        self._add_bool_prop(sampler, 'HTTPSampler.DO_MULTIPART_POST', False)

        # Add arguments if present
        arguments = request.get('arguments', [])
        body = request.get('body', '')

        if arguments:
            args_elem = ET.SubElement(sampler, 'elementProp', {
                'name': 'HTTPsampler.Arguments',
                'elementType': 'Arguments',
                'guiclass': 'HTTPArgumentsPanel',
                'testclass': 'Arguments',
                'enabled': 'true'
            })

            coll_prop = ET.SubElement(args_elem, 'collectionProp', {'name': 'Arguments.arguments'})

            for arg in arguments:
                arg_name = arg.get('name', '')
                arg_value = arg.get('value', '')

                # Convert LoadRunner variables to JMeter format
                if '{' in arg_value and '}' in arg_value:
                    arg_value = self.string_helper.convert_lr_to_jmeter_variable(arg_value)

                self._add_argument(coll_prop, arg_name, arg_value)

        elif body:
            # For POST body
            args_elem = ET.SubElement(sampler, 'elementProp', {
                'name': 'HTTPsampler.Arguments',
                'elementType': 'Arguments'
            })

            coll_prop = ET.SubElement(args_elem, 'collectionProp', {'name': 'Arguments.arguments'})

            # Add body as single argument
            arg_elem = ET.SubElement(coll_prop, 'elementProp', {
                'name': '',
                'elementType': 'HTTPArgument'
            })

            self._add_bool_prop(arg_elem, 'HTTPArgument.always_encode', False)

            # Convert LoadRunner variables
            if '{' in body and '}' in body:
                body = self.string_helper.convert_lr_to_jmeter_variable(body)

            self._add_string_prop(arg_elem, 'Argument.value', body)
            self._add_string_prop(arg_elem, 'Argument.metadata', '=')

        return sampler

    def _create_extractor(self, correlation: Dict[str, Any]) -> ET.Element:
        """
        Create extractor element (RegexExtractor or JSONPostProcessor)

        Args:
            correlation: Correlation data

        Returns:
            Extractor XML element
        """
        corr_type = correlation.get('type', 'regex')

        if corr_type == 'json':
            return self._create_json_extractor(correlation)
        else:
            return self._create_regex_extractor(correlation)

    def _create_regex_extractor(self, correlation: Dict[str, Any]) -> ET.Element:
        """
        Create RegexExtractor element

        Args:
            correlation: Correlation data

        Returns:
            RegexExtractor XML element
        """
        extractor = ET.Element(JMETER_ELEMENTS['REGEX_EXTRACTOR'], {
            'guiclass': 'RegexExtractorGui',
            'testclass': JMETER_ELEMENTS['REGEX_EXTRACTOR'],
            'testname': f"Extract {correlation.get('param_name', 'param')}",
            'enabled': 'true'
        })

        # Convert LB/RB to regex
        lb = correlation.get('left_boundary', '')
        rb = correlation.get('right_boundary', '')
        regex_pattern = self._convert_boundaries_to_regex(lb, rb)

        # Convert ordinal
        ordinal = correlation.get('ordinal', '1')
        if ordinal == 'Last':
            match_no = '-1'
        elif ordinal == 'All':
            match_no = '0'
        else:
            match_no = str(ordinal)

        self._add_string_prop(extractor, 'RegexExtractor.useHeaders', 'false')
        self._add_string_prop(extractor, 'RegexExtractor.refname', correlation.get('param_name', 'param'))
        self._add_string_prop(extractor, 'RegexExtractor.regex', regex_pattern)
        self._add_string_prop(extractor, 'RegexExtractor.template', '$1$')
        self._add_string_prop(extractor, 'RegexExtractor.default', '')
        self._add_string_prop(extractor, 'RegexExtractor.match_number', match_no)

        return extractor

    def _create_json_extractor(self, correlation: Dict[str, Any]) -> ET.Element:
        """
        Create JSONPostProcessor element

        Args:
            correlation: Correlation data

        Returns:
            JSONPostProcessor XML element
        """
        extractor = ET.Element(JMETER_ELEMENTS['JSON_EXTRACTOR'], {
            'guiclass': 'JSONPostProcessorGui',
            'testclass': JMETER_ELEMENTS['JSON_EXTRACTOR'],
            'testname': f"Extract JSON {correlation.get('param_name', 'param')}",
            'enabled': 'true'
        })

        self._add_string_prop(extractor, 'JSONPostProcessor.referenceNames', correlation.get('param_name', 'param'))
        self._add_string_prop(extractor, 'JSONPostProcessor.jsonPathExprs', correlation.get('json_path', ''))
        self._add_string_prop(extractor, 'JSONPostProcessor.match_numbers', '1')
        self._add_string_prop(extractor, 'JSONPostProcessor.defaultValues', '')

        return extractor

    def _create_constant_timer(self, delay_ms: int) -> ET.Element:
        """
        Create ConstantTimer element

        Args:
            delay_ms: Delay in milliseconds

        Returns:
            ConstantTimer XML element
        """
        timer = ET.Element(JMETER_ELEMENTS['CONSTANT_TIMER'], {
            'guiclass': 'ConstantTimerGui',
            'testclass': JMETER_ELEMENTS['CONSTANT_TIMER'],
            'testname': 'Think Time',
            'enabled': 'true'
        })

        self._add_string_prop(timer, 'ConstantTimer.delay', str(delay_ms))

        return timer

    def _create_transaction_controller(self, name: str) -> ET.Element:
        """
        Create TransactionController element

        Args:
            name: Transaction name

        Returns:
            TransactionController XML element
        """
        controller = ET.Element(JMETER_ELEMENTS['TRANSACTION_CONTROLLER'], {
            'guiclass': 'TransactionControllerGui',
            'testclass': JMETER_ELEMENTS['TRANSACTION_CONTROLLER'],
            'testname': name,
            'enabled': 'true'
        })

        self._add_bool_prop(controller, 'TransactionController.includeTimers', False)
        self._add_bool_prop(controller, 'TransactionController.parent', True)

        return controller

    def _convert_boundaries_to_regex(self, lb: str, rb: str) -> str:
        """
        Convert left/right boundaries to regex pattern

        Args:
            lb: Left boundary
            rb: Right boundary

        Returns:
            Regex pattern string
        """
        # Escape special regex characters
        lb_escaped = re.escape(lb) if lb else ''
        rb_escaped = re.escape(rb) if rb else ''

        # Build pattern with capture group
        if lb_escaped and rb_escaped:
            return f"{lb_escaped}(.+?){rb_escaped}"
        elif lb_escaped:
            return f"{lb_escaped}(.+)"
        elif rb_escaped:
            return f"(.+?){rb_escaped}"
        else:
            return "(.+)"

    def _add_string_prop(self, parent: ET.Element, name: str, value: str) -> None:
        """
        Add stringProp element

        Args:
            parent: Parent XML element
            name: Property name
            value: Property value
        """
        prop = ET.SubElement(parent, 'stringProp', {'name': name})
        prop.text = str(value)

    def _add_bool_prop(self, parent: ET.Element, name: str, value: bool) -> None:
        """
        Add boolProp element

        Args:
            parent: Parent XML element
            name: Property name
            value: Property value
        """
        prop = ET.SubElement(parent, 'boolProp', {'name': name})
        prop.text = 'true' if value else 'false'

    def _add_argument(self, parent: ET.Element, arg_name: str, arg_value: str) -> None:
        """
        Add argument element

        Args:
            parent: Parent collectionProp element
            arg_name: Argument name
            arg_value: Argument value
        """
        elem_prop = ET.SubElement(parent, 'elementProp', {
            'name': arg_name,
            'elementType': 'Argument'
        })

        self._add_string_prop(elem_prop, 'Argument.name', arg_name)
        self._add_string_prop(elem_prop, 'Argument.value', arg_value)
        self._add_string_prop(elem_prop, 'Argument.metadata', '=')

    def _create_header_manager(self, headers: list) -> ET.Element:
        """
        Create HeaderManager element

        Args:
            headers: List of header dictionaries with 'name' and 'value'

        Returns:
            HeaderManager XML element
        """
        header_manager = ET.Element(JMETER_ELEMENTS['HEADER_MANAGER'], {
            'guiclass': 'HeaderPanel',
            'testclass': JMETER_ELEMENTS['HEADER_MANAGER'],
            'testname': 'HTTP Header Manager',
            'enabled': 'true'
        })

        coll_prop = ET.SubElement(header_manager, 'collectionProp', {'name': 'HeaderManager.headers'})

        for header in headers:
            header_elem = ET.SubElement(coll_prop, 'elementProp', {
                'name': '',
                'elementType': 'Header'
            })

            self._add_string_prop(header_elem, 'Header.name', header.get('name', ''))
            self._add_string_prop(header_elem, 'Header.value', header.get('value', ''))

        return header_manager

    def _create_cookie_manager(self) -> ET.Element:
        """
        Create CookieManager element

        Returns:
            CookieManager XML element
        """
        cookie_manager = ET.Element(JMETER_ELEMENTS['COOKIE_MANAGER'], {
            'guiclass': 'CookiePanel',
            'testclass': JMETER_ELEMENTS['COOKIE_MANAGER'],
            'testname': 'HTTP Cookie Manager',
            'enabled': 'true'
        })

        self._add_bool_prop(cookie_manager, 'CookieManager.clearEachIteration', False)
        ET.SubElement(cookie_manager, 'collectionProp', {'name': 'CookieManager.cookies'})

        return cookie_manager

    def _format_xml(self, root: ET.Element) -> str:
        """
        Format XML with consistent indentation and clean output

        Args:
            root: Root XML element

        Returns:
            Formatted XML string
        """
        # Convert to string first
        xml_string = ET.tostring(root, encoding='utf-8')

        # Parse with minidom for pretty printing
        dom = minidom.parseString(xml_string)

        # Generate pretty XML with 2-space indentation
        pretty_xml = dom.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

        # Clean up the output
        lines = []
        for line in pretty_xml.split('\n'):
            # Skip empty lines
            if not line.strip():
                continue
            # Skip XML declaration if it's the default one (we'll add our own)
            if line.strip().startswith('<?xml') and 'version="1.0"' in line:
                continue
            lines.append(line)

        # Add proper XML declaration at the beginning
        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>'
        result = [xml_declaration] + lines

        return '\n'.join(result)
