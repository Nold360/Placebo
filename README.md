Placebo
=======

Placebo - ClamAV Central Management for Enterprises


This will be the place for the Placebo rewrite.<br>
For POC code see: https://github.com/Nold360/Placebo_POC


What will be new?
=======
- Ticket-Based (Everything is a Ticket. If it's a scan, an update or adding a client)
- Improved communication stabiliy - Tickets are saved in the filesystem, so they can be restored
- Improved communication between Placebo and the OS using pyClamd and python-gnupg
- Improved Code! (Classes, Threads, Object - Everything i hate ;-) )
- Freshclam will be used for updateing virus-signatures
- The daemon will not run as root anymore
- Web-Interface will use salted-sha256 for Passwords instead md5
