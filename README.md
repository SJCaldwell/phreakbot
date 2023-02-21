# phreakbot

- Drive a browser with GPT-3 with [natbot](https://github.com/nat/natbot)
- Fuzz parameters
- Recognize vulners
- Writeup results

Currently demoing against Damn Vulnerable Web App

To demo capabilities.
1. Have `.env` file with `OPENAI_API_KEY` set
2. Run [DVWA](https://github.com/digininja/DVWA) with `docker run --rm -it -p 80:80 vulnerables/web-dvwa`
3. Run the proxy.py file
4. Run phreakbot.py


Ideas for improvement:
- include text of current sitemap into prompt 
- Prompt chaining
- Make a recorder to collect human feedback and do better few-shot
