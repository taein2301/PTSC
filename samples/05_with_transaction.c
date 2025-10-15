/*
 * LoadRunner Sample Script: Transaction with Think Time
 * Generated for testing purposes
 */

#include "web_api.h"

Action()
{
    // Start transaction
    lr_start_transaction("Login_Flow");

    // Login request
    web_submit_data("login",
        "Action=http://example.com/login",
        "Method=POST",
        "RecContentType=text/html",
        "Referer=http://example.com/",
        "Snapshot=t6.inf",
        "Mode=HTML",
        ITEMDATA,
        "Name=username", "Value=user1", ENDITEM,
        "Name=password", "Value=pass123", ENDITEM,
        LAST);

    // Think time (3 seconds)
    lr_think_time(3);

    // Navigate to dashboard
    web_url("dashboard",
        "URL=http://example.com/dashboard",
        "Resource=0",
        "RecContentType=text/html",
        "Referer=http://example.com/login",
        "Snapshot=t7.inf",
        "Mode=HTML",
        LAST);

    // End transaction
    lr_end_transaction("Login_Flow", LR_AUTO);

    return 0;
}
