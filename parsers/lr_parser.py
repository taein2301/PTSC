"""
LoadRunner C Script Parser

Parses LoadRunner C scripts and extracts:
- Function boundaries (vuser_init, Action, vuser_end)
- HTTP function calls and parameters
- Transaction markers
- Variable declarations and usage
- Control flow structures
"""

import re
from typing import Dict, List, Any, Optional
from utils.constants import LR_FUNCTIONS, ERROR_CODES


class LRParser:
    """Parser for LoadRunner C scripts"""

    def __init__(self):
        """Initialize the LoadRunner parser"""
        self.script_content = ""
        self.lines = []

    def parse(self, lr_content: str) -> Dict[str, Any]:
        """
        Parse LoadRunner C script content

        Args:
            lr_content: LoadRunner C script as string

        Returns:
            Dictionary containing parsed script data
        """
        self.script_content = lr_content
        self.lines = lr_content.split('\n')

        try:
            # Extract functions
            vuser_init_code = self._extract_function(LR_FUNCTIONS['VUSER_INIT'])
            action_code = self._extract_function(LR_FUNCTIONS['ACTION'])
            vuser_end_code = self._extract_function(LR_FUNCTIONS['VUSER_END'])

            # Parse vuser_init for variables
            variables = self._parse_variables(vuser_init_code)

            # Parse Action for HTTP requests and logic
            http_requests = self._parse_http_requests(action_code)
            transactions = self._parse_transactions(action_code)
            think_times = self._parse_think_times(action_code)
            correlations = self._parse_correlations(action_code)
            headers = self._parse_headers(action_code)
            control_flows = self._parse_control_flow(action_code)

            return {
                'success': True,
                'vuser_init': vuser_init_code,
                'action': action_code,
                'vuser_end': vuser_end_code,
                'variables': variables,
                'http_requests': http_requests,
                'transactions': transactions,
                'think_times': think_times,
                'correlations': correlations,
                'headers': headers,
                'control_flows': control_flows
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"{ERROR_CODES['PARSING_ERROR']}: {str(e)}",
                'data': None
            }

    def _extract_function(self, function_name: str) -> str:
        """
        Extract a specific function's body from the script

        Args:
            function_name: Name of the function to extract

        Returns:
            Function body as string
        """
        in_function = False
        brace_count = 0
        function_lines = []

        for line in self.lines:
            stripped = line.strip()

            # Find function start
            if not in_function and function_name in stripped and '()' in stripped:
                in_function = True
                continue

            if in_function:
                # Track braces to find function end
                brace_count += stripped.count('{')
                brace_count -= stripped.count('}')

                if brace_count < 0:  # Function ended
                    break

                function_lines.append(line)

        return '\n'.join(function_lines)

    def _parse_variables(self, code: str) -> Dict[str, str]:
        """
        Parse variable declarations from code

        Args:
            code: Function code

        Returns:
            Dictionary of variable name-value pairs
        """
        variables = {}

        # Pattern for lr_save_string("value", "varname");
        pattern = r'lr_save_string\s*\(\s*"([^"]*)",\s*"([^"]*)"\s*\)'
        matches = re.finditer(pattern, code)

        for match in matches:
            value = match.group(1)
            varname = match.group(2)
            variables[varname] = value

        return variables

    def _parse_http_requests(self, code: str) -> List[Dict[str, Any]]:
        """
        Parse HTTP requests from code

        Args:
            code: Function code

        Returns:
            List of HTTP request dictionaries
        """
        requests = []

        # Parse web_url calls
        web_url_pattern = r'web_url\s*\((.*?)\s*LAST\s*\);'
        for match in re.finditer(web_url_pattern, code, re.DOTALL):
            request_data = self._parse_web_url(match.group(1))
            if request_data:
                requests.append(request_data)

        # Parse web_submit_data calls
        web_submit_pattern = r'web_submit_data\s*\((.*?)\s*LAST\s*\);'
        for match in re.finditer(web_submit_pattern, code, re.DOTALL):
            request_data = self._parse_web_submit_data(match.group(1))
            if request_data:
                requests.append(request_data)

        # Parse web_custom_request calls
        web_custom_pattern = r'web_custom_request\s*\((.*?)\s*LAST\s*\);'
        for match in re.finditer(web_custom_pattern, code, re.DOTALL):
            request_data = self._parse_web_custom_request(match.group(1))
            if request_data:
                requests.append(request_data)

        return requests

    def _parse_web_url(self, params: str) -> Optional[Dict[str, Any]]:
        """
        Parse web_url function parameters

        Args:
            params: Function parameters string

        Returns:
            Dictionary with request data
        """
        # Extract name
        name_match = re.search(r'"([^"]*)"', params)
        name = name_match.group(1) if name_match else "GET Request"

        # Extract URL
        url_match = re.search(r'URL\s*=\s*"([^"]*)"', params)
        url = url_match.group(1) if url_match else ""

        if not url:
            return None

        # Parse URL components
        parsed_url = self._parse_url(url)

        return {
            'type': 'web_url',
            'name': name,
            'method': 'GET',
            'url': url,
            'protocol': parsed_url.get('protocol', 'https'),
            'domain': parsed_url.get('domain', ''),
            'port': parsed_url.get('port', ''),
            'path': parsed_url.get('path', '/'),
            'arguments': []
        }

    def _parse_web_submit_data(self, params: str) -> Optional[Dict[str, Any]]:
        """
        Parse web_submit_data function parameters

        Args:
            params: Function parameters string

        Returns:
            Dictionary with request data
        """
        # Extract name
        name_match = re.search(r'"([^"]*)"', params)
        name = name_match.group(1) if name_match else "POST Request"

        # Extract action URL
        action_match = re.search(r'Action\s*=\s*"([^"]*)"', params)
        url = action_match.group(1) if action_match else ""

        if not url:
            return None

        # Extract parameters (Name/Value pairs)
        arguments = []
        name_value_pattern = r'Name\s*=\s*"([^"]*)",\s*Value\s*=\s*"([^"]*)"'
        for match in re.finditer(name_value_pattern, params):
            arg_name = match.group(1)
            arg_value = match.group(2)
            arguments.append({'name': arg_name, 'value': arg_value})

        # Extract body if present
        body_match = re.search(r'Body\s*=\s*"([^"]*)"', params)
        body = body_match.group(1) if body_match else ""

        # Parse URL components
        parsed_url = self._parse_url(url)

        return {
            'type': 'web_submit_data',
            'name': name,
            'method': 'POST',
            'url': url,
            'protocol': parsed_url.get('protocol', 'https'),
            'domain': parsed_url.get('domain', ''),
            'port': parsed_url.get('port', ''),
            'path': parsed_url.get('path', '/'),
            'arguments': arguments,
            'body': body
        }

    def _parse_web_custom_request(self, params: str) -> Optional[Dict[str, Any]]:
        """
        Parse web_custom_request function parameters

        Args:
            params: Function parameters string

        Returns:
            Dictionary with request data
        """
        # Extract name
        name_match = re.search(r'"([^"]*)"', params)
        name = name_match.group(1) if name_match else "Custom Request"

        # Extract URL
        url_match = re.search(r'URL\s*=\s*"([^"]*)"', params)
        url = url_match.group(1) if url_match else ""

        # Extract method
        method_match = re.search(r'Method\s*=\s*"?([^",\s]*)"?', params)
        method = method_match.group(1) if method_match else "GET"

        # Extract body if present
        body_match = re.search(r'Body\s*=\s*"([^"]*)"', params)
        body = body_match.group(1) if body_match else ""

        if not url:
            return None

        # Parse URL components
        parsed_url = self._parse_url(url)

        return {
            'type': 'web_custom_request',
            'name': name,
            'method': method.upper(),
            'url': url,
            'protocol': parsed_url.get('protocol', 'https'),
            'domain': parsed_url.get('domain', ''),
            'port': parsed_url.get('port', ''),
            'path': parsed_url.get('path', '/'),
            'body': body,
            'arguments': []
        }

    def _parse_url(self, url: str) -> Dict[str, str]:
        """
        Parse URL into components

        Args:
            url: URL string

        Returns:
            Dictionary with URL components
        """
        # Pattern: protocol://domain:port/path
        pattern = r'^(https?):\/\/([^:\/]+)(?::(\d+))?(\/.*)?$'
        match = re.match(pattern, url)

        if match:
            return {
                'protocol': match.group(1),
                'domain': match.group(2),
                'port': match.group(3) or '',
                'path': match.group(4) or '/'
            }

        # Fallback
        return {
            'protocol': 'https',
            'domain': url,
            'port': '',
            'path': '/'
        }

    def _parse_transactions(self, code: str) -> List[Dict[str, str]]:
        """
        Parse transaction markers

        Args:
            code: Function code

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        # Pattern for lr_start_transaction
        start_pattern = r'lr_start_transaction\s*\(\s*"([^"]*)"\s*\)'
        for match in re.finditer(start_pattern, code):
            transaction_name = match.group(1)
            transactions.append({
                'type': 'start',
                'name': transaction_name
            })

        # Pattern for lr_end_transaction
        end_pattern = r'lr_end_transaction\s*\(\s*"([^"]*)"\s*,\s*([^)]+)\s*\)'
        for match in re.finditer(end_pattern, code):
            transaction_name = match.group(1)
            transactions.append({
                'type': 'end',
                'name': transaction_name
            })

        return transactions

    def _parse_think_times(self, code: str) -> List[Dict[str, Any]]:
        """
        Parse think time calls

        Args:
            code: Function code

        Returns:
            List of think time dictionaries
        """
        think_times = []

        # Pattern for lr_think_time
        pattern = r'lr_think_time\s*\(\s*([0-9.]+)\s*\)'
        for match in re.finditer(pattern, code):
            duration = match.group(1)
            think_times.append({
                'duration_seconds': float(duration),
                'duration_ms': int(float(duration) * 1000)
            })

        return think_times

    def _parse_correlations(self, code: str) -> List[Dict[str, Any]]:
        """
        Parse correlation functions

        Args:
            code: Function code

        Returns:
            List of correlation dictionaries
        """
        correlations = []

        # Pattern for web_reg_save_param
        pattern = r'web_reg_save_param\s*\((.*?)\s*LAST\s*\);'
        for match in re.finditer(pattern, code, re.DOTALL):
            correlation = self._parse_web_reg_save_param(match.group(1))
            if correlation:
                correlations.append(correlation)

        # Pattern for web_reg_save_param_json
        json_pattern = r'web_reg_save_param_json\s*\((.*?)\s*LAST\s*\);'
        for match in re.finditer(json_pattern, code, re.DOTALL):
            correlation = self._parse_web_reg_save_param_json(match.group(1))
            if correlation:
                correlations.append(correlation)

        return correlations

    def _parse_web_reg_save_param(self, params: str) -> Optional[Dict[str, Any]]:
        """
        Parse web_reg_save_param function parameters

        Args:
            params: Function parameters string

        Returns:
            Dictionary with correlation data
        """
        # Extract parameter name
        param_match = re.search(r'"([^"]*)"', params)
        if not param_match:
            return None

        param_name = param_match.group(1)

        # Extract left boundary
        lb_match = re.search(r'LB\s*=\s*"([^"]*)"', params)
        lb = lb_match.group(1) if lb_match else ""

        # Extract right boundary
        rb_match = re.search(r'RB\s*=\s*"([^"]*)"', params)
        rb = rb_match.group(1) if rb_match else ""

        # Extract ordinal
        ord_match = re.search(r'Ordinal\s*=\s*"?([^",\s]*)"?', params)
        ordinal = ord_match.group(1) if ord_match else "1"

        return {
            'type': 'regex',
            'param_name': param_name,
            'left_boundary': lb,
            'right_boundary': rb,
            'ordinal': ordinal
        }

    def _parse_web_reg_save_param_json(self, params: str) -> Optional[Dict[str, Any]]:
        """
        Parse web_reg_save_param_json function parameters

        Args:
            params: Function parameters string

        Returns:
            Dictionary with JSON correlation data
        """
        # Extract parameter name
        param_match = re.search(r'ParamName\s*=\s*"?([^",\s]*)"?', params)
        if not param_match:
            return None

        param_name = param_match.group(1)

        # Extract JSON path
        path_match = re.search(r'QueryString\s*=\s*"([^"]*)"', params)
        json_path = path_match.group(1) if path_match else ""

        return {
            'type': 'json',
            'param_name': param_name,
            'json_path': json_path
        }

    def _parse_headers(self, code: str) -> List[Dict[str, str]]:
        """
        Parse web_add_header function calls

        Args:
            code: Function code

        Returns:
            List of header dictionaries
        """
        headers = []

        # Pattern for web_add_header
        pattern = r'web_add_header\s*\(\s*"([^"]*)"\s*\)'
        for match in re.finditer(pattern, code):
            header_line = match.group(1)

            # Split header into name and value
            if ':' in header_line:
                parts = header_line.split(':', 1)
                header_name = parts[0].strip()
                header_value = parts[1].strip()

                headers.append({
                    'name': header_name,
                    'value': header_value
                })

        return headers

    def _parse_control_flow(self, code: str) -> List[Dict[str, Any]]:
        """
        Parse control flow structures (if, for, while)

        Args:
            code: Function code

        Returns:
            List of control flow dictionaries
        """
        control_flows = []

        # Pattern for if statements
        if_pattern = r'if\s*\((.*?)\)\s*\{'
        for match in re.finditer(if_pattern, code):
            condition = match.group(1)
            control_flows.append({
                'type': 'if',
                'condition': condition.strip()
            })

        # Pattern for for loops
        for_pattern = r'for\s*\((.*?)\)\s*\{'
        for match in re.finditer(for_pattern, code):
            loop_def = match.group(1)
            control_flows.append({
                'type': 'for',
                'definition': loop_def.strip()
            })

        # Pattern for while loops
        while_pattern = r'while\s*\((.*?)\)\s*\{'
        for match in re.finditer(while_pattern, code):
            condition = match.group(1)
            control_flows.append({
                'type': 'while',
                'condition': condition.strip()
            })

        return control_flows
