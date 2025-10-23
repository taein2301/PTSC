"""Test AI prompt loading functionality"""
from utils.ai_helper import GeminiHelper


def test_prompt_loading():
    """Test that prompts are loaded from file"""
    helper = GeminiHelper()

    print("Testing prompt loading...")
    print(f"Prompts loaded: {len(helper.prompts)}")
    print(f"Available prompts: {list(helper.prompts.keys())}")

    if 'conversion_analysis' in helper.prompts:
        print("\n[OK] conversion_analysis prompt loaded")
        print(f"Length: {len(helper.prompts['conversion_analysis'])} chars")
        print(f"Preview: {helper.prompts['conversion_analysis'][:100]}...")
    else:
        print("\n[FAIL] conversion_analysis prompt NOT loaded")

    if 'conversion_tips' in helper.prompts:
        print("\n[OK] conversion_tips prompt loaded")
        print(f"Length: {len(helper.prompts['conversion_tips'])} chars")
        print(f"Preview: {helper.prompts['conversion_tips'][:100]}...")
    else:
        print("\n[FAIL] conversion_tips prompt NOT loaded")

    # Test format string variables
    if 'conversion_analysis' in helper.prompts:
        print("\n\nTesting conversion_analysis format variables...")
        try:
            test_prompt = helper.prompts['conversion_analysis'].format(
                source_type='JMeter',
                target_type='LoadRunner',
                total=10,
                converted=8,
                skipped=2,
                accuracy=80.0,
                warning_count=1,
                warnings='- Test warning',
                error_count=0,
                errors='',
                content_preview='Sample code...'
            )
            print("[OK] Format test passed")
            print(f"Formatted prompt length: {len(test_prompt)} chars")
        except Exception as e:
            print(f"[FAIL] Format test failed: {e}")

    if 'conversion_tips' in helper.prompts:
        print("\n\nTesting conversion_tips format variables...")
        try:
            test_prompt = helper.prompts['conversion_tips'].format(
                source_type='JMeter',
                target_type='LoadRunner'
            )
            print("[OK] Format test passed")
            print(f"Formatted prompt length: {len(test_prompt)} chars")
        except Exception as e:
            print(f"[FAIL] Format test failed: {e}")


if __name__ == '__main__':
    test_prompt_loading()
