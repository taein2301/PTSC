"""
Script Comparison Utility

This module provides functionality for comparing scripts side-by-side:
- Line-by-line comparison
- Diff generation with highlighting
- Similarity analysis
- Change statistics
"""

from typing import List, Tuple, Dict, Optional
from difflib import SequenceMatcher, unified_diff
from enum import Enum


class ChangeType(Enum):
    """Type of change in diff"""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class DiffLine:
    """Represents a single line in the diff view"""

    def __init__(self, line_num_left: Optional[int], line_num_right: Optional[int],
                 content_left: str, content_right: str, change_type: ChangeType):
        """
        Initialize a diff line.

        Args:
            line_num_left: Line number in left file (None if added)
            line_num_right: Line number in right file (None if removed)
            content_left: Content of left line
            content_right: Content of right line
            change_type: Type of change
        """
        self.line_num_left = line_num_left
        self.line_num_right = line_num_right
        self.content_left = content_left
        self.content_right = content_right
        self.change_type = change_type


class ComparisonStats:
    """Statistics about the comparison"""

    def __init__(self):
        """Initialize comparison statistics"""
        self.total_lines_left = 0
        self.total_lines_right = 0
        self.lines_added = 0
        self.lines_removed = 0
        self.lines_modified = 0
        self.lines_unchanged = 0
        self.similarity_ratio = 0.0

    def to_dict(self) -> Dict:
        """Convert stats to dictionary"""
        return {
            'total_lines_left': self.total_lines_left,
            'total_lines_right': self.total_lines_right,
            'lines_added': self.lines_added,
            'lines_removed': self.lines_removed,
            'lines_modified': self.lines_modified,
            'lines_unchanged': self.lines_unchanged,
            'similarity_ratio': self.similarity_ratio,
        }

    def get_summary(self) -> str:
        """Get a human-readable summary"""
        lines = [
            "Comparison Statistics:",
            f"  Similarity: {self.similarity_ratio:.1%}",
            f"  Total lines (Original): {self.total_lines_left}",
            f"  Total lines (Converted): {self.total_lines_right}",
            f"  Lines added: {self.lines_added}",
            f"  Lines removed: {self.lines_removed}",
            f"  Lines modified: {self.lines_modified}",
            f"  Lines unchanged: {self.lines_unchanged}",
        ]
        return "\n".join(lines)


