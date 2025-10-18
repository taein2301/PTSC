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
                for header_manager in headers:
                    # HeaderManager contains a nested 'headers' array
                    if isinstance(header_manager, dict) and 'headers' in header_manager:
                        for header in header_manager['headers']:
                            lines.append(self._generate_header_call(header))
                    elif isinstance(header_manager, dict) and 'name' in header_manager and 'value' in header_manager:
                        # Direct header dict
                        lines.append(self._generate_header_call(header_manager))
                lines.append("")

            # Process samplers
            samplers = thread_group.get('samplers', [])
            extractors = thread_group.get('extractors', [])
            timers = thread_group.get('timers', [])
            controllers = thread_group.get('controllers', [])

            # Handle transactions that wrap multiple samplers
            # TransactionControllers are separate from samplers in JMeter structure
            transaction_controllers = [c for c in controllers if c.get('type') == 'TransactionController']

            # If there are transaction controllers, wrap samplers
            if transaction_controllers:
                for trans_ctrl in transaction_controllers:
                    trans_name = trans_ctrl.get('name', 'Transaction')
                    lines.append(self._generate_transaction_start(trans_name))
                    lines.append("")

                    # Add all samplers inside this transaction
                    for sampler_idx, sampler in enumerate(samplers):
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

                    lines.append(self._generate_transaction_end(trans_name))
                    lines.append("")
            else:
                # No transactions, just generate samplers
                for sampler_idx, sampler in enumerate(samplers):
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

        # Add POST parameters (check both 'parameters' and 'arguments' for backward compatibility)
        parameters = sampler.get('parameters', sampler.get('arguments', []))
        post_body = sampler.get('body', sampler.get('post_body', ''))

        if parameters:
            lines.append(self._indent('    "Method=POST",', level=1))
            # Add parameters as ITEMDATA
            for param in parameters:
                param_name = self.formatter.escape_c_string(param['name'])
                param_value = self.formatter.escape_c_string(param['value'])

                # Convert JMeter variables to LoadRunner format
                if '${' in param_value:
                    param_value = self.string_helper.convert_jmeter_to_lr_variable(param_value)

                lines.append(self._indent(f'    ITEMDATA,', level=1))
                lines.append(self._indent(f'        "Name={param_name}", "Value={param_value}", ENDITEM,', level=1))
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

    def _generate_cookie_call(self, cookie: Dict[str, Any]) -> str:
        """
        Generate web_add_cookie or web_set_cookie call

        Args:
            cookie: Cookie dictionary

        Returns:
            LoadRunner cookie function call
        """
        name = self.formatter.escape_c_string(cookie.get('name', ''))
        value = self.formatter.escape_c_string(cookie.get('value', ''))
        domain = cookie.get('domain', '')
        path = cookie.get('path', '/')

        lines = []
        lines.append(self._indent(f'{LR_FUNCTIONS["WEB_ADD_COOKIE"]}('))
        lines.append(self._indent(f'    "{name}={value};', level=1))

        if domain:
            lines.append(self._indent(f'    domain={domain};', level=1))

        if path:
            lines.append(self._indent(f'    path={path}");', level=1))
        else:
            lines[-1] = lines[-1].rstrip(';') + '");'

        return "\n".join(lines)

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

    def _generate_if_statement(self, condition: str, body_lines: List[str]) -> str:
        """
        Generate if statement for conditional execution

        Args:
            condition: Condition expression
            body_lines: Lines of code inside if block

        Returns:
            Complete if statement
        """
        lines = []
        # Convert JMeter condition to C condition if needed
        c_condition = self._convert_condition_to_c(condition)

        lines.append(self._indent(f'if ({c_condition})'))
        lines.append(self._indent('{'))

        for body_line in body_lines:
            lines.append(self._indent(body_line, level=self.indent_level + 1))

        lines.append(self._indent('}'))

        return "\n".join(lines)

    def _generate_for_loop(self, loop_count: int, body_lines: List[str]) -> str:
        """
        Generate for loop for iteration

        Args:
            loop_count: Number of iterations
            body_lines: Lines of code inside loop

        Returns:
            Complete for loop
        """
        lines = []
        lines.append(self._indent(f'for (int i = 0; i < {loop_count}; i++)'))
        lines.append(self._indent('{'))

        for body_line in body_lines:
            lines.append(self._indent(body_line, level=self.indent_level + 1))

        lines.append(self._indent('}'))

        return "\n".join(lines)

    def _generate_variable_save(self, var_name: str, var_value: str) -> str:
        """
        Generate lr_save_string call for variable assignment

        Args:
            var_name: Variable name
            var_value: Variable value

        Returns:
            lr_save_string function call
        """
        escaped_value = self.formatter.escape_c_string(var_value)
        safe_name = self.string_helper.sanitize_variable_name(var_name)

        return self._indent(f'{LR_FUNCTIONS["LR_SAVE_STRING"]}("{escaped_value}", "{safe_name}");')

    def _generate_error_check(self, assertion: Dict[str, Any]) -> str:
        """
        Generate error handling code for assertions

        Args:
            assertion: Assertion data dictionary

        Returns:
            Error checking code
        """
        test_field = assertion.get('test_field', 'response_data')
        test_type = assertion.get('test_type', 'contains')
        test_patterns = assertion.get('test_patterns', [])

        lines = []

        if not test_patterns:
            return ""

        # For simplicity, generate a basic check
        for pattern in test_patterns:
            escaped_pattern = self.formatter.escape_c_string(pattern)

            if test_type in ['contains', 'matches']:
                lines.append(self._indent('// Assertion: Check response contains expected value'))
                lines.append(self._indent('if (/* response check failed */)'))
                lines.append(self._indent('{'))
                lines.append(self._indent(f'    {LR_FUNCTIONS["LR_ERROR_MESSAGE"]}("Assertion failed: Expected pattern not found - {escaped_pattern}");', level=1))
                lines.append(self._indent(f'    {LR_FUNCTIONS["LR_ABORT"]}();', level=1))
                lines.append(self._indent('}'))

        return "\n".join(lines)

    def _convert_condition_to_c(self, condition: str) -> str:
        """
        Convert JMeter condition expression to C syntax

        Args:
            condition: JMeter condition

        Returns:
            C-style condition
        """
        # Replace JMeter variable references with LoadRunner format
        if '${' in condition:
            condition = self.string_helper.convert_jmeter_to_lr_variable(condition)

        # Convert common JMeter functions/operators to C
        condition = condition.replace(' == ', ' == ')
        condition = condition.replace(' eq ', ' == ')
        condition = condition.replace(' ne ', ' != ')
        condition = condition.replace(' gt ', ' > ')
        condition = condition.replace(' lt ', ' < ')
        condition = condition.replace(' && ', ' && ')
        condition = condition.replace(' || ', ' || ')

        # If condition contains LoadRunner variables, wrap in strcmp or similar
        if '{' in condition and '}' in condition:
            # This is a simplification - real implementation would parse properly
            condition = condition.replace('==', '== 0 && strcmp(lr_eval_string("')
            condition += '"), "") == 0'

        return condition

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
