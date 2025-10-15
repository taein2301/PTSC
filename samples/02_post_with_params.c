/*
 * LoadRunner Sample Script: POST Request with Parameters
 * Generated for testing purposes
 */

#include "web_api.h"

Action()
{
    // POST request with form data
    web_submit_data("login_request",
        "Action=http://example.com/login",
        "Method=POST",
        "RecContentType=application/json",
        "Referer=http://example.com/",
        "Snapshot=t2.inf",
        "Mode=HTML",
        ITEMDATA,
        "Name=username", "Value=testuser", ENDITEM,
        "Name=password", "Value=testpass123", ENDITEM,
        LAST);

    return 0;
}
