# phreakbot

- Drive a browser with GPT-3
- Fuzz parameters
- Recognize vulners
- Writeup results

Currently demoing against Damn Vulnerable Web App

To demo capabilities.
1. Have `.env` file with `OPENAI_API_KEY` set
2. Run the proxy.py file
3. Run phreakbot.py
4. Enter an objective or hit enter to use the default objective `login to the application with default credentials, then submit as many forms as possible`

Ideas for improvement:
- include text of current sitemap into prompt 
- Prompt chaining
- Make a recorder to collect human feedback and do better few-shot