class ScriptComparator:
    """
    Script comparator class for comparing two scripts side-by-side.
    """

    def __init__(self):
        """Initialize the script comparator"""
        pass

    def compare(self, content_left: str, content_right: str,
                label_left: str = "Original", label_right: str = "Converted") -> Tuple[List[DiffLine], ComparisonStats]:
        """
        Compare two scripts and generate diff lines.

        Args:
            content_left: Content of the left (original) script
            content_right: Content of the right (converted) script
            label_left: Label for left side
            label_right: Label for right side

        Returns:
            Tuple of (list of diff lines, comparison statistics)

        Example:
            >>> comparator = ScriptComparator()
            >>> diff_lines, stats = comparator.compare("line1\\nline2", "line1\\nline3")
        """
        lines_left = content_left.split('\n') if content_left else []
        lines_right = content_right.split('\n') if content_right else []

        # Calculate similarity
        stats = ComparisonStats()
        stats.total_lines_left = len(lines_left)
        stats.total_lines_right = len(lines_right)
        stats.similarity_ratio = self.calculate_similarity(content_left, content_right)

        # Generate diff lines
        diff_lines = self._generate_diff_lines(lines_left, lines_right, stats)

        return diff_lines, stats

    def _generate_diff_lines(self, lines_left: List[str], lines_right: List[str],
                             stats: ComparisonStats) -> List[DiffLine]:
        """
        Generate diff lines from two lists of lines.

        Args:
            lines_left: Lines from left file
            lines_right: Lines from right file
            stats: Statistics object to update

        Returns:
            List of DiffLine objects
        """
        diff_lines: List[DiffLine] = []

        # Use SequenceMatcher to find matching blocks
        matcher = SequenceMatcher(None, lines_left, lines_right)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Lines are equal
                for i in range(i1, i2):
                    diff_lines.append(DiffLine(
                        i + 1, j1 + (i - i1) + 1,
                        lines_left[i], lines_right[j1 + (i - i1)],
                        ChangeType.UNCHANGED
                    ))
                    stats.lines_unchanged += 1

            elif tag == 'replace':
                # Lines are different (modified)
                # Show side by side
                max_lines = max(i2 - i1, j2 - j1)
                for k in range(max_lines):
                    left_idx = i1 + k if i1 + k < i2 else None
                    right_idx = j1 + k if j1 + k < j2 else None

                    left_content = lines_left[left_idx] if left_idx is not None else ""
                    right_content = lines_right[right_idx] if right_idx is not None else ""

                    left_line_num = left_idx + 1 if left_idx is not None else None
                    right_line_num = right_idx + 1 if right_idx is not None else None

                    if left_idx is not None and right_idx is not None:
                        change_type = ChangeType.MODIFIED
                        stats.lines_modified += 1
                    elif left_idx is not None:
                        change_type = ChangeType.REMOVED
                        stats.lines_removed += 1
                    else:
                        change_type = ChangeType.ADDED
                        stats.lines_added += 1

                    diff_lines.append(DiffLine(
                        left_line_num, right_line_num,
                        left_content, right_content,
                        change_type
                    ))

            elif tag == 'delete':
                # Lines removed from left
                for i in range(i1, i2):
                    diff_lines.append(DiffLine(
                        i + 1, None,
                        lines_left[i], "",
                        ChangeType.REMOVED
                    ))
                    stats.lines_removed += 1

            elif tag == 'insert':
                # Lines added to right
                for j in range(j1, j2):
                    diff_lines.append(DiffLine(
                        None, j + 1,
                        "", lines_right[j],
                        ChangeType.ADDED
                    ))
                    stats.lines_added += 1

        return diff_lines

    def calculate_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate similarity ratio between two texts.

        Args:
            content1: First text
            content2: Second text

        Returns:
            Similarity ratio (0.0 to 1.0)

        Example:
            >>> comparator = ScriptComparator()
            >>> ratio = comparator.calculate_similarity("hello", "hello world")
            >>> print(f"{ratio:.2%}")
        """
        matcher = SequenceMatcher(None, content1, content2)
        return matcher.ratio()

    def generate_unified_diff(self, content_left: str, content_right: str,
                              label_left: str = "Original", label_right: str = "Converted") -> str:
        """
        Generate a unified diff format output.

        Args:
            content_left: Content of the left (original) script
            content_right: Content of the right (converted) script
            label_left: Label for left side
            label_right: Label for right side

        Returns:
            Unified diff as string

        Example:
            >>> comparator = ScriptComparator()
            >>> diff = comparator.generate_unified_diff("line1\\nline2", "line1\\nline3")
        """
        lines_left = content_left.split('\n') if content_left else []
        lines_right = content_right.split('\n') if content_right else []

        diff = unified_diff(
            lines_left,
            lines_right,
            fromfile=label_left,
            tofile=label_right,
            lineterm=''
        )

        return '\n'.join(diff)

    def highlight_character_diff(self, text1: str, text2: str) -> Tuple[str, str]:
        """
        Highlight character-level differences between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Tuple of (highlighted text1, highlighted text2)
            Uses <mark> tags for highlighting

        Example:
            >>> comparator = ScriptComparator()
            >>> h1, h2 = comparator.highlight_character_diff("hello", "hallo")
        """
        if not text1 and not text2:
            return "", ""
        if not text1:
            return "", f"<mark>{text2}</mark>"
        if not text2:
            return f"<mark>{text1}</mark>", ""

        matcher = SequenceMatcher(None, text1, text2)

        result1_parts = []
        result2_parts = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                result1_parts.append(text1[i1:i2])
                result2_parts.append(text2[j1:j2])
            elif tag == 'replace':
                if i1 < i2:
                    result1_parts.append(f"<mark>{text1[i1:i2]}</mark>")
                if j1 < j2:
                    result2_parts.append(f"<mark>{text2[j1:j2]}</mark>")
            elif tag == 'delete':
                result1_parts.append(f"<mark>{text1[i1:i2]}</mark>")
            elif tag == 'insert':
                result2_parts.append(f"<mark>{text2[j1:j2]}</mark>")

        return ''.join(result1_parts), ''.join(result2_parts)

    def get_change_summary(self, diff_lines: List[DiffLine]) -> Dict[str, int]:
        """
        Get a summary of changes from diff lines.

        Args:
            diff_lines: List of DiffLine objects

        Returns:
            Dictionary with change counts

        Example:
            >>> comparator = ScriptComparator()
            >>> diff_lines, _ = comparator.compare("line1\\nline2", "line1\\nline3")
            >>> summary = comparator.get_change_summary(diff_lines)
        """
        summary = {
            'added': 0,
            'removed': 0,
            'modified': 0,
            'unchanged': 0
        }

        for line in diff_lines:
            if line.change_type == ChangeType.ADDED:
                summary['added'] += 1
            elif line.change_type == ChangeType.REMOVED:
                summary['removed'] += 1
            elif line.change_type == ChangeType.MODIFIED:
                summary['modified'] += 1
            elif line.change_type == ChangeType.UNCHANGED:
                summary['unchanged'] += 1

        return summary

    def filter_diff_lines(self, diff_lines: List[DiffLine],
                          show_unchanged: bool = True) -> List[DiffLine]:
        """
        Filter diff lines based on options.

        Args:
            diff_lines: List of DiffLine objects
            show_unchanged: Whether to include unchanged lines

        Returns:
            Filtered list of DiffLine objects

        Example:
            >>> comparator = ScriptComparator()
            >>> diff_lines, _ = comparator.compare("line1\\nline2", "line1\\nline3")
            >>> filtered = comparator.filter_diff_lines(diff_lines, show_unchanged=False)
        """
        if show_unchanged:
            return diff_lines

        return [line for line in diff_lines if line.change_type != ChangeType.UNCHANGED]


def compare_scripts(content_left: str, content_right: str) -> Tuple[List[DiffLine], ComparisonStats]:
    """
    Convenience function to compare two scripts.

    Args:
        content_left: Content of the left script
        content_right: Content of the right script

    Returns:
        Tuple of (list of diff lines, comparison statistics)

    Example:
        >>> from utils.comparator import compare_scripts
        >>> diff_lines, stats = compare_scripts("line1\\nline2", "line1\\nline3")
        >>> print(stats.get_summary())
    """
    comparator = ScriptComparator()
    return comparator.compare(content_left, content_right)
