"""
LoadRunner to JMeter Converter

Orchestrates the conversion process from LoadRunner C scripts to JMeter JMX files.
Uses LRParser to parse input and JMXGenerator to generate output.
"""

from typing import Tuple, Optional, Dict, Any
from converters.base_converter import BaseConverter
from parsers.lr_parser import LRParser
from generators.jmx_generator import JMXGenerator
from utils.constants import ERROR_CODES, LR_FUNCTIONS


class LRToJMeterConverter(BaseConverter):
    """Converter for LoadRunner C script → JMeter JMX"""

    def __init__(self):
        """Initialize the converter"""
        super().__init__()
        self.parser = LRParser()
        self.generator = JMXGenerator()

    def validate_input(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate LoadRunner C script content before conversion

        Args:
            content: LoadRunner C script content as string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Input content is empty"

        # Check for basic LoadRunner structure
        has_includes = '#include' in content
        has_vuser_functions = any(func in content for func in
                                  [LR_FUNCTIONS['VUSER_INIT'], LR_FUNCTIONS['ACTION'], LR_FUNCTIONS['VUSER_END']])
        has_web_functions = any(func in content for func in
                               [LR_FUNCTIONS['WEB_URL'], LR_FUNCTIONS['WEB_SUBMIT_DATA'],
                                LR_FUNCTIONS['WEB_CUSTOM_REQUEST']])

        if not (has_includes or has_vuser_functions or has_web_functions):
            return False, f"{ERROR_CODES['INVALID_C_SYNTAX']}: Content does not appear to be a LoadRunner script"

        # Warn if no web functions found
        if not has_web_functions:
            return True, "Warning: No web functions found in script"

        return True, None

    def convert(self, content: str) -> Dict[str, Any]:
        """
        Perform LoadRunner to JMeter conversion

        Args:
            content: LoadRunner C script content as string

        Returns:
            Dictionary with conversion results
        """
        try:
            # Parse LoadRunner content
            parse_result = self.parser.parse(content)

            if not parse_result.get('success', False):
                error_msg = parse_result.get('error', 'Unknown parsing error')
                self.add_error(error_msg)
                return {
                    'success': False,
                    'data': None,
                    'errors': self.errors,
                    'warnings': self.warnings
                }

            # Track conversion statistics
            self._analyze_parsed_data(parse_result)

            # Add conversion warnings
            self._check_for_conversion_notes(parse_result)

            return {
                'success': True,
                'data': parse_result,
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
        Generate JMeter JMX file from converted data

        Args:
            converted_data: Parsed and converted data structure

        Returns:
            JMeter JMX file as string
        """
        try:
            jmx_content = self.generator.generate(converted_data)
            return jmx_content

        except Exception as e:
            self.add_error(f"{ERROR_CODES['CONVERSION_ERROR']}: Failed to generate output - {str(e)}")
            return f"<!-- Error generating JMX: {str(e)} -->"

    def _analyze_parsed_data(self, parse_result: Dict[str, Any]) -> None:
        """
        Analyze parsed data and update conversion statistics

        Args:
            parse_result: Parsed LoadRunner data
        """
        http_requests = parse_result.get('http_requests', [])
        variables = parse_result.get('variables', {})
        correlations = parse_result.get('correlations', [])
        think_times = parse_result.get('think_times', [])
        transactions = parse_result.get('transactions', [])

        # Count total items
        total_items = (len(http_requests) + len(variables) + len(correlations) +
                      len(think_times) + len(transactions))

        self.increment_stat('items_total', total_items)

        # All items are converted
        self.increment_stat('items_converted', total_items)

    def _check_for_conversion_notes(self, parse_result: Dict[str, Any]) -> None:
        """
        Check parsed data and add conversion warnings/notes

        Args:
            parse_result: Parsed LoadRunner data
        """
        http_requests = parse_result.get('http_requests', [])
        variables = parse_result.get('variables', {})
        correlations = parse_result.get('correlations', [])
        transactions = parse_result.get('transactions', [])

        # Check for empty script
        if not http_requests:
            self.add_warning("No HTTP requests found in LoadRunner script")

        # Check for variables
        if variables:
            self.add_warning(f"Converted {len(variables)} user variables to JMeter User Defined Variables")

        # Check for correlations
        if correlations:
            regex_count = len([c for c in correlations if c.get('type') == 'regex'])
            json_count = len([c for c in correlations if c.get('type') == 'json'])

            if regex_count > 0:
                self.add_warning(f"Converted {regex_count} web_reg_save_param to RegexExtractor")
            if json_count > 0:
                self.add_warning(f"Converted {json_count} web_reg_save_param_json to JSONPostProcessor")

        # Check for transactions
        if transactions:
            trans_starts = len([t for t in transactions if t.get('type') == 'start'])
            self.add_warning(f"Converted {trans_starts} transactions to TransactionController")

        # General warnings
        self.add_warning("Thread count and ramp-up should be configured in JMeter ThreadGroup properties")
        self.add_warning("Runtime settings from LoadRunner need to be configured in JMeter test plan")

        # Check for custom functions or advanced features
        vuser_init = parse_result.get('vuser_init', '')
        action = parse_result.get('action', '')

        if 'lr_eval_string' in action:
            self.add_warning("Found lr_eval_string calls - verify variable references converted correctly")

        if 'lr_output_message' in action or 'lr_log_message' in action:
            self.add_warning("Found logging functions - implement using JMeter Debug Sampler or listeners")

        if 'lr_error_message' in action:
            self.add_warning("Found lr_error_message - implement using JMeter Response Assertions")

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
            "LoadRunner → JMeter Conversion Summary",
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
