"""
AI Helper for Gemini API integration

Provides AI-powered analysis of conversion results using Google Gemini API
"""

import os
import socket
import re
import google.generativeai as genai
from typing import Dict, Any, Optional
from pathlib import Path


class GeminiHelper:
    """Helper class for Gemini API integration"""

    def __init__(self):
        """Initialize Gemini API with API key from environment variable"""
        # Temporary hardcoded API key for testing
        self.api_key = os.getenv('GEMINI_API_KEY') or 'AIzaSyBh5TKyfQ2A81_M6rXCu5XE-O61DG0qiJs'
        self.model = None
        self.prompts = {}

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Use the latest Gemini model (best price-performance)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
                self.model = None

        # Load prompts from file
        self._load_prompts()

    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.model is not None

    def _load_prompts(self):
        """Load prompt templates from docs/ai_prompt.md"""
        try:
            # Find the project root directory
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent
            prompt_file = project_root / 'docs' / 'ai_prompt.md'

            if not prompt_file.exists():
                print(f"Warning: Prompt file not found: {prompt_file}")
                return

            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract prompts using regex
            # Match content between ``` blocks
            prompt_blocks = re.findall(r'```\n(.*?)\n```', content, re.DOTALL)

            if len(prompt_blocks) >= 2:
                self.prompts['conversion_analysis'] = prompt_blocks[0].strip()
                self.prompts['conversion_tips'] = prompt_blocks[1].strip()
            else:
                print(f"Warning: Could not parse prompts from {prompt_file}")

        except Exception as e:
            print(f"Error loading prompts: {e}")

    def _check_network_connection(self) -> bool:
        """
        Check if network connection is available

        Returns:
            True if network is available, False otherwise
        """
        try:
            # Try to connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def analyze_conversion(self,
                          source_type: str,
                          target_type: str,
                          stats: Dict[str, Any],
                          warnings: list,
                          errors: list,
                          converted_content: str = None) -> str:
        """
        Analyze conversion results and provide AI summary

        Args:
            source_type: Source format (e.g., 'JMeter', 'LoadRunner')
            target_type: Target format (e.g., 'LoadRunner', 'JMeter')
            stats: Conversion statistics dictionary
            warnings: List of warning messages
            errors: List of error messages
            converted_content: Optional converted script content (first 500 chars)

        Returns:
            AI-generated summary and recommendations
        """
        if not self.is_available():
            return "⚠️ Gemini API를 사용할 수 없습니다. GEMINI_API_KEY 환경 변수를 설정해주세요."

        # Check network connection first
        if not self._check_network_connection():
            return "⚠️ 네트워크 연결이 없습니다. AI 요약 기능을 사용할 수 없습니다."

        try:
            # Prepare conversion summary
            total = stats.get('items_total', 0)
            converted = stats.get('items_converted', 0)
            skipped = stats.get('items_skipped', 0)
            accuracy = stats.get('accuracy', 0)

            # Truncate converted content for context
            content_preview = ""
            if converted_content:
                content_preview = converted_content[:500] + "..." if len(converted_content) > 500 else converted_content

            # Get prompt template from file
            prompt_template = self.prompts.get('conversion_analysis', '')
            if not prompt_template:
                return "⚠️ AI 프롬프트를 로드할 수 없습니다."

            # Format prompt with actual values
            warning_list = '\n'.join(['- ' + w for w in warnings[:5]])
            error_list = '\n'.join(['- ' + e for e in errors[:5]])

            prompt = prompt_template.format(
                source_type=source_type,
                target_type=target_type,
                total=total,
                converted=converted,
                skipped=skipped,
                accuracy=accuracy,
                warning_count=len(warnings),
                warnings=warning_list,
                error_count=len(errors),
                errors=error_list,
                content_preview=content_preview
            )

            # Call Gemini API
            response = self.model.generate_content(prompt)

            if response and response.text:
                return response.text.strip()
            else:
                return "AI 분석 결과를 생성할 수 없습니다."

        except Exception as e:
            return f"AI 분석 중 오류 발생: {str(e)}"

    def get_conversion_tips(self, source_type: str, target_type: str) -> str:
        """
        Get conversion tips and best practices

        Args:
            source_type: Source format
            target_type: Target format

        Returns:
            AI-generated tips
        """
        if not self.is_available():
            return ""

        # Check network connection first
        if not self._check_network_connection():
            return ""

        try:
            # Get prompt template from file
            prompt_template = self.prompts.get('conversion_tips', '')
            if not prompt_template:
                return ""

            # Format prompt with actual values
            prompt = prompt_template.format(
                source_type=source_type,
                target_type=target_type
            )

            response = self.model.generate_content(prompt)

            if response and response.text:
                return response.text.strip()
            else:
                return ""

        except Exception as e:
            return f"오류: {str(e)}"
