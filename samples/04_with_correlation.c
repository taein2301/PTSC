/*
 * LoadRunner Sample Script: Request with Correlation
 * Generated for testing purposes
 */

#include "web_api.h"

Action()
{
	// Register correlation to extract session token
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

	return 0;
}
