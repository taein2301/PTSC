"""
Test JSON body conversion
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from converters.jmeter_to_lr import JMeterToLRConverter

jmx_file = "test_json_body.jmx"

with open(jmx_file, 'r', encoding='utf-8') as f:
    jmx_content = f.read()

converter = JMeterToLRConverter(include_comments=True)
success, output_content, stats = converter.execute_conversion(jmx_content)

if success:
    print("✅ Conversion successful!")
    print("\n" + "=" * 80)
    print("Generated LoadRunner Script:")
    print("=" * 80)
    print(output_content)
    print("=" * 80)

    # Check if web_custom_request is used (correct for JSON body)
    if 'web_custom_request' in output_content:
        print("\n✅ Correctly using web_custom_request for JSON body!")

        # Check if Body parameter is present
        if '"Body=' in output_content:
            print("✅ Body parameter found!")

            # Extract and show the body line
            lines = output_content.split('\n')
            for line in lines:
                if '"Body=' in line:
                    print(f"\n📝 Body line:\n{line}")
        else:
            print("❌ Body parameter NOT found!")
    elif 'web_submit_data' in output_content:
        print("\n❌ ERROR: Using web_submit_data for JSON body (should use web_custom_request)!")

    print("\n⚠️ Warnings:")
    for warning in stats.get('warnings', []):
        print(f"   {warning}")
else:
    print("❌ Conversion failed!")
    for error in stats.get('errors', []):
        print(f"   {error}")
