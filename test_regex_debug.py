"""
Debug script to check RegexExtractor parsing
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from parsers.jmx_parser import JMXParser

jmx_file = "samples/04_with_regex_extractor.jmx"

parser = JMXParser(jmx_file)
success, test_plan = parser.parse()

if success:
    print("✅ Parsing successful!")
    print("\n📊 Test Plan Structure:")
    print(f"Name: {test_plan['test_plan']['name']}")
    print(f"Thread Groups: {len(test_plan['thread_groups'])}")

    for i, tg in enumerate(test_plan['thread_groups']):
        print(f"\n📁 Thread Group {i+1}: {tg['name']}")
        print(f"   Samplers: {len(tg.get('samplers', []))}")
        print(f"   Extractors: {len(tg.get('extractors', []))}")
        print(f"   Headers: {len(tg.get('headers', []))}")
        print(f"   Timers: {len(tg.get('timers', []))}")

        print("\n   📝 Samplers:")
        for sampler in tg.get('samplers', []):
            print(f"      - {sampler.get('name', 'Unknown')} ({sampler.get('method', 'GET')})")

        print("\n   🔗 Extractors:")
        for extractor in tg.get('extractors', []):
            print(f"      - {extractor.get('refname', 'Unknown')}: {extractor.get('regex', 'N/A')}")

    print("\n   📄 Elements (top-level):")
    for elem in test_plan.get('elements', []):
        print(f"      - {elem.get('type', 'Unknown')}: {elem.get('name', 'N/A')}")
else:
    print("❌ Parsing failed!")
    print(parser.errors)
