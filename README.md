# IPMONITOR

IP Monitor is a simple Python script that monitors the IP address of your Broadband connection and sends a Pushover Notification when it is changed.

* Requirements : Python (Tested against Python 2.7.9)
* Operation    : This can be set to run on a cron job. No input parameters are required but if supplied a single input parm of the config file name

A static configuration file in JSON format is loaded at runtime containing all of the relevant static data including PushOver API information and Email addresses.

As I use a local Email server for my notifications internally I do not require or use SMTP authentication.
This can be added if so desired.
