"""
Test script to verify correlation conversion functionality
"""

import sys
import io

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from converters.jmeter_to_lr import JMeterToLRConverter
from converters.lr_to_jmeter import LRToJMeterConverter

def test_jmeter_to_lr_correlation():
    """Test JMeter RegexExtractor to LoadRunner web_reg_save_param"""
    print("=" * 80)
    print("TEST 1: JMeter RegexExtractor → LoadRunner web_reg_save_param")
    print("=" * 80)

    jmx_file = "samples/04_with_regex_extractor.jmx"

    with open(jmx_file, 'r', encoding='utf-8') as f:
        jmx_content = f.read()

    converter = JMeterToLRConverter(include_comments=True)
    success, output_content, stats = converter.execute_conversion(jmx_content)

    if success:
        print("✅ Conversion successful!")
        print("\n📊 Statistics:")
        print(f"   Total: {stats['stats']['items_total']}")
        print(f"   Converted: {stats['stats']['items_converted']}")
        print(f"   Skipped: {stats['stats']['items_skipped']}")

        print("\n📝 Generated LoadRunner Script:")
        print("-" * 80)
        print(output_content)
        print("-" * 80)

        # Check if web_reg_save_param is present
        if 'web_reg_save_param' in output_content:
            print("\n✅ web_reg_save_param found in output!")

            # Check if it appears before the request
            lines = output_content.split('\n')
            web_reg_line = -1
            web_url_line = -1

            for i, line in enumerate(lines):
                if 'web_reg_save_param' in line:
                    web_reg_line = i
                if 'web_url' in line and web_url_line == -1:
                    web_url_line = i

            if web_reg_line >= 0 and web_url_line >= 0:
                if web_reg_line < web_url_line:
                    print(f"✅ Correct placement: web_reg_save_param (line {web_reg_line}) before web_url (line {web_url_line})")
                else:
                    print(f"❌ Wrong placement: web_reg_save_param (line {web_reg_line}) after web_url (line {web_url_line})")
        else:
            print("\n❌ web_reg_save_param NOT found in output!")

        print("\n📋 Errors:")
        for error in stats.get('errors', []):
            print(f"   ❌ {error}")

        print("\n⚠️ Warnings:")
        for warning in stats.get('warnings', []):
            print(f"   ⚠️ {warning}")
    else:
        print("❌ Conversion failed!")
        for error in stats.get('errors', []):
            print(f"   {error}")

    return {'success': success, 'data': output_content, 'stats': stats}

def test_lr_to_jmeter_correlation():
    """Test LoadRunner web_reg_save_param to JMeter RegexExtractor"""
    print("\n\n")
    print("=" * 80)
    print("TEST 2: LoadRunner web_reg_save_param → JMeter RegexExtractor")
    print("=" * 80)

    c_file = "samples/04_with_correlation.c"

    with open(c_file, 'r', encoding='utf-8') as f:
        c_content = f.read()

    converter = LRToJMeterConverter()
    success, output_content, stats = converter.execute_conversion(c_content)

    if success:
        print("✅ Conversion successful!")
        print("\n📊 Statistics:")
        print(f"   Total: {stats['stats']['items_total']}")
        print(f"   Converted: {stats['stats']['items_converted']}")
        print(f"   Skipped: {stats['stats']['items_skipped']}")

        print("\n📝 Generated JMeter XML (first 2000 chars):")
        print("-" * 80)
        print(output_content[:2000])
        print("-" * 80)

        # Check if RegexExtractor is present
        if 'RegexExtractor' in output_content:
            print("\n✅ RegexExtractor found in output!")

            # Check for key elements
            if 'refname' in output_content:
                print("✅ refname property found")
            if 'regex' in output_content:
                print("✅ regex property found")
        else:
            print("\n❌ RegexExtractor NOT found in output!")

        print("\n📋 Errors:")
        for error in stats.get('errors', []):
            print(f"   ❌ {error}")

        print("\n⚠️ Warnings:")
        for warning in stats.get('warnings', []):
            print(f"   ⚠️ {warning}")
    else:
        print("❌ Conversion failed!")
        for error in stats.get('errors', []):
            print(f"   {error}")

    return {'success': success, 'data': output_content, 'stats': stats}

if __name__ == "__main__":
    # Test both directions
    jmeter_result = test_jmeter_to_lr_correlation()
    lr_result = test_lr_to_jmeter_correlation()

    print("\n\n")
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"JMeter → LoadRunner: {'✅ PASS' if jmeter_result['success'] else '❌ FAIL'}")
    print(f"LoadRunner → JMeter: {'✅ PASS' if lr_result['success'] else '❌ FAIL'}")
