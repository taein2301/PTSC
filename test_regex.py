import re

# Full Action code from parser
code = '''	// Register correlation to extract session token
	web_reg_save_param("SessionToken",
		"LB=<session>",
		"RB=</session>",
		"Ord=1",
		"Search=Body",
		LAST);

	// Initial request to get session
	web_url("get_session",
		"URL=http://example.com/session",
		"Resource=0",
		"RecContentType=application/json",
		"Referer=",
		"Snapshot=t4.inf",
		"Mode=HTML",
		LAST);

	// Use correlated value in subsequent request
	web_custom_request("use_session",
		"URL=http://example.com/api/data",
		"Method=GET",
		"Resource=0",
		"RecContentType=application/json",
		"Referer=",
		"Snapshot=t5.inf",
		"Mode=HTML",
		"Body={SessionToken}",
		LAST);

	return 0;'''

# Test the regex pattern
web_url_pattern = r'web_url\s*\((.*?)\s*LAST\s*\);'
matches = list(re.finditer(web_url_pattern, code, re.DOTALL))

print(f"Found {len(matches)} web_url matches")
for i, match in enumerate(matches):
    print(f"\nMatch {i+1}:")
    print(f"Full match (first 150 chars): {match.group(0)[:150]}...")

# Test web_custom_request
web_custom_pattern = r'web_custom_request\s*\((.*?)\s*LAST\s*\);'
custom_matches = list(re.finditer(web_custom_pattern, code, re.DOTALL))

print(f"\n\nFound {len(custom_matches)} web_custom_request matches")

# Test web_reg_save_param
web_reg_pattern = r'web_reg_save_param\s*\((.*?)\s*LAST\s*\);'
reg_matches = list(re.finditer(web_reg_pattern, code, re.DOTALL))

print(f"Found {len(reg_matches)} web_reg_save_param matches")
