#!/usr/bin/python
#
# Monitor Command : wget -nv -O - myip.dnsomatic.com > /dev/null 2>&1
import sys
import httplib, urllib
import smtplib
import json
import os
from datetime import datetime, timedelta

# Change this file to the location of your JSON configuration file
configfile = "/etc/security/notifications.json"

#
# Load the Configuration file
#     Config file is a JSON file with structure
#     {
#         "pushover":{
#              "apiurl":"api.pushover.net:443",
#              "token":"Your API Token",
#              "userkey":"Your user key"
#          },
#          "email":{
#              "server":"smtp email server",
#              "fromaddress":"From Email Address",
#              "fromname":"Friendly From Name",
#              "toaddress":"To Email Address",
#              "toname":"Friendly To Name"
#          },
#          "ipmonitor":{
#              "ipsite":"tracking IP address site - I use http://myip.dnsomatic.com",
#              "addressfile":"local file name to save the old ip address in",
#              "statefile":"name of the state file to save current check state",
#              "emailnotificationrate":number of hours between email failure messages
#          }
def LoadConfig(filename):
  jdataf = open(filename)
  jdata  = json.load(jdataf)
  jdataf.close()
  return jdata

def GetNewIP(site):
  data = urllib.urlopen(site)
  return data.read().rstrip()

def IsStateOK(filename):
  retval = 0
  if os.path.isfile(filename):
    f = open(filename,"r")
    oldstate = f.read().rstrip()
    f.close()
    if (oldstate == "OK"):
      retval = 1      
    else:
      moddatetime = datetime.fromtimestamp(os.path.getmtime(filename))
      oldest = datetime.now() - timedelta(hours=cfg["email"]["emailnotificationrate"])
      if (moddatetime < oldest):
        retval = 1  
  else:
    retval = 1   
  return retval

def SetStateOK(filename):
  f = open(filename,"w")
  f.write("OK\n")
  f.close()
  
def SetStateFail(filename):
  f = open(filename,"w")
  f.write("FAIL\n")
  f.close()    

def GetIPUpdate(filename):
  if os.path.isfile(filename):
    f = open(filename,"r")
    oldip =  f.read().rstrip()
    f.close()
    return oldip
  else:
    return "???.???.???.???"  

def SaveIPUpdate(filename,ipaddress):
  f = open(filename,"w")
  f.write(ipaddress + "\n")
  f.close()


def PushOver(title,message):
  pcfg = cfg["pushover"]
  conn = httplib.HTTPSConnection(pcfg["apiurl"])
  conn.request("POST","/1/messages.json",
    urllib.urlencode({
      "token":pcfg["token"],
      "user":pcfg["userkey"],
      "message":message,
      "title":title,
      }), { "Content-type": "application/x-www-form-urlencoded"})
  conn.getresponse()

if (len(sys.argv) > 1):
  configfile = sys.argv[1]

cfg = LoadConfig(configfile)
ipfile = cfg["ipmonitor"]["addressfile"]
statefile = cfg["ipmonitor"]["statefile"]
ipsite = cfg["ipmonitor"]["ipsite"]

oldip = GetIPUpdate(ipfile)
try:
   newip = GetNewIP(ipsite)

   if (newip != oldip):
      SaveIPUpdate(ipfile,newip)
      PushOver("IP Update",newip + " from " + oldip)
   SetStateOK(statefile)
except Exception as e: 
   if (IsStateOK(statefile) == 1):
     if ("email" in cfg): 
         frominfo = "From: " + cfg["email"]["fromname"] + " - IP Monitor <" + cfg["email"]["fromaddress"] + ">"
         toinfo   = "To: " + cfg["email"]["toname"] + " <" + cfg["email"]["toaddress"] + ">"
         subject  = "Subject: IPMonitor Error"
         msgtext  = "Error performing IP Monitor lookup\n" + \
                    "Failure in GetNewIP for test site\n\n" + \
                    ipsite + "\n\n" + \
                    "Please check the Broadband connection to ensure it is working correctly\n" + \
                    "Error details from ipmonitor script below\n\n" + \
                    str(e)
     
         message = frominfo + "\n" + toinfo + "\n" + subject + "\n\n" + msgtext

         
         server = smtplib.SMTP(cfg["email"]["server"])
         server.sendmail(cfg["email"]["fromaddress"], [cfg["email"]["toaddress"]], message)
         server.quit()
         SetStateFail(statefile)   
