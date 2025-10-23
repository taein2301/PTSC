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

    def __init__(self, include_comments: bool = True):
        """Initialize the LoadRunner generator

        Args:
            include_comments: Whether to include descriptive comments in generated code
        """
        self.formatter = CodeFormatter()
        self.string_helper = StringHelper()
        self.indent_level = 1
        self.use_tabs = True  # LoadRunner uses tabs for indentation
        self.snapshot_counter = 1  # Track snapshot IDs for LoadRunner functions
        self.include_comments = include_comments

    def generate(self, parsed_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate LoadRunner C script files from parsed data

        Args:
            parsed_data: Parsed test plan data

        Returns:
            Dictionary with 4 files: globals.h, vuser_init.c, Action.c, vuser_end.c
        """
        files = {}

        # Generate globals.h
        files['globals.h'] = self._generate_globals_h(parsed_data)

        # Generate vuser_init.c
        files['vuser_init.c'] = self._generate_vuser_init_file(parsed_data)

        # Generate Action.c
        files['Action.c'] = self._generate_action_file(parsed_data)

        # Generate vuser_end.c
        files['vuser_end.c'] = self._generate_vuser_end_file(parsed_data)

        return files

    def generate_single_file(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate complete LoadRunner C script as single file (legacy support)

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

        # Return without additional formatting - already properly formatted
        return full_script

    def _generate_header(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate header with includes and optional comments

        Args:
            parsed_data: Parsed test plan data

        Returns:
            Header section as string with optional Korean comments
        """
        test_plan_name = parsed_data.get('test_plan', {}).get('name', 'Unknown Test Plan')

        if self.include_comments:
            header = f"""/*
 * ============================================================================
 * LoadRunner C 스크립트
 * ============================================================================
 *
 * 변환 정보:
 *   - 원본: JMeter Test Plan ({test_plan_name})
 *   - 변환 도구: Performance Test Script Converter (PTSC)
 *   - 생성일: 자동 변환
 *
 * 주의사항:
 *   이 스크립트는 자동으로 변환되었습니다.
 *   프로덕션 환경에서 사용하기 전에 반드시 검토 및 테스트를 수행하세요.
 *
 * ============================================================================
 */

#include "web_api.h"
#include "lrun.h"
#include "web_custom_body.h"
"""
        else:
            header = """#include "web_api.h"
#include "lrun.h"
#include "web_custom_body.h"
"""
        return header

    def _generate_vuser_init(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate vuser_init function

        Args:
            parsed_data: Parsed test plan data

        Returns:
            vuser_init function as string with optional Korean comments
        """
        lines = []

        if self.include_comments:
            lines.append("/*")
            lines.append(" * ============================================================================")
            lines.append(" * vuser_init - 가상 사용자 초기화")
            lines.append(" * ============================================================================")
            lines.append(" * 설명:")
            lines.append(" *   각 가상 사용자(Vuser)가 스크립트 실행을 시작하기 전에 한 번 실행됩니다.")
            lines.append(" *   로그인 정보, 전역 변수 등을 초기화하는 용도로 사용됩니다.")
            lines.append(" *")
            lines.append(" * 실행 시점:")
            lines.append(" *   - Action 함수 실행 전")
            lines.append(" *   - 각 Vuser당 1회만 실행")
            lines.append(" * ============================================================================")
            lines.append(" */")

        lines.append(f"{LR_FUNCTIONS['VUSER_INIT']}()")
        lines.append("{")

        # Add common initialization
        if self.include_comments:
            lines.append(self._indent("// ========================================"))
            lines.append(self._indent("// 초기 설정"))
            lines.append(self._indent("// ========================================"))
            lines.append(self._indent('// 초기 대기 시간 (1초)'))
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
            Action function as string with optional Korean comments
        """
        lines = []
        lines.append("")

        if self.include_comments:
            lines.append("/*")
            lines.append(" * ============================================================================")
            lines.append(" * Action - 메인 비즈니스 로직")
            lines.append(" * ============================================================================")
            lines.append(" * 설명:")
            lines.append(" *   실제 부하 테스트 시나리오가 실행되는 메인 함수입니다.")
            lines.append(" *   HTTP 요청, 트랜잭션, 검증 등 주요 비즈니스 로직이 포함됩니다.")
            lines.append(" *")
            lines.append(" * 실행 시점:")
            lines.append(" *   - vuser_init 실행 후")
            lines.append(" *   - Runtime Settings에 설정된 횟수만큼 반복 실행")
            lines.append(" *   - vuser_end 실행 전")
            lines.append(" * ============================================================================")
            lines.append(" */")

        lines.append(f"{LR_FUNCTIONS['ACTION']}()")
        lines.append("{")

        # Process each thread group
        thread_groups = parsed_data.get('thread_groups', [])

        if not thread_groups:
            if self.include_comments:
                lines.append(self._indent("// 변환할 샘플러가 없습니다"))
            lines.append(self._indent("return 0;"))
            lines.append("}")
            return "\n".join(lines)

        # For simplicity, combine all thread groups into Action
        # In a real scenario, you might want separate actions
        for tg_idx, thread_group in enumerate(thread_groups):
            if tg_idx > 0 and self.include_comments:
                lines.append("")
                lines.append(self._indent(f"// Thread Group: {thread_group['name']}"))
                lines.append("")

            # Process headers (add them before requests)
            headers = thread_group.get('headers', [])
            if headers:
                if self.include_comments:
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

            # Process controllers in order (they now contain their children)
            controllers = thread_group.get('controllers', [])
            samplers = thread_group.get('samplers', [])  # Top-level samplers not in controllers

            # Process all controllers in the order they appear
            for controller in controllers:
                ctrl_type = controller.get('type')
                ctrl_name = controller.get('name', 'Controller')

                if ctrl_type == 'TransactionController':
                    # Start transaction
                    lines.append(self._generate_transaction_start(ctrl_name))
                    lines.append("")

                    # Process samplers inside this transaction
                    ctrl_samplers = controller.get('samplers', [])
                    ctrl_extractors = controller.get('extractors', [])
                    ctrl_timers = controller.get('timers', [])

                    # Track which extractors/timers have been used
                    extractor_idx = 0
                    timer_idx = 0

                    for sampler_idx, sampler in enumerate(ctrl_samplers):
                        # Add extractor for THIS sampler (one extractor per sampler)
                        if extractor_idx < len(ctrl_extractors):
                            lines.append(self._generate_extractor(ctrl_extractors[extractor_idx]))
                            extractor_idx += 1

                        # Generate HTTP request
                        lines.append(self._generate_http_request(sampler))
                        lines.append("")

                        # Add timer for THIS sampler (one timer per sampler)
                        if timer_idx < len(ctrl_timers):
                            lines.append(self._generate_think_time(ctrl_timers[timer_idx]))
                            lines.append("")
                            timer_idx += 1

                    # End transaction
                    lines.append(self._generate_transaction_end(ctrl_name))
                    lines.append("")

                elif ctrl_type == 'LoopController':
                    loop_count = controller.get('loops', 1)

                    # Start loop
                    if self.include_comments:
                        lines.append(self._indent(f'// ======================================== 루프 시작: {ctrl_name} (반복 {loop_count}회) ========================================', level=1))
                    lines.append(self._generate_for_loop_start(loop_count))
                    lines.append("")

                    # Process samplers inside loop
                    loop_samplers = controller.get('samplers', [])
                    loop_extractors = controller.get('extractors', [])
                    loop_timers = controller.get('timers', [])

                    for sampler_idx, sampler in enumerate(loop_samplers):
                        # Add extractors before sampler
                        for extractor in loop_extractors:
                            extractor_lines = self._generate_extractor(extractor).split('\n')
                            for extr_line in extractor_lines:
                                lines.append(self._indent(extr_line, level=2))

                        # Generate HTTP request with extra indentation
                        request_lines = self._generate_http_request(sampler).split('\n')
                        for req_line in request_lines:
                            lines.append(self._indent(req_line, level=2))
                        lines.append("")

                        # Add timers
                        for timer in loop_timers:
                            timer_lines = self._generate_timer(timer).split('\n')
                            for timer_line in timer_lines:
                                lines.append(self._indent(timer_line, level=2))
                            lines.append("")

                    # End loop
                    lines.append(self._generate_for_loop_end())
                    if self.include_comments:
                        lines.append(self._indent(f'// ======================================== 루프 종료: {ctrl_name} ========================================', level=1))
                    lines.append("")

            # Process any top-level samplers and extractors (not in controllers)
            extractors = thread_group.get('extractors', [])
            timers = thread_group.get('timers', [])

            if samplers or extractors:
                # Track which extractors/timers have been used
                extractor_idx = 0
                timer_idx = 0

                for sampler_idx, sampler in enumerate(samplers):
                    # Add extractor BEFORE the sampler it applies to
                    if extractor_idx < len(extractors):
                        lines.append(self._generate_extractor(extractors[extractor_idx]))
                        lines.append("")
                        extractor_idx += 1

                    # Generate HTTP request
                    lines.append(self._generate_http_request(sampler))
                    lines.append("")

                    # Add timer after the sampler
                    if timer_idx < len(timers):
                        lines.append(self._generate_think_time(timers[timer_idx]))
                        lines.append("")
                        timer_idx += 1

        lines.append(self._indent("return 0;"))
        lines.append("}")

        return "\n".join(lines)

    def _generate_vuser_end(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate vuser_end function

        Args:
            parsed_data: Parsed test plan data

        Returns:
            vuser_end function as string with optional Korean comments
        """
        lines = []
        lines.append("")

        if self.include_comments:
            lines.append("/*")
            lines.append(" * ============================================================================")
            lines.append(" * vuser_end - 가상 사용자 종료")
            lines.append(" * ============================================================================")
            lines.append(" * 설명:")
            lines.append(" *   각 가상 사용자(Vuser)가 스크립트 실행을 종료한 후 한 번 실행됩니다.")
            lines.append(" *   연결 해제, 리소스 정리 등을 수행하는 용도로 사용됩니다.")
            lines.append(" *")
            lines.append(" * 실행 시점:")
            lines.append(" *   - Action 함수 실행 후")
            lines.append(" *   - 각 Vuser당 1회만 실행")
            lines.append(" * ============================================================================")
            lines.append(" */")

        lines.append(f"{LR_FUNCTIONS['VUSER_END']}()")
        lines.append("{")

        if self.include_comments:
            lines.append(self._indent("// ========================================"))
            lines.append(self._indent("// 종료 처리"))
            lines.append(self._indent("// ========================================"))
            lines.append(self._indent("// 필요시 로그아웃, 연결 해제 등의 정리 작업을 수행합니다"))
        lines.append("")
        lines.append(self._indent("return 0;"))
        lines.append("}")

        return "\n".join(lines)

    def _generate_http_request(self, sampler: Dict[str, Any]) -> str:
        """
        Generate HTTP request function call with optional Korean comments

        Args:
            sampler: Sampler data dictionary

        Returns:
            LoadRunner web function call with optional Korean comments
        """
        method = sampler.get('method', 'GET').upper()
        name = sampler.get('name', 'HTTP Request')
        url = self._build_url(sampler)

        # Add Korean comment before the request (if enabled)
        comment = ""
        if self.include_comments:
            comment_lines = []
            comment_lines.append(self._indent("// ----------------------------------------"))
            comment_lines.append(self._indent(f"// HTTP 요청: {name}"))
            comment_lines.append(self._indent(f"// 메서드: {method}"))
            comment_lines.append(self._indent(f"// URL: {url[:80]}{'...' if len(url) > 80 else ''}"))
            comment_lines.append(self._indent("// ----------------------------------------"))
            comment = "\n".join(comment_lines) + "\n"

        if method == 'GET':
            return comment + self._generate_web_url(name, url, sampler)
        elif method == 'POST':
            # Check if this is form data or raw body (JSON)
            post_body = sampler.get('body', sampler.get('post_body', ''))
            parameters = sampler.get('parameters', sampler.get('arguments', []))

            # If there's a raw body (JSON, XML, etc.), use web_custom_request
            if post_body and not parameters:
                return comment + self._generate_web_custom_request(sampler, name, url, method)
            else:
                # Form data: use web_submit_data
                return comment + self._generate_web_submit_data(sampler, name, url)
        else:
            return comment + self._generate_web_custom_request(sampler, name, url, method)

    def _generate_web_url(self, name: str, url: str, sampler: Dict[str, Any] = None) -> str:
        """
        Generate web_url function call with LoadRunner VuGen standard parameters

        Args:
            name: Step name
            url: Full URL
            sampler: Optional sampler data for additional parameters

        Returns:
            web_url function call with complete LoadRunner standard parameters
        """
        escaped_name = self.formatter.escape_c_string(name)
        escaped_url = self.formatter.escape_c_string(url)
        snapshot_id = self._get_next_snapshot()

        # Use consistent indentation with spaces (4 spaces for level 1)
        indent = "    "  # 4 spaces

        lines = []
        lines.append(indent + f'{LR_FUNCTIONS["WEB_URL"]}("{escaped_name}", ')

        if self.include_comments:
            lines.append(indent + f'    "URL={escaped_url}",            // 요청할 URL 주소')
            lines.append(indent + f'    "Resource=0",                   // 0: 페이지 요청, 1: 리소스(이미지/CSS/JS) 요청')
            lines.append(indent + f'    "RecContentType=text/html",     // 응답 Content-Type (응답 검증용)')
            lines.append(indent + f'    "Referer=",                     // HTTP Referer 헤더 (이전 페이지 URL)')
            lines.append(indent + f'    "Snapshot={snapshot_id}",       // VuGen 스냅샷 파일명 (디버깅용)')
            lines.append(indent + f'    "Mode=HTML",                    // 파싱 모드: HTML, HTTP, ALL')
            lines.append(indent + f'    LAST );                         // 파라미터 목록의 끝을 나타냄 (필수)')
        else:
            lines.append(indent + f'    "URL={escaped_url}", ')
            lines.append(indent + f'    "Resource=0", ')
            lines.append(indent + f'    "RecContentType=text/html", ')
            lines.append(indent + f'    "Referer=", ')
            lines.append(indent + f'    "Snapshot={snapshot_id}", ')
            lines.append(indent + f'    "Mode=HTML", ')
            lines.append(indent + f'    LAST );')

        return "\n".join(lines)

    def _generate_web_submit_data(self, sampler: Dict[str, Any], name: str, url: str) -> str:
        """
        Generate web_submit_data function call with LoadRunner VuGen standard parameters

        Args:
            sampler: Sampler data
            name: Step name
            url: Full URL

        Returns:
            web_submit_data function call with complete LoadRunner standard parameters
        """
        escaped_name = self.formatter.escape_c_string(name)
        escaped_url = self.formatter.escape_c_string(url)
        snapshot_id = self._get_next_snapshot()

        # Use consistent indentation with spaces (4 spaces for level 1)
        indent = "    "  # 4 spaces

        lines = []
        lines.append(indent + f'{LR_FUNCTIONS["WEB_SUBMIT_DATA"]}("{escaped_name}", ')

        # Add POST parameters (check both 'parameters' and 'arguments' for backward compatibility)
        parameters = sampler.get('parameters', sampler.get('arguments', []))
        post_body = sampler.get('body', sampler.get('post_body', ''))

        # Add standard parameters with comments
        if self.include_comments:
            lines.append(indent + f'    "Action={escaped_url}",         // Form Action URL (POST 요청 대상)')
            lines.append(indent + f'    "Method=POST",                  // HTTP 메서드 (POST/GET)')
            lines.append(indent + f'    "RecContentType=text/html",     // 응답 Content-Type')
            lines.append(indent + f'    "Referer=",                     // HTTP Referer 헤더')
            lines.append(indent + f'    "Snapshot={snapshot_id}",       // VuGen 스냅샷 파일명')
            lines.append(indent + f'    "Mode=HTML",                    // 파싱 모드: HTML, HTTP, ALL')
        else:
            lines.append(indent + f'    "Action={escaped_url}", ')
            lines.append(indent + f'    "Method=POST", ')
            lines.append(indent + f'    "RecContentType=text/html", ')
            lines.append(indent + f'    "Referer=", ')
            lines.append(indent + f'    "Snapshot={snapshot_id}", ')
            lines.append(indent + f'    "Mode=HTML", ')

        # Add parameters as ITEMDATA if present
        if parameters:
            if self.include_comments:
                lines.append(indent + f'    ITEMDATA,                       // POST 파라미터 목록 시작')
            else:
                lines.append(indent + f'    ITEMDATA, ')

            for param in parameters:
                param_name = self.formatter.escape_c_string(param['name'])
                param_value = self.formatter.escape_c_string(param['value'])

                # Convert JMeter variables to LoadRunner format
                if '${' in param_value:
                    param_value = self.string_helper.convert_jmeter_to_lr_variable(param_value)

                if self.include_comments:
                    lines.append(indent + f'    "Name={param_name}", "Value={param_value}", ENDITEM,  // Form 파라미터: {param_name}')
                else:
                    lines.append(indent + f'    "Name={param_name}", "Value={param_value}", ENDITEM, ')

        if self.include_comments:
            lines.append(indent + f'    LAST );                         // 파라미터 목록 끝 (필수)')
        else:
            lines.append(indent + f'    LAST );')

        return "\n".join(lines)

    def _generate_web_custom_request(self, sampler: Dict[str, Any], name: str, url: str, method: str) -> str:
        """
        Generate web_custom_request function call with LoadRunner VuGen standard parameters

        Args:
            sampler: Sampler data
            name: Step name
            url: Full URL
            method: HTTP method (POST with JSON body, PUT, DELETE, PATCH, etc.)

        Returns:
            web_custom_request function call with complete LoadRunner standard parameters
        """
        escaped_name = self.formatter.escape_c_string(name)
        escaped_url = self.formatter.escape_c_string(url)
        snapshot_id = self._get_next_snapshot()

        # Use consistent indentation with spaces (4 spaces for level 1)
        indent = "    "  # 4 spaces

        lines = []
        lines.append(indent + f'{LR_FUNCTIONS["WEB_CUSTOM_REQUEST"]}("{escaped_name}", ')

        if self.include_comments:
            lines.append(indent + f'    "URL={escaped_url}",                // 요청 URL')
            lines.append(indent + f'    "Method={method}",                  // HTTP 메서드')
            lines.append(indent + f'    "Resource=0",                       // 리소스 타입')
            lines.append(indent + f'    "RecContentType=text/html",         // 응답 Content-Type')
            lines.append(indent + f'    "Referer=",                         // HTTP Referer')
            lines.append(indent + f'    "Snapshot={snapshot_id}",           // VuGen 스냅샷')
            lines.append(indent + f'    "Mode=HTML",                        // 파싱 모드')
        else:
            lines.append(indent + f'    "URL={escaped_url}", ')
            lines.append(indent + f'    "Method={method}", ')
            lines.append(indent + f'    "Resource=0", ')
            lines.append(indent + f'    "RecContentType=text/html", ')
            lines.append(indent + f'    "Referer=", ')
            lines.append(indent + f'    "Snapshot={snapshot_id}", ')
            lines.append(indent + f'    "Mode=HTML", ')

        # Add body if present (JSON, XML, raw text)
        post_body = sampler.get('body', sampler.get('post_body', ''))
        if post_body:
            escaped_body = self.formatter.escape_c_string(post_body)
            if self.include_comments:
                # Show preview of body content
                body_preview = post_body[:50] + ('...' if len(post_body) > 50 else '')
                lines.append(indent + f'    "Body={escaped_body}",              // Request Body: {body_preview}')
            else:
                lines.append(indent + f'    "Body={escaped_body}", ')

        if self.include_comments:
            lines.append(indent + f'    LAST );                             // 파라미터 목록 끝')
        else:
            lines.append(indent + f'    LAST );')

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

        return self._indent(f'{LR_FUNCTIONS["WEB_ADD_HEADER"]}("{name}", "{value}");', level=1)

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
        Generate web_reg_save_param for regex extraction with LoadRunner VuGen standard parameters

        Args:
            extractor: Extractor data

        Returns:
            web_reg_save_param function call with complete LoadRunner standard parameters and Korean comments
        """
        refname = extractor.get('refname', 'param')
        regex = extractor.get('regex', '')
        match_no = extractor.get('match_no', '1')

        # Convert regex to LB/RB if possible (simplified)
        # This is a basic conversion - real implementation would be more sophisticated
        lb, rb = self._convert_regex_to_boundaries(regex)

        # Escape the boundaries properly
        lb_escaped = self.formatter.escape_c_string(lb)
        rb_escaped = self.formatter.escape_c_string(rb)

        # Convert match_no: -1 = last, 0 or 1 = first, >1 = specific instance
        if match_no == '-1':
            ordinal = 'Last'
            ordinal_kr = '마지막'
        elif match_no == '0':
            ordinal = 'All'
            ordinal_kr = '전체'
        else:
            ordinal = match_no
            ordinal_kr = f'{match_no}번째'

        # Use consistent indentation with spaces (4 spaces for level 1)
        indent = "    "  # 4 spaces

        lines = []
        # Add comments if enabled
        if self.include_comments:
            lines.append(indent + "// ========================================")
            lines.append(indent + f"// 상관관계(Correlation): {refname}")
            lines.append(indent + f"// 좌측 경계(LB): {lb[:40]}{'...' if len(lb) > 40 else ''}")
            lines.append(indent + f"// 우측 경계(RB): {rb[:40]}{'...' if len(rb) > 40 else ''}")
            lines.append(indent + f"// 추출 순서: {ordinal_kr} 값")
            lines.append(indent + "// 주의: 이 함수는 HTTP 요청 전에 위치해야 합니다")
            lines.append(indent + "// ========================================")
            lines.append(indent + f'{LR_FUNCTIONS["WEB_REG_SAVE_PARAM"]}("{refname}",  // 저장할 파라미터 이름 (추후 lr_eval_string으로 사용)')
            lines.append(indent + f'    "LB={lb_escaped}",  // Left Boundary: 추출할 값의 왼쪽 경계 문자열')
            lines.append(indent + f'    "RB={rb_escaped}",  // Right Boundary: 추출할 값의 오른쪽 경계 문자열')
            lines.append(indent + f'    "Ord={ordinal}",  // Ordinal: 추출 순서 (1=첫번째, Last=마지막, All=전체)')
            lines.append(indent + f'    "Search=Body",  // 검색 대상: Body(응답본문), Headers(응답헤더), All(전체)')
            lines.append(indent + f'    "RelFrameID=All",  // 프레임 ID: All(모든 프레임), 또는 특정 프레임 번호')
            lines.append(indent + f'    LAST );  // 파라미터 목록 끝 (필수)')
        else:
            lines.append(indent + f'{LR_FUNCTIONS["WEB_REG_SAVE_PARAM"]}("{refname}", ')
            lines.append(indent + f'    "LB={lb_escaped}", ')
            lines.append(indent + f'    "RB={rb_escaped}", ')
            lines.append(indent + f'    "Ord={ordinal}", ')
            lines.append(indent + f'    "Search=Body", ')
            lines.append(indent + f'    "RelFrameID=All", ')
            lines.append(indent + f'    LAST );')

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
        lines.append(self._indent(f'{LR_FUNCTIONS["WEB_REG_SAVE_PARAM_JSON"]}(', level=1))
        lines.append(self._indent(f'"ParamName={refname}", ', level=2))
        lines.append(self._indent(f'"QueryString={jsonpath}", ', level=2))
        lines.append(self._indent('LAST );', level=2))

        return "\n".join(lines)

    def _generate_think_time(self, timer: Dict[str, Any]) -> str:
        """
        Generate lr_think_time call with optional Korean comments

        Args:
            timer: Timer data

        Returns:
            lr_think_time function call with optional Korean comments
        """
        delay = timer.get('delay', '0')

        # Convert milliseconds to seconds (JMeter uses ms, LR uses seconds)
        try:
            delay_seconds = float(delay) / 1000.0
            delay_ms = int(float(delay))
            if self.include_comments:
                comment = self._indent(f'// Think Time: {delay_ms}ms = {delay_seconds:.1f}초 대기', level=1)
                think_time = self._indent(f'{LR_FUNCTIONS["LR_THINK_TIME"]}({delay_seconds:.1f});', level=1)
                return f"{comment}\n{think_time}"
            else:
                think_time = self._indent(f'{LR_FUNCTIONS["LR_THINK_TIME"]}({delay_seconds:.1f});', level=1)
                return think_time
        except ValueError:
            if self.include_comments:
                comment = self._indent('// Think Time: 기본 1초 대기', level=1)
                think_time = self._indent(f'{LR_FUNCTIONS["LR_THINK_TIME"]}(1);', level=1)
                return f"{comment}\n{think_time}"
            else:
                think_time = self._indent(f'{LR_FUNCTIONS["LR_THINK_TIME"]}(1);', level=1)
                return think_time

    def _generate_transaction_start(self, name: str) -> str:
        """
        Generate lr_start_transaction call with optional Korean comments

        Args:
            name: Transaction name

        Returns:
            lr_start_transaction function call with optional Korean comments
        """
        escaped_name = self.formatter.escape_c_string(name)
        if self.include_comments:
            comment = self._indent(f'// ======================================== 트랜잭션 시작: {name} ========================================', level=1)
            trans_start = self._indent(f'{LR_FUNCTIONS["LR_START_TRANSACTION"]}("{escaped_name}");  // 응답시간 측정 시작', level=1)
            return f"{comment}\n{trans_start}"
        else:
            trans_start = self._indent(f'{LR_FUNCTIONS["LR_START_TRANSACTION"]}("{escaped_name}");', level=1)
            return trans_start

    def _generate_transaction_end(self, name: str) -> str:
        """
        Generate lr_end_transaction call with optional Korean comments

        Args:
            name: Transaction name

        Returns:
            lr_end_transaction function call with optional Korean comments
        """
        escaped_name = self.formatter.escape_c_string(name)
        if self.include_comments:
            comment = self._indent(f'// ======================================== 트랜잭션 종료: {name} ========================================', level=1)
            trans_end = self._indent(f'{LR_FUNCTIONS["LR_END_TRANSACTION"]}("{escaped_name}", LR_AUTO);  // LR_AUTO: 성공/실패 자동 판단', level=1)
            return f"{comment}\n{trans_end}"
        else:
            trans_end = self._indent(f'{LR_FUNCTIONS["LR_END_TRANSACTION"]}("{escaped_name}", LR_AUTO);', level=1)
            return trans_end

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

        Supports common regex capture group patterns:
        - (.+?) - non-greedy any character
        - (.*) - greedy any character
        - ([^X]+) - any character except X

        Args:
            regex: Regular expression

        Returns:
            Tuple of (left_boundary, right_boundary)
        """
        import re as regex_module

        # Pattern to find capture groups: (...)
        capture_pattern = r'\(([^)]+)\)'
        match = regex_module.search(capture_pattern, regex)

        if match:
            # Found a capture group
            capture_group = match.group(0)  # Full match with parentheses
            start_pos = match.start()
            end_pos = match.end()

            # Extract left boundary (everything before capture group)
            lb = regex[:start_pos]

            # Extract right boundary (everything after capture group)
            rb = regex[end_pos:]

            return (lb, rb)
        else:
            # No capture group found, use entire regex as LB
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

        lines.append(self._indent(f'if ({c_condition})', level=1))
        lines.append(self._indent('{', level=1))

        for body_line in body_lines:
            lines.append(self._indent(body_line, level=2))

        lines.append(self._indent('}', level=1))

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
        lines.append(self._indent(f'for (int i = 0; i < {loop_count}; i++)', level=1))
        lines.append(self._indent('{', level=1))

        for body_line in body_lines:
            lines.append(self._indent(body_line, level=2))

        lines.append(self._indent('}', level=1))

        return "\n".join(lines)

    def _generate_for_loop_start(self, loop_count: int) -> str:
        """
        Generate for loop opening

        Args:
            loop_count: Number of iterations

        Returns:
            For loop opening statement
        """
        indent = "    "  # 4 spaces
        return indent + f'for (int loop_i = 0; loop_i < {loop_count}; loop_i++)\n' + indent + '{'

    def _generate_for_loop_end(self) -> str:
        """
        Generate for loop closing

        Returns:
            For loop closing brace
        """
        indent = "    "  # 4 spaces
        return indent + '}'

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

        return self._indent(f'{LR_FUNCTIONS["LR_SAVE_STRING"]}("{escaped_value}", "{safe_name}");', level=1)

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
                lines.append(self._indent('// Assertion: Check response contains expected value', level=1))
                lines.append(self._indent('if (/* response check failed */)', level=1))
                lines.append(self._indent('{', level=1))
                lines.append(self._indent(f'{LR_FUNCTIONS["LR_ERROR_MESSAGE"]}("Assertion failed: Expected pattern not found - {escaped_pattern}");', level=2))
                lines.append(self._indent(f'{LR_FUNCTIONS["LR_ABORT"]}();', level=2))
                lines.append(self._indent('}', level=1))

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

    def _get_next_snapshot(self) -> str:
        """
        Generate next snapshot ID in LoadRunner format (t1.inf, t2.inf, etc.)

        Returns:
            Snapshot ID string
        """
        snapshot = f"t{self.snapshot_counter}.inf"
        self.snapshot_counter += 1
        return snapshot

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

        # LoadRunner uses tabs for indentation
        indent = '\t' * level
        return indent + text

    def _generate_globals_h(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate globals.h file with global declarations

        Args:
            parsed_data: Parsed test plan data

        Returns:
            globals.h file content
        """
        content = """#ifndef _GLOBALS_H
#define _GLOBALS_H

//--------------------------------------------------------------------
// Include Files
#include "lrun.h"
#include "web_api.h"
#include "lrw_custom_body.h"

//--------------------------------------------------------------------
// Global Variables

#endif // _GLOBALS_H
"""
        return content

    def _generate_vuser_init_file(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate vuser_init.c file

        Args:
            parsed_data: Parsed test plan data

        Returns:
            vuser_init.c file content
        """
        lines = []

        # Add include
        lines.append('#include "globals.h"')
        lines.append("")

        # Generate vuser_init function
        lines.append(self._generate_vuser_init(parsed_data))

        return "\n".join(lines)

    def _generate_action_file(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate Action.c file

        Args:
            parsed_data: Parsed test plan data

        Returns:
            Action.c file content
        """
        lines = []

        # Add include
        lines.append('#include "globals.h"')
        lines.append("")

        # Generate Action function
        lines.append(self._generate_action(parsed_data))

        return "\n".join(lines)

    def _generate_vuser_end_file(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate vuser_end.c file

        Args:
            parsed_data: Parsed test plan data

        Returns:
            vuser_end.c file content
        """
        lines = []

        # Add include
        lines.append('#include "globals.h"')
        lines.append("")

        # Generate vuser_end function
        lines.append(self._generate_vuser_end(parsed_data))

        return "\n".join(lines)
