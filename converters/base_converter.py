"""
Base Converter Abstract Class

This module defines the abstract base class that all converters must implement.
It provides the standard interface for conversion operations.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any


class BaseConverter(ABC):
    """
    Abstract base class for all converters

    Defines the interface that JMeter→LoadRunner and LoadRunner→JMeter
    converters must implement.
    """

    def __init__(self):
        """Initialize the base converter"""
        self.errors = []
        self.warnings = []
        self.conversion_stats = {
            'items_total': 0,
            'items_converted': 0,
            'items_skipped': 0,
            'items_partial': 0
        }

    @abstractmethod
    def validate_input(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the input content before conversion

        Args:
            content: The input file content as string

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if content is valid for conversion
            - error_message: Description of validation error if invalid, None otherwise
        """
        pass

    @abstractmethod
    def convert(self, content: str) -> Dict[str, Any]:
        """
        Perform the actual conversion

        Args:
            content: The input file content as string

        Returns:
            Dictionary containing:
            - 'success': bool indicating if conversion succeeded
            - 'data': parsed/converted data structure
            - 'errors': list of error messages
            - 'warnings': list of warning messages
        """
        pass

    @abstractmethod
    def generate_output(self, converted_data: Dict[str, Any]) -> str:
        """
        Generate the output file content from converted data

        Args:
            converted_data: The converted data structure from convert()

        Returns:
            The output file content as string
        """
        pass

    def execute_conversion(self, content: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Execute the complete conversion pipeline

        This is the main entry point that orchestrates the conversion process:
        1. Validate input
        2. Perform conversion
        3. Generate output

        Args:
            content: The input file content as string

        Returns:
            Tuple of (success, output_content, stats)
            - success: True if conversion succeeded
            - output_content: Generated output file content, None if failed
            - stats: Dictionary with conversion statistics and messages
        """
        # Reset state
        self.errors = []
        self.warnings = []
        self.conversion_stats = {
            'items_total': 0,
            'items_converted': 0,
            'items_skipped': 0,
            'items_partial': 0
        }

        # Step 1: Validate input
        is_valid, error_msg = self.validate_input(content)
        if not is_valid:
            self.errors.append(f"Validation failed: {error_msg}")
            return False, None, self._get_conversion_stats()

        # Step 2: Perform conversion
        try:
            conversion_result = self.convert(content)

            if not conversion_result.get('success', False):
                self.errors.extend(conversion_result.get('errors', []))
                return False, None, self._get_conversion_stats()

            # Collect warnings
            self.warnings.extend(conversion_result.get('warnings', []))

            # Step 3: Generate output
            try:
                output_content = self.generate_output(conversion_result.get('data', {}))
                return True, output_content, self._get_conversion_stats()
            except Exception as gen_error:
                # Generation error - errors already added by generate_output
                self.errors.append(f"Generation failed: {str(gen_error)}")
                return False, None, self._get_conversion_stats()

        except Exception as e:
            self.errors.append(f"Conversion error: {str(e)}")
            return False, None, self._get_conversion_stats()

    def _get_conversion_stats(self) -> Dict[str, Any]:
        """
        Get conversion statistics and messages

        Returns:
            Dictionary with stats, errors, and warnings
        """
        total = self.conversion_stats['items_converted'] + self.conversion_stats['items_skipped']
        accuracy = (self.conversion_stats['items_converted'] / total * 100) if total > 0 else 0

        return {
            'stats': self.conversion_stats,
            'accuracy': accuracy,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def add_error(self, message: str) -> None:
        """
        Add an error message

        Args:
            message: Error message to add
        """
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """
        Add a warning message

        Args:
            message: Warning message to add
        """
        self.warnings.append(message)

    def increment_stat(self, stat_name: str, increment: int = 1) -> None:
        """
        Increment a conversion statistic

        Args:
            stat_name: Name of the stat to increment
            increment: Amount to increment by (default 1)
        """
        if stat_name in self.conversion_stats:
            self.conversion_stats[stat_name] += increment
