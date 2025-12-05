https://github.com/user-attachments/assets/dffb17d3-cf1c-40e0-ab53-5aaa5f88fe9f
# Model-Based Planning for Device-Control Agents

## Quick Start

This section will guide you on how to quickly use `gpt-4-vision-preview` as an agent to complete specific tasks for you on your Android app.

### Step 1. Prerequisites

1. On your PC, download and install [Android Debug Bridge](https://developer.android.com/tools/adb) (adb) which is a
   command-line tool that lets you communicate with your Android device from the PC.

2. Get an Android device and enable the USB debugging that can be found in Developer Options in Settings.

3. Connect your device to your PC using a USB cable.

4. Clone this repo and install the dependencies. All scripts in this project are written in Python 3 so make sure you
   have installed it.

```bash
cd Model-Based Planning for Device-Control Agents
pip install -r requirements.txt
```

### 🤖 Step 2. Configure the Agent

The Agent needs to be powered by a multi-modal model which can receive both text and visual inputs. During our experiment
, we used `gpt-4-vision-preview` as the model to make decisions on how to take actions to complete a task on the smartphone.

To configure your requests to GPT-4V, you should modify `config.yaml` in the root directory.
There are two key parameters that must be configured to try AppAgent:
1. OpenAI API key: you must purchase an eligible API key from OpenAI so that you can have access to GPT-4V.
2. Request interval: this is the time interval in seconds between consecutive GPT-4V requests to control the frequency 
of your requests to GPT-4V. Adjust this value according to the status of your account.

Other parameters in `config.yaml` are well commented. Modify them as you need.

### Run the Agent

you can run `run.py` in the root directory. Follow the prompted instructions to enter the name of the app and provide the task description. Then, your agent will do the job for you. The agent will automatically create the world model and the associated plans, and revise them accordingly throughout the process.

```bash
python run.py
```



## Evaluation on MobileAgentBench

This section provides a detailed guide on how to evaluate our proposed method using the MobileAgentBench framework.

### Step 1: Build MobileAgentBench as a Python Library

1. Clone [MobileAgentBench](https://github.com/MobileAgentBench/mobile-agent-bench) to your environment.

2. Install the repository as Python library by following the installation instructions provided in the repository.

### Step 2: Execute the TestAgent

Once the test environment has been properly configured, execute the `TestAgent.py` script. The evaluation results will be generated and displayed automatically.





