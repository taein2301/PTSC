"""
Test cases for script comparison functionality
"""

import unittest
from utils.comparator import ScriptComparator, ChangeType, compare_scripts


class TestScriptComparator(unittest.TestCase):
    """Test cases for ScriptComparator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.comparator = ScriptComparator()

    def test_identical_scripts(self):
        """Test comparison of identical scripts"""
        content = "line1\nline2\nline3"
        diff_lines, stats = self.comparator.compare(content, content)

        self.assertEqual(stats.similarity_ratio, 1.0)
        self.assertEqual(stats.lines_added, 0)
        self.assertEqual(stats.lines_removed, 0)
        self.assertEqual(stats.lines_modified, 0)
        self.assertEqual(stats.lines_unchanged, 3)

    def test_completely_different_scripts(self):
        """Test comparison of completely different scripts"""
        content1 = "line1\nline2\nline3"
        content2 = "lineA\nlineB\nlineC"
        diff_lines, stats = self.comparator.compare(content1, content2)

        self.assertLess(stats.similarity_ratio, 1.0)
        self.assertEqual(stats.lines_modified, 3)

    def test_added_lines(self):
        """Test detection of added lines"""
        content1 = "line1\nline2"
        content2 = "line1\nline2\nline3"
        diff_lines, stats = self.comparator.compare(content1, content2)

        self.assertEqual(stats.lines_added, 1)
        self.assertEqual(stats.lines_unchanged, 2)

    def test_removed_lines(self):
        """Test detection of removed lines"""
        content1 = "line1\nline2\nline3"
        content2 = "line1\nline2"
        diff_lines, stats = self.comparator.compare(content1, content2)

        self.assertEqual(stats.lines_removed, 1)
        self.assertEqual(stats.lines_unchanged, 2)

    def test_modified_lines(self):
        """Test detection of modified lines"""
        content1 = "line1\nline2\nline3"
        content2 = "line1\nmodified\nline3"
        diff_lines, stats = self.comparator.compare(content1, content2)

        self.assertEqual(stats.lines_modified, 1)
        self.assertEqual(stats.lines_unchanged, 2)

    def test_calculate_similarity(self):
        """Test similarity calculation"""
        content1 = "hello world"
        content2 = "hello world"
        ratio = self.comparator.calculate_similarity(content1, content2)
        self.assertEqual(ratio, 1.0)

        content1 = "hello"
        content2 = "world"
        ratio = self.comparator.calculate_similarity(content1, content2)
        self.assertLess(ratio, 1.0)

    def test_unified_diff_generation(self):
        """Test unified diff generation"""
        content1 = "line1\nline2\nline3"
        content2 = "line1\nmodified\nline3"
        diff = self.comparator.generate_unified_diff(content1, content2)

        self.assertIn("-line2", diff)
        self.assertIn("+modified", diff)

    def test_filter_diff_lines(self):
        """Test filtering diff lines"""
        content1 = "line1\nline2\nline3"
        content2 = "line1\nmodified\nline3"
        diff_lines, stats = self.comparator.compare(content1, content2)

        # Filter out unchanged lines
        filtered = self.comparator.filter_diff_lines(diff_lines, show_unchanged=False)
        self.assertLess(len(filtered), len(diff_lines))

        # All lines with show_unchanged=True
        filtered = self.comparator.filter_diff_lines(diff_lines, show_unchanged=True)
        self.assertEqual(len(filtered), len(diff_lines))

    def test_get_change_summary(self):
        """Test change summary generation"""
        content1 = "line1\nline2\nline3"
        content2 = "line1\nmodified\nline3\nline4"
        diff_lines, stats = self.comparator.compare(content1, content2)

        summary = self.comparator.get_change_summary(diff_lines)
        self.assertIn('added', summary)
        self.assertIn('removed', summary)
        self.assertIn('modified', summary)
        self.assertIn('unchanged', summary)

    def test_empty_content(self):
        """Test comparison with empty content"""
        diff_lines, stats = self.comparator.compare("", "")
        self.assertEqual(stats.similarity_ratio, 1.0)
        self.assertEqual(len(diff_lines), 0)

        diff_lines, stats = self.comparator.compare("line1", "")
        self.assertEqual(stats.lines_removed, 1)

        diff_lines, stats = self.comparator.compare("", "line1")
        self.assertEqual(stats.lines_added, 1)

    def test_highlight_character_diff(self):
        """Test character-level diff highlighting"""
        text1 = "hello"
        text2 = "hallo"
        h1, h2 = self.comparator.highlight_character_diff(text1, text2)

        self.assertIn("<mark>", h1)
        self.assertIn("<mark>", h2)

    def test_comparison_stats_to_dict(self):
        """Test conversion of stats to dictionary"""
        content1 = "line1\nline2"
        content2 = "line1\nmodified"
        diff_lines, stats = self.comparator.compare(content1, content2)

        stats_dict = stats.to_dict()
        self.assertIn('total_lines_left', stats_dict)
        self.assertIn('total_lines_right', stats_dict)
        self.assertIn('similarity_ratio', stats_dict)

    def test_comparison_stats_summary(self):
        """Test stats summary generation"""
        content1 = "line1\nline2"
        content2 = "line1\nmodified"
        diff_lines, stats = self.comparator.compare(content1, content2)

        summary = stats.get_summary()
        self.assertIn("Similarity", summary)
        self.assertIn("Lines added", summary)


class TestCompareScriptsFunction(unittest.TestCase):
    """Test cases for compare_scripts convenience function"""

    def test_compare_scripts_function(self):
        """Test the compare_scripts convenience function"""
        content1 = "line1\nline2\nline3"
        content2 = "line1\nmodified\nline3"

        diff_lines, stats = compare_scripts(content1, content2)

        self.assertIsNotNone(diff_lines)
        self.assertIsNotNone(stats)
        self.assertEqual(stats.lines_modified, 1)


if __name__ == '__main__':
    unittest.main()
