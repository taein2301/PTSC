"""
LoadRunner Code Generator

Generates LoadRunner C script code from parsed data structures.
Handles proper formatting, function calls, and LoadRunner-specific syntax.
"""

from typing import Dict, List, Any
from utils.formatters import CodeFormatter
from utils.helpers import StringHelper
from utils.constants import LR_FUNCTIONS


class LRGenerator:
    """Generator for LoadRunner C scripts"""

    def __init__(self):
        """Initialize the LoadRunner generator"""
        self.formatter = CodeFormatter()
        self.string_helper = StringHelper()
        self.indent_level = 1
        self.indent_size = 4

    def generate(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate complete LoadRunner C script from parsed data

        Args:
            parsed_data: Parsed test plan data

        Returns:
            Complete LoadRunner C script as string
        """
        script_parts = []

        # Add header comments and includes
        script_parts.append(self._generate_header(parsed_data))
        script_parts.append("\n")

        # Generate vuser functions
        script_parts.append(self._generate_vuser_init(parsed_data))
        script_parts.append("\n")
        script_parts.append(self._generate_action(parsed_data))
        script_parts.append("\n")
        script_parts.append(self._generate_vuser_end(parsed_data))

        full_script = "\n".join(script_parts)

        # Format the code
        return self.formatter.format_c_code(full_script)

    def _generate_header(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate header with includes and comments

        Args:
            parsed_data: Parsed test plan data

        Returns:
            Header section as string
        """
        test_plan_name = parsed_data.get('test_plan', {}).get('name', 'Unknown Test Plan')

        header = f"""/*
 * LoadRunner C Script
 * Converted from JMeter Test Plan: {test_plan_name}
 *
 * NOTE: This script was automatically converted.
 * Please review and test before using in production.
 */

#include "web_api.h"
#include "lrun.h"
#include "web_custom_body.h"

/*
 * Runtime Settings:
 * - Thread Count: Configure in Runtime Settings > Run Logic
 * - Ramp-up: Configure in Runtime Settings > Run Logic > Start
 * - Think Time: Configure in Runtime Settings > Think Time
 */
"""
        return header

    def _generate_vuser_init(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate vuser_init function

        Args:
            parsed_data: Parsed test plan data

        Returns:
            vuser_init function as string
        """
        lines = []
        lines.append(f"{LR_FUNCTIONS['VUSER_INIT']}()")
        lines.append("{")

        # Add user variables initialization
        user_vars = parsed_data.get('user_variables', {})
        if user_vars:
            lines.append(self._indent("// User defined variables"))
            for var_name, var_value in user_vars.items():
                safe_name = self.string_helper.sanitize_variable_name(var_name)
                escaped_value = self.formatter.escape_c_string(var_value)
                lines.append(self._indent(f'lr_save_string("{escaped_value}", "{safe_name}");'))
            lines.append("")

        # Add common initialization
        lines.append(self._indent("// Set web options"))
        lines.append(self._indent('lr_think_time(1);'))
        lines.append("")
        lines.append(self._indent("return 0;"))
        lines.append("}")

        return "\n".join(lines)

    def _generate_action(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate Action function with main script logic

        Args:
            parsed_data: Parsed test plan data

        Returns:
            Action function as string
        """
        lines = []
        lines.append(f"{LR_FUNCTIONS['ACTION']}()")
        lines.append("{")

        # Process each thread group
        thread_groups = parsed_data.get('thread_groups', [])

        if not thread_groups:
            lines.append(self._indent("// No samplers to convert"))
            lines.append(self._indent("return 0;"))
            lines.append("}")
            return "\n".join(lines)

        # For simplicity, combine all thread groups into Action
        # In a real scenario, you might want separate actions
        for tg_idx, thread_group in enumerate(thread_groups):
            if tg_idx > 0:
                lines.append("")
                lines.append(self._indent(f"// Thread Group: {thread_group['name']}"))
                lines.append("")

            # Process headers (add them before requests)
            headers = thread_group.get('headers', [])
            if headers:
                lines.append(self._indent("// Add headers"))
                for header in headers:
                    lines.append(self._generate_header_call(header))
                lines.append("")

            # Process samplers
            samplers = thread_group.get('samplers', [])
            extractors = thread_group.get('extractors', [])
            timers = thread_group.get('timers', [])
            controllers = thread_group.get('controllers', [])

            # Track transaction controllers
            in_transaction = False
            transaction_name = None

            for sampler_idx, sampler in enumerate(samplers):
                # Check if this sampler is in a transaction
                if controllers and sampler_idx < len(controllers):
                    controller = controllers[sampler_idx]
                    if controller.get('type') == 'transaction' and not in_transaction:
                        transaction_name = controller['name']
                        lines.append(self._generate_transaction_start(transaction_name))
                        in_transaction = True

                # Add extractors that apply to this sampler (placed BEFORE request)
                if extractors:
                    for extractor in extractors:
                        lines.append(self._generate_extractor(extractor))

                # Generate the HTTP request
                lines.append(self._generate_http_request(sampler))
                lines.append("")

                # Add think time if specified
                if timers and sampler_idx < len(timers):
                    timer = timers[sampler_idx]
                    lines.append(self._generate_think_time(timer))
                    lines.append("")

                # Close transaction if needed
                if in_transaction and (sampler_idx == len(samplers) - 1 or
                                      (sampler_idx + 1 < len(controllers) and
                                       controllers[sampler_idx + 1].get('type') != 'transaction')):
                    lines.append(self._generate_transaction_end(transaction_name))
                    in_transaction = False

        lines.append(self._indent("return 0;"))
        lines.append("}")

        return "\n".join(lines)

    def _generate_vuser_end(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate vuser_end function

        Args:
            parsed_data: Parsed test plan data

        Returns:
            vuser_end function as string
        """
        lines = []
        lines.append(f"{LR_FUNCTIONS['VUSER_END']}()")
        lines.append("{")
        lines.append(self._indent("// Cleanup code"))
        lines.append(self._indent("return 0;"))
        lines.append("}")

        return "\n".join(lines)

    def _generate_http_request(self, sampler: Dict[str, Any]) -> str:
        """
        Generate HTTP request function call

        Args:
            sampler: Sampler data dictionary

        Returns:
            LoadRunner web function call
        """
        method = sampler.get('method', 'GET').upper()
        name = sampler.get('name', 'HTTP Request')
        url = self._build_url(sampler)

        if method == 'GET':
            return self._generate_web_url(name, url)
        elif method == 'POST':
            return self._generate_web_submit_data(sampler, name, url)
        else:
            return self._generate_web_custom_request(sampler, name, url, method)

    def _generate_web_url(self, name: str, url: str) -> str:
        """
        Generate web_url function call

        Args:
            name: Step name
            url: Full URL

        Returns:
            web_url function call
        """
        escaped_name = self.formatter.escape_c_string(name)
        escaped_url = self.formatter.escape_c_string(url)

        lines = []
        lines.append(self._indent(f'{LR_FUNCTIONS["WEB_URL"]}('))
        lines.append(self._indent(f'    "{escaped_name}",', level=1))
        lines.append(self._indent(f'    "URL={escaped_url}",', level=1))
        lines.append(self._indent('    LAST);', level=1))

        return "\n".join(lines)

    def _generate_web_submit_data(self, sampler: Dict[str, Any], name: str, url: str) -> str:
        """
        Generate web_submit_data function call

        Args:
            sampler: Sampler data
            name: Step name
            url: Full URL

        Returns:
            web_submit_data function call
        """
        escaped_name = self.formatter.escape_c_string(name)
        escaped_url = self.formatter.escape_c_string(url)

        lines = []
        lines.append(self._indent(f'{LR_FUNCTIONS["WEB_SUBMIT_DATA"]}('))
        lines.append(self._indent(f'    "{escaped_name}",', level=1))
        lines.append(self._indent(f'    "Action={escaped_url}",', level=1))

        # Add POST parameters
        arguments = sampler.get('arguments', [])
        post_body = sampler.get('post_body', '')

        if arguments:
            lines.append(self._indent('    "Method=POST",', level=1))
            for arg in arguments:
                arg_name = self.formatter.escape_c_string(arg['name'])
                arg_value = self.formatter.escape_c_string(arg['value'])

                # Convert JMeter variables to LoadRunner format
                if '${' in arg_value:
                    arg_value = self.string_helper.convert_jmeter_to_lr_variable(arg_value)
                    lines.append(self._indent(f'    "Name={arg_name}", "Value={arg_value}",', level=1))
                else:
                    lines.append(self._indent(f'    "Name={arg_name}", "Value={arg_value}",', level=1))
        elif post_body:
            escaped_body = self.formatter.escape_c_string(post_body)
            lines.append(self._indent(f'    "Body={escaped_body}",', level=1))

        lines.append(self._indent('    LAST);', level=1))

        return "\n".join(lines)

    def _generate_web_custom_request(self, sampler: Dict[str, Any], name: str, url: str, method: str) -> str:
        """
        Generate web_custom_request function call

        Args:
            sampler: Sampler data
            name: Step name
            url: Full URL
            method: HTTP method

        Returns:
            web_custom_request function call
        """
        escaped_name = self.formatter.escape_c_string(name)
        escaped_url = self.formatter.escape_c_string(url)

        lines = []
        lines.append(self._indent(f'{LR_FUNCTIONS["WEB_CUSTOM_REQUEST"]}('))
        lines.append(self._indent(f'    "{escaped_name}",', level=1))
        lines.append(self._indent(f'    "URL={escaped_url}",', level=1))
        lines.append(self._indent(f'    "Method={method}",', level=1))

        # Add body if present
        post_body = sampler.get('post_body', '')
        if post_body:
            escaped_body = self.formatter.escape_c_string(post_body)
            lines.append(self._indent(f'    "Body={escaped_body}",', level=1))

        lines.append(self._indent('    LAST);', level=1))

        return "\n".join(lines)

    def _generate_header_call(self, header: Dict[str, str]) -> str:
        """
        Generate web_add_header call

        Args:
            header: Header dictionary

        Returns:
            web_add_header function call
        """
        name = self.formatter.escape_c_string(header['name'])
        value = self.formatter.escape_c_string(header['value'])

        return self._indent(f'{LR_FUNCTIONS["WEB_ADD_HEADER"]}("{name}", "{value}");')

    def _generate_extractor(self, extractor: Dict[str, Any]) -> str:
        """
        Generate correlation function (web_reg_save_param)

        Args:
            extractor: Extractor data

        Returns:
            web_reg_save_param function call
        """
        extractor_type = extractor.get('type', 'regex')
        refname = extractor.get('refname', 'param')

        if extractor_type == 'json':
            return self._generate_json_extractor(extractor)
        else:
            return self._generate_regex_extractor(extractor)

    def _generate_regex_extractor(self, extractor: Dict[str, Any]) -> str:
        """
        Generate web_reg_save_param for regex extraction

        Args:
            extractor: Extractor data

        Returns:
            web_reg_save_param function call
        """
        refname = extractor.get('refname', 'param')
        regex = extractor.get('regex', '')
        match_no = extractor.get('match_no', '1')

        # Convert regex to LB/RB if possible (simplified)
        # This is a basic conversion - real implementation would be more sophisticated
        lb, rb = self._convert_regex_to_boundaries(regex)

        lines = []
        lines.append(self._indent(f'{LR_FUNCTIONS["WEB_REG_SAVE_PARAM"]}('))
        lines.append(self._indent(f'    "{refname}",', level=1))
        lines.append(self._indent(f'    "LB={lb}",', level=1))
        lines.append(self._indent(f'    "RB={rb}",', level=1))

        # Convert match_no: -1 = last, 0 or 1 = first, >1 = specific instance
        if match_no == '-1':
            ordinal = 'Last'
        elif match_no == '0':
            ordinal = 'All'
        else:
            ordinal = match_no

        lines.append(self._indent(f'    "Ordinal={ordinal}",', level=1))
        lines.append(self._indent('    LAST);', level=1))

        return "\n".join(lines)

    def _generate_json_extractor(self, extractor: Dict[str, Any]) -> str:
        """
        Generate web_reg_save_param_json for JSON extraction

        Args:
            extractor: Extractor data

        Returns:
            web_reg_save_param_json function call
        """
        refname = extractor.get('refname', 'param')
        jsonpath = extractor.get('jsonpath', '')

        lines = []
        lines.append(self._indent(f'{LR_FUNCTIONS["WEB_REG_SAVE_PARAM_JSON"]}('))
        lines.append(self._indent(f'    "ParamName={refname}",', level=1))
        lines.append(self._indent(f'    "QueryString={jsonpath}",', level=1))
        lines.append(self._indent('    LAST);', level=1))

        return "\n".join(lines)

    def _generate_think_time(self, timer: Dict[str, Any]) -> str:
        """
        Generate lr_think_time call

        Args:
            timer: Timer data

        Returns:
            lr_think_time function call
        """
        delay = timer.get('delay', '0')

        # Convert milliseconds to seconds (JMeter uses ms, LR uses seconds)
        try:
            delay_seconds = float(delay) / 1000.0
            return self._indent(f'{LR_FUNCTIONS["LR_THINK_TIME"]}({delay_seconds:.1f});')
        except ValueError:
            return self._indent(f'{LR_FUNCTIONS["LR_THINK_TIME"]}(1);')

    def _generate_transaction_start(self, name: str) -> str:
        """
        Generate lr_start_transaction call

        Args:
            name: Transaction name

        Returns:
            lr_start_transaction function call
        """
        escaped_name = self.formatter.escape_c_string(name)
        return self._indent(f'{LR_FUNCTIONS["LR_START_TRANSACTION"]}("{escaped_name}");')

    def _generate_transaction_end(self, name: str) -> str:
        """
        Generate lr_end_transaction call

        Args:
            name: Transaction name

        Returns:
            lr_end_transaction function call
        """
        escaped_name = self.formatter.escape_c_string(name)
        return self._indent(f'{LR_FUNCTIONS["LR_END_TRANSACTION"]}("{escaped_name}", LR_AUTO);')

    def _build_url(self, sampler: Dict[str, Any]) -> str:
        """
        Build full URL from sampler data

        Args:
            sampler: Sampler data

        Returns:
            Full URL string
        """
        protocol = sampler.get('protocol', 'https')
        domain = sampler.get('domain', '')
        port = sampler.get('port', '')
        path = sampler.get('path', '/')

        # Build URL
        url = f"{protocol}://{domain}"

        if port:
            url += f":{port}"

        url += path

        # Convert JMeter variables
        if '${' in url:
            url = self.string_helper.convert_jmeter_to_lr_variable(url)

        return url

    def _convert_regex_to_boundaries(self, regex: str) -> tuple:
        """
        Convert regex pattern to left/right boundaries

        This is a simplified conversion. Real implementation would be more sophisticated.

        Args:
            regex: Regular expression

        Returns:
            Tuple of (left_boundary, right_boundary)
        """
        # Simple heuristic: look for patterns like "prefix(.+?)suffix"
        # This is very basic and should be enhanced for production use

        if '(.+?)' in regex:
            parts = regex.split('(.+?)')
            lb = parts[0] if len(parts) > 0 else ''
            rb = parts[1] if len(parts) > 1 else ''
            return (lb, rb)
        elif '(.*)' in regex:
            parts = regex.split('(.*)')
            lb = parts[0] if len(parts) > 0 else ''
            rb = parts[1] if len(parts) > 1 else ''
            return (lb, rb)
        else:
            # Fallback
            return (regex, '')

    def _indent(self, text: str, level: int = None) -> str:
        """
        Add indentation to text

        Args:
            text: Text to indent
            level: Indentation level (uses self.indent_level if None)

        Returns:
            Indented text
        """
        if level is None:
            level = self.indent_level

        spaces = ' ' * (level * self.indent_size)
        return spaces + text
