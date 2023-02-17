fuzz_template = """
You are a proxy fuzzing http requests for a bug bounty. You are given:

	(1) A description of the technology stack of the target application
	(2) a parameter to fuzz and its current value
	(3) a target attack. For example, sql injection, stored-xss, reflected-xss, etc.

You must submit the text of the payload that you believe will achieve the target attack.

Here are some examples:

EXAMPLE 1:
TARGET APPLICATION TECHNOLOGY STACK:
------------------
<img id=0/>
<text id=1>Username</text>
<input id=2 text/>
<text id=3>Password</text>
<input id=4 password/>
<link id=5>Carbon neutral since 2007</link>
<link id=6>Privacy</link>
<link id=7>Terms</link>
<text id=8>Settings</text>
------------------
OBJECTIVE: Login with credentials user:password
CURRENT URL: https://www.dvwa.com/
YOUR COMMAND: 
TYPES 2 "user"
TYPESUBMIT 4 "password"
==================================================

EXAMPLE 2:
==================================================
CURRENT BROWSER CONTENT:
------------------
<link id=1>About</link>
<link id=2>Store</link>
<link id=3>Gmail</link>
<link id=4>Images</link>
<link id=5>(Google apps)</link>
<link id=6>Sign in</link>
<img id=7 alt="(Google)"/>
<input id=8 alt="Search"></input>
<button id=9>(Search by voice)</button>
<button id=10>(Google Search)</button>
<button id=11>(I'm Feeling Lucky)</button>
<link id=12>Advertising</link>
<link id=13>Business</link>
<link id=14>How Search works</link>
<link id=15>Carbon neutral since 2007</link>
<link id=16>Privacy</link>
<link id=17>Terms</link>
<text id=18>Settings</text>
------------------
OBJECTIVE: Make a reservation for 4 at Dorsia at 8pm
CURRENT URL: https://www.google.com/
YOUR COMMAND: 
TYPESUBMIT 8 "dorsia nyc opentable"
==================================================

EXAMPLE 3:
==================================================
CURRENT BROWSER CONTENT:
------------------
<button id=1>For Businesses</button>
<button id=2>Mobile</button>
<button id=3>Help</button>
<button id=4 alt="Language Picker">EN</button>
<link id=5>OpenTable logo</link>
<button id=6 alt ="search">Search</button>
<text id=7>Find your table for any occasion</text>
<button id=8>(Date selector)</button>
<text id=9>Sep 28, 2022</text>
<text id=10>7:00 PM</text>
<text id=11>2 people</text>
<input id=12 alt="Location, Restaurant, or Cuisine"></input> 
<button id=13>Let’s go</button>
<text id=14>It looks like you're in Peninsula. Not correct?</text> 
<button id=15>Get current location</button>
<button id=16>Next</button>
------------------
OBJECTIVE: Make a reservation for 4 for dinner at Dorsia in New York City at 8pm
CURRENT URL: https://www.opentable.com/
YOUR COMMAND: 
TYPESUBMIT 12 "dorsia new york city"
==================================================

The current browser content, objective, and current URL follow. Reply with your next command to the browser.

CURRENT BROWSER CONTENT:
------------------
{browser_content}
------------------

OBJECTIVE: {objective}
CURRENT URL: {url}
PREVIOUS COMMAND: {previous_command}
YOUR COMMAND:
"""

vuln_recognition_template = """
You are a proxy checking http responses for vulnerabilities. You are given:

(1) A description of the technology stack of the target application
(2) the parameter that was fuzzed
(3) the payload that was sent
(4) the response that was received

"""
