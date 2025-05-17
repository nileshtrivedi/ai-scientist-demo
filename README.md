## AI Scientist Agent

This is a fork of [PySD Cookbook](http://pysd-cookbook.readthedocs.org/) but I have added an agent that can perform PySD operations on multiple SD models on arbitrary scientific domains.

This is built using Google's [Agent Development Kit.](https://google.github.io/adk-docs/)
Copy `scientist-agent/.env.example` to `scientist-agent/.env` and provide your Gemini API key there.
Run `adk web` from the root directory of this project and access http://localhost:8000/dev-ui?app=scientist-agent for the Agent UI.

#### Screenshots:

Listing the models available for a domain:

<img width="1674" alt="image" src="https://github.com/user-attachments/assets/b2f44ff6-28c7-428a-9678-4671b9bb4a2c" />

Running the model and seeing the plot image:

<img width="1685" alt="image" src="https://github.com/user-attachments/assets/648b7352-239a-4429-bbe0-2807a7523ac6" />