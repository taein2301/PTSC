"""
Debug LRParser to see what it extracts
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from parsers.lr_parser import LRParser

c_file = "samples/04_with_correlation.c"

with open(c_file, 'r', encoding='utf-8') as f:
    c_content = f.read()

parser = LRParser()
result = parser.parse(c_content)

# Extract Action function to see what was extracted
parser2 = LRParser()
parser2.script_content = c_content
parser2.lines = c_content.split('\n')
action_code = parser2._extract_function('Action')

print("=" * 80)
print("Extracted Action() Function Body:")
print("=" * 80)
print(action_code)
print("=" * 80)
print(f"\nLength: {len(action_code)} characters")

# Parse HTTP requests
http_requests = parser2._parse_http_requests(action_code)
print(f"\nFound {len(http_requests)} HTTP requests")
for i, req in enumerate(http_requests):
    print(f"  {i+1}. {req.get('type')}: {req.get('name')}")

# Parse correlations
correlations = parser2._parse_correlations(action_code)
print(f"\nFound {len(correlations)} correlations")
for i, corr in enumerate(correlations):
    print(f"  {i+1}. {corr.get('refname')}: LB={corr.get('lb', 'N/A')}, RB={corr.get('rb', 'N/A')}")

# Show parsed result
print("\n" + "=" * 80)
print("Full Parse Result:")
print("=" * 80)
print(f"Success: {result.get('success')}")
print(f"Variables: {len(result.get('data', {}).get('variables', {}))}")
print(f"HTTP Requests: {len(result.get('data', {}).get('http_requests', []))}")
print(f"Transactions: {len(result.get('data', {}).get('transactions', []))}")
print(f"Correlations: {len(result.get('data', {}).get('correlations', []))}")
