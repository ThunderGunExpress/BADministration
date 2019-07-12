# BADministration

#### What is BADministration?

BADministration is a tool which interfaces with management or administration applications from an offensive standpoint. It attempts to provide offsec personnel a tool with the ability to identify and leverage these non-technical vulnerabilities. As always: use for good, promote security, and fight application propagation. 

Sorry for using python2.7, I found a lot of the vendor APIs would only run on 2.7 and I'm not experienced enough to mix and match python versions.

#### Application Propagation

In my opinion, we often do a fantastic job of network segmentation and we're starting to catch on with domain segmentation; however, one area I often see us fall down is application segmentation. Application segmentation is similar to network segmentation in that we're trying to reduce the exposure of a critical zone from a less trusted zone if it were to become exploited. Administration applications often have privileged access to all its clients, if an attacker lands on that administration application there is a good chance all the clients can become exploited as well. Application segmentation tries to ensure that server-to-client relationships don't cross any trust boundaries. For example, if your admin network is trust level 100 and it's administered by your NMS server, your NMS server should be considered trust level 100.

#### Installation

There will be a collection of python scripts, exes, and who knows what; for the central python module it's pretty simple

**pip install -r requirements.txt**

## Current Modules

#### Solarwinds Orion

- solarwinds-enum - Module used to enumerate clients of Orion
- solarwinds-listalerts - Lists Orion alerts and draws attention to malicious BADministration alerts
- solarwinds-alertremove - Removes the malicious alert
- solarwinds-syscmd - Executes a system command on the Orion server via malicious alert
- Standalone **x64** .NET BADministration_SWDump.exe - Scrapes memory for WMI credentials used by Orion.
  - Can consume large amounts of memory, use at your own risk
  - Compile me as x64

### Check us out at 
- https://ijustwannared.team
- https://twitter.com/cpl3h
- https://twitter.com/DarknessCherry
