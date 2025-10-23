"""
JMeter to LoadRunner Converter

Orchestrates the conversion process from JMeter JMX files to LoadRunner C scripts.
Uses JMXParser to parse input and LRGenerator to generate output.
"""

from typing import Tuple, Optional, Dict, Any
from converters.base_converter import BaseConverter
from parsers.jmx_parser import JMXParser
from generators.lr_generator import LRGenerator
from utils.constants import ERROR_CODES


class JMeterToLRConverter(BaseConverter):
    """Converter for JMeter JMX → LoadRunner C script"""

    def __init__(self, include_comments: bool = True):
        """Initialize the converter

        Args:
            include_comments: Whether to include descriptive comments in generated code
        """
        super().__init__()
        self.parser = JMXParser()
        self.generator = LRGenerator(include_comments=include_comments)

    def validate_input(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate JMX content before conversion

        Args:
            content: JMX file content as string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Input content is empty"

        # Check if it looks like XML
        if not content.strip().startswith('<?xml') and not content.strip().startswith('<'):
            return False, f"{ERROR_CODES['INVALID_XML']}: Content does not appear to be XML"

        # Check for jmeterTestPlan element
        if 'jmeterTestPlan' not in content:
            return False, f"{ERROR_CODES['INVALID_XML']}: Missing jmeterTestPlan element"

        # Check for TestPlan element
        if 'TestPlan' not in content:
            return False, f"{ERROR_CODES['MISSING_REQUIRED_FIELD']}: No TestPlan found in JMX"

        return True, None

    def convert(self, content: str) -> Dict[str, Any]:
        """
        Perform JMeter to LoadRunner conversion

        Args:
            content: JMX file content as string

        Returns:
            Dictionary with conversion results
        """
        try:
            # Parse XML content directly
            success, error = self.parser._parse_xml(content)
            if not success:
                self.add_error(error)
                return {
                    'success': False,
                    'data': None,
                    'errors': self.errors,
                    'warnings': self.warnings
                }

            # Parse JMX structure
            success, parse_result = self.parser.parse()

            if not success:
                error_msg = parse_result.get('error', 'Unknown parsing error')
                self.add_error(error_msg)
                return {
                    'success': False,
                    'data': None,
                    'errors': self.errors,
                    'warnings': self.warnings
                }

            # Reorganize parsed data to group elements with thread groups
            reorganized_data = self._reorganize_parsed_data(parse_result)

            # Track conversion statistics
            self._analyze_parsed_data(reorganized_data)

            # Add conversion warnings for unsupported elements
            self._check_for_unsupported_elements(reorganized_data)

            return {
                'success': True,
                'data': reorganized_data,
                'errors': self.errors,
                'warnings': self.warnings
            }

        except Exception as e:
            self.add_error(f"{ERROR_CODES['CONVERSION_ERROR']}: {str(e)}")
            return {
                'success': False,
                'data': None,
                'errors': self.errors,
                'warnings': self.warnings
            }

    def generate_output(self, converted_data: Dict[str, Any]) -> str:
        """
        Generate LoadRunner C script from converted data

        Args:
            converted_data: Parsed and converted data structure

        Returns:
            LoadRunner C script as string

        Raises:
            Exception: If generation fails
        """
        try:
            lr_script = self.generator.generate(converted_data)
            return lr_script

        except Exception as e:
            error_msg = f"{ERROR_CODES['CONVERSION_ERROR']}: Failed to generate output - {str(e)}"
            self.add_error(error_msg)
            # Re-raise the exception so execute_conversion can handle it properly
            raise Exception(error_msg) from e

    def _remove_duplicates(self, items: list) -> list:
        """
        Remove duplicate items from a list based on their name and type.

        Args:
            items: List of dictionaries with 'name' and 'type' keys

        Returns:
            List with duplicates removed
        """
        if not items:
            return []

        seen = set()
        unique_items = []

        for item in items:
            # Create a unique key based on name and type
            key = (item.get('name', ''), item.get('type', ''))

            if key not in seen:
                seen.add(key)
                unique_items.append(item)

        return unique_items

    def _reorganize_parsed_data(self, parse_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        The parser now organizes data hierarchically, so this method
        just passes through the structure and ensures required fields exist.

        Args:
            parse_result: Raw parsed data from JMXParser (already hierarchical)

        Returns:
            Data structure ready for code generation
        """
        thread_groups = parse_result.get('thread_groups', [])

        # If no thread groups exist, create a default one
        if not thread_groups:
            thread_groups = [{
                'name': 'Thread Group',
                'enabled': True,
                'num_threads': 1,
                'ramp_time': 1,
                'loops': 1,
                'samplers': [],
                'headers': [],
                'extractors': [],
                'timers': [],
                'assertions': [],
                'controllers': [],
                'cookies': []
            }]

        # Ensure all thread groups have required lists
        for tg in thread_groups:
            if 'samplers' not in tg:
                tg['samplers'] = []
            if 'headers' not in tg:
                tg['headers'] = []
            if 'extractors' not in tg:
                tg['extractors'] = []
            if 'timers' not in tg:
                tg['timers'] = []
            if 'assertions' not in tg:
                tg['assertions'] = []
            if 'controllers' not in tg:
                tg['controllers'] = []
            if 'cookies' not in tg:
                tg['cookies'] = []

        # Extract user variables from TestPlan variables
        user_vars = parse_result.get('variables', {})

        return {
            'test_plan': parse_result.get('test_plan', {}),
            'thread_groups': thread_groups,
            'user_variables': user_vars,
            'variables': user_vars,
            'elements': parse_result.get('elements', [])
        }

    def _analyze_parsed_data(self, parse_result: Dict[str, Any]) -> None:
        """
        Analyze parsed data and update conversion statistics

        Args:
            parse_result: Parsed JMX data
        """
        thread_groups = parse_result.get('thread_groups', [])

        for thread_group in thread_groups:
            samplers = thread_group.get('samplers', [])
            headers = thread_group.get('headers', [])
            extractors = thread_group.get('extractors', [])
            timers = thread_group.get('timers', [])
            assertions = thread_group.get('assertions', [])
            controllers = thread_group.get('controllers', [])

            # Count total items
            total_items = (len(samplers) + len(headers) + len(extractors) +
                          len(timers) + len(assertions) + len(controllers))

            self.increment_stat('items_total', total_items)

            # Count converted items (samplers, headers, extractors, timers, controllers)
            converted = len(samplers) + len(headers) + len(extractors) + len(timers) + len(controllers)
            self.increment_stat('items_converted', converted)

            # Assertions are partially supported (skipped for now)
            if assertions:
                self.increment_stat('items_skipped', len(assertions))
                self.add_warning(f"Skipped {len(assertions)} assertions - manual implementation required")

    def _check_for_unsupported_elements(self, parse_result: Dict[str, Any]) -> None:
        """
        Check for unsupported JMeter elements and add warnings

        Args:
            parse_result: Parsed JMX data
        """
        thread_groups = parse_result.get('thread_groups', [])

        for thread_group in thread_groups:
            # Check for cookies
            cookies = thread_group.get('cookies', [])
            if cookies:
                self.add_warning(f"Found {len(cookies)} cookies - may need manual configuration in LoadRunner")

            # Check for assertions
            assertions = thread_group.get('assertions', [])
            if assertions:
                self.add_warning(f"Found {len(assertions)} assertions - implement using lr_error_message() manually")

            # Check for complex controllers
            controllers = thread_group.get('controllers', [])
            if_controllers = [c for c in controllers if c.get('type') == 'if']
            while_controllers = [c for c in controllers if c.get('type') == 'while']

            if if_controllers:
                self.add_warning(f"Found {len(if_controllers)} If Controllers - implement using C if statements")

            if while_controllers:
                self.add_warning(f"Found {len(while_controllers)} While Controllers - implement using C while loops")

            # Warn about thread configuration
            num_threads = thread_group.get('num_threads', '1')
            if num_threads != '1':
                self.add_warning(f"Thread count ({num_threads}) should be configured in LoadRunner Runtime Settings")

            ramp_time = thread_group.get('ramp_time', '0')
            if ramp_time != '0':
                self.add_warning(f"Ramp-up time ({ramp_time}s) should be configured in LoadRunner Runtime Settings")

    def get_conversion_summary(self) -> str:
        """
        Get a human-readable conversion summary

        Returns:
            Summary string
        """
        stats = self.conversion_stats
        total = stats['items_converted'] + stats['items_skipped']
        accuracy = (stats['items_converted'] / total * 100) if total > 0 else 0

        summary_lines = [
            "=" * 60,
            "JMeter → LoadRunner Conversion Summary",
            "=" * 60,
            f"Total Items: {stats['items_total']}",
            f"Converted: {stats['items_converted']}",
            f"Skipped: {stats['items_skipped']}",
            f"Accuracy: {accuracy:.1f}%",
            ""
        ]

        if self.warnings:
            summary_lines.append("Warnings:")
            for warning in self.warnings:
                summary_lines.append(f"  ⚠ {warning}")
            summary_lines.append("")

        if self.errors:
            summary_lines.append("Errors:")
            for error in self.errors:
                summary_lines.append(f"  ✗ {error}")
            summary_lines.append("")

        summary_lines.append("=" * 60)

        return "\n".join(summary_lines)
