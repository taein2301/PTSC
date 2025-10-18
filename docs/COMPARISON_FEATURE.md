# Script Comparison Feature

## Overview

The Script Comparison feature allows users to compare two scripts side-by-side and visualize the differences with color-coded highlighting. This is particularly useful for:

- Verifying conversion accuracy
- Understanding what changed during conversion
- Reviewing differences between original and converted scripts
- Identifying potential issues in converted code

## Features

### 1. Side-by-Side Comparison
- View original and converted scripts in parallel columns
- Line numbers for easy reference
- Synchronized scrolling (when possible)

### 2. Color-Coded Highlighting
- **Gray background**: Unchanged lines
- **Green background**: Added lines
- **Red background**: Removed lines
- **Yellow background**: Modified lines

### 3. Statistics Dashboard
- **Similarity ratio**: Overall similarity percentage between scripts
- **Lines added**: Number of new lines in converted script
- **Lines removed**: Number of lines removed from original
- **Lines modified**: Number of lines that changed

### 4. Filtering Options
- Toggle "Show unchanged lines" to focus only on differences
- Reduces clutter when reviewing large scripts

### 5. Export Options
- Download unified diff format (.patch file)
- Compatible with standard diff tools
- Can be applied using `patch` command

## How to Use

### Method 1: Upload Files Directly

1. Navigate to the "Compare Scripts" tab
2. Upload the original script in the left column
3. Upload the converted script in the right column
4. Click "Compare" button
5. Review the side-by-side comparison and statistics

### Method 2: Use Conversion Results

1. First, perform a conversion in JMeter → LoadRunner or LoadRunner → JMeter tab
2. Navigate to the "Compare Scripts" tab
3. Click "Use JMeter Conversion Result" or "Use LoadRunner Conversion Result"
4. Upload or select the other file to compare
5. Click "Compare" button

### Method 3: Compare Any Two Scripts

You can compare any two scripts, not just conversion results:
- Compare different versions of the same script
- Compare manually edited scripts with originals
- Compare scripts from different sources

## Understanding the Output

### Similarity Ratio
- **90-100%**: Excellent match, minimal differences
- **70-89%**: Good match, some differences
- **50-69%**: Moderate differences
- **Below 50%**: Significant differences

### Diff View Interpretation

**Example:**
```
Original (Left)          | Converted (Right)
-------------------------|-------------------------
1  web_url("GET",        | 1  web_url("GET",
2      "URL=http://...", | 2      "URL=http://...",
3      LAST);            | 3      "Mode=HTML",
                         | 4      LAST);
```

In this example:
- Lines 1-2 are unchanged (gray)
- Line 3 (left) was modified → Line 3-4 (right) (yellow)

## API Usage

You can also use the comparison functionality programmatically:

```python
from utils.comparator import ScriptComparator, compare_scripts

# Method 1: Using the class
comparator = ScriptComparator()
diff_lines, stats = comparator.compare(
    content_left="original script",
    content_right="converted script",
    label_left="Original",
    label_right="Converted"
)

print(f"Similarity: {stats.similarity_ratio:.1%}")
print(f"Lines added: {stats.lines_added}")
print(f"Lines removed: {stats.lines_removed}")
print(f"Lines modified: {stats.lines_modified}")

# Method 2: Using the convenience function
diff_lines, stats = compare_scripts("original", "converted")

# Generate unified diff
unified_diff = comparator.generate_unified_diff(
    content_left="original script",
    content_right="converted script"
)
print(unified_diff)

# Filter diff lines
filtered = comparator.filter_diff_lines(
    diff_lines,
    show_unchanged=False  # Show only changes
)
```

## Technical Details

### Algorithm
The comparison uses Python's `difflib.SequenceMatcher` which implements the Ratcliff/Obershelp algorithm:
- Compares sequences of lines
- Identifies matching blocks
- Classifies changes as add/remove/modify/unchanged

### Performance
- Optimized for scripts up to 10,000 lines
- Display limited to 500 lines in UI for performance
- Full diff available in download for larger scripts

### Limitations
- Character-level diff highlighting is available via API but not shown in UI
- Very large files (>10MB) may be slow to process
- Complex multi-line changes may be shown as multiple single-line changes

## Best Practices

1. **Start with small samples**: Test conversion with small scripts first
2. **Review statistics**: Check similarity ratio before diving into details
3. **Use filters**: Toggle "Show unchanged lines" off to focus on differences
4. **Download diffs**: Save unified diff for documentation or review
5. **Manual verification**: Always manually verify critical changes

## Troubleshooting

### Problem: Comparison is slow
**Solution**:
- Reduce file size
- Filter out unchanged lines
- Download diff instead of viewing in browser

### Problem: Too many differences shown
**Solution**:
- Verify you're comparing related scripts
- Check if file encodings are consistent
- Review conversion settings

### Problem: Can't see all differences
**Solution**:
- Scroll through the side-by-side view
- Download unified diff for complete view
- Use "Show unchanged lines" toggle

## Related Features

- [JMeter to LoadRunner Conversion](../CLAUDE.md#jmeter--loadrunner)
- [LoadRunner to JMeter Conversion](../CLAUDE.md#loadrunner--jmeter)
- [File Validation](../CLAUDE.md#error-handling)

## Future Enhancements

Planned improvements for future versions:
- [ ] Inline character-level diff highlighting in UI
- [ ] Jump to next/previous difference
- [ ] Search within diff view
- [ ] Syntax highlighting for code
- [ ] Export to HTML format
- [ ] Three-way merge view
- [ ] Diff statistics by file section

## Feedback

If you encounter issues or have suggestions for the comparison feature, please:
1. Check the troubleshooting section
2. Review the documentation
3. Report issues on GitHub: https://github.com/taein2301/PTSC/issues
