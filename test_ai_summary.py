"""
Test AI Summary feature
"""

import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set fake API key for testing
os.environ['GEMINI_API_KEY'] = 'test_key'

from utils.ai_helper import GeminiHelper

# Test initialization
helper = GeminiHelper()

print("=" * 80)
print("Gemini Helper Test")
print("=" * 80)
print(f"API Available: {helper.is_available()}")
print(f"API Key set: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
print(f"Model initialized: {'Yes' if helper.model else 'No'}")
print("=" * 80)

# Test conversion analysis (will fail without real API key)
if helper.is_available():
    print("\nTesting analyze_conversion()...")

    stats = {
        'items_total': 5,
        'items_converted': 5,
        'items_skipped': 0,
        'accuracy': 100.0
    }

    warnings = [
        'Thread count should be configured in Runtime Settings',
        'Ramp-up time should be configured in Runtime Settings'
    ]

    errors = []

    result = helper.analyze_conversion(
        source_type='JMeter',
        target_type='LoadRunner',
        stats=stats,
        warnings=warnings,
        errors=errors,
        converted_content='web_url("test", "URL=http://example.com", LAST);'
    )

    print("\n📝 AI Summary:")
    print("-" * 80)
    print(result)
    print("-" * 80)
else:
    print("\n⚠️ Gemini API not available")
    print("Set GEMINI_API_KEY environment variable to enable AI features")
