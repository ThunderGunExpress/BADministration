# BADministration

#### What is BADministration?

BADministration is a tool which interfaces with management or administration applications from an offensive standpoint. It attempts to provide offsec personnel the ability to identify and leverage these non-technical vulnerabilities. As always: use for good, promote security, and fight application propagation.

#### Application Propagation

In my opinion, we often do a fantastic job of network segmentation and we're starting to catch on with domain segmentation; however, one area I often see us fall down is application segmentation. Application segmentation is similar to network segmentation in that we're trying to reduce the exposure of a critical network (or server) through exploitation of a less critical network. For example, if you're admin network is trust level 100 and it's a client of your NMS server, your NMS server is trust level 100 as well.

## Current Modules

#### Solarwinds Orion

- solarwinds-enum - Module used to enumerate clients of Orion
- solarwinds-listalerts - Lists Orion alerts and draws attention to malicious BADministration alerts
- solarwinds-alertremove - Removes the malicious alert
- solarwinds-syscmd - Executes a system command on the Orion server via malicious alert
- standalone .NET BADministration_SWDump.exe - Scrapes memory for WMI credentials used by Orion.


Check us out at 
- https://ijustwannared.team
- https://twitter.com/cpl3h
- https://twitter.com/DarknessCherry
  
