#!/usr/bin/env python
"""
Test conversion functionality
"""

from converters.jmeter_to_lr import JMeterToLRConverter

# Test with test_loop.jmx
print("=" * 80)
print("Testing JMeter to LoadRunner conversion")
print("=" * 80)

converter = JMeterToLRConverter()

# Test file 1
print("\n1. Testing test_loop.jmx...")
try:
    with open('test_loop.jmx', 'r', encoding='utf-8') as f:
        jmx_content = f.read()

    success, result_data, log_msg = converter.execute_conversion(jmx_content)

    if success:
        print("[OK] Conversion successful!")
        print(f"   Log: {str(log_msg)[:200]}")

        # Save output
        with open('test_loop_output.c', 'w', encoding='utf-8') as f:
            f.write(result_data)
        print("   Output saved to: test_loop_output.c")

        # Show first 30 lines
        lines = result_data.split('\n')
        print(f"\n   First 30 lines of output:")
        print("   " + "-" * 76)
        for i, line in enumerate(lines[:30], 1):
            print(f"   {i:3d} | {line}")
    else:
        print("[FAIL] Conversion failed!")
        print(f"   Log: {log_msg}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
