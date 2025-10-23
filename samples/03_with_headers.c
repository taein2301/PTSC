/*
 * LoadRunner Sample Script: Request with Custom Headers
 * Generated for testing purposes
 */

#include "web_api.h"

Action()
{
	// Add custom headers
	web_add_header("Content-Type", "application/json");
	web_add_header("Authorization", "Bearer token123");
	web_add_header("X-Custom-Header", "CustomValue");

	// GET request with headers
	web_url("api_request",
		"URL=http://api.example.com/data",
		"Resource=0",
		"RecContentType=application/json",
		"Referer=",
		"Snapshot=t3.inf",
		"Mode=HTML",
		LAST);

	return 0;
}
