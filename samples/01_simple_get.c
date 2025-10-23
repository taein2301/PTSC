/*
 * LoadRunner Sample Script: Simple GET Request
 * Generated for testing purposes
 */

#include "web_api.h"

Action()
{
	// Simple GET request
	web_url("example_homepage",
		"URL=http://example.com/",
		"Resource=0",
		"RecContentType=text/html",
		"Referer=",
		"Snapshot=t1.inf",
		"Mode=HTML",
		LAST);

	return 0;
}
