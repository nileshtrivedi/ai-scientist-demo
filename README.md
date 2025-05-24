# AI Scientist Agent

This is an agent that can run system dynamics models (Vensim or XMILE) using [PySD](https://pysd.readthedocs.io/) and do things like:

- Perform sensitivity analysis
- Generate phase-portrait diagrams
- Design robust policy across multiple theories
- Design experiments to discriminate between candidate theories
- And more.

This repo is a fork of [PySD Cookbook](http://pysd-cookbook.readthedocs.org/) which provides many vensim models and analysis recipes.


### Run locally

- Run `pip install google-adk pysd matplotlib browser-use langchain-google-genai`
- Copy `scientist-agent/.env.example` to `scientist-agent/.env` and provide your Gemini API key there.
- Run `adk web` from the root directory of this project.
- Access http://localhost:8000/dev-ui?app=scientist-agent for the Agent UI.

#### Screenshots:

Listing the models available for a domain:

<img width="1674" alt="image" src="https://github.com/user-attachments/assets/b2f44ff6-28c7-428a-9678-4671b9bb4a2c" />

Running the model and seeing the plot image:

<img width="1685" alt="image" src="https://github.com/user-attachments/assets/648b7352-239a-4429-bbe0-2807a7523ac6" />

Generating phase portrait chart to see system trajectories in many states at once:

![image](https://github.com/user-attachments/assets/bf7e203d-074c-42f4-bcab-3484f0ee2180)

Vision model can analyze and identify patterns in the generated plots:

![image](https://github.com/user-attachments/assets/65aaf7b4-37f6-4e81-a138-6502a560692a)