# Persuasion-Based Prompt Injection Against Agentic AI

Code and dataset for a final-year research project evaluating whether persuasion techniques derived from Cialdini's seven principles of influence affect the success rate of indirect prompt injection attacks against an agentic AI framework based on Qwen2.5:7B, relative to a non-persuasive baseline.

* **Note:** Code was written by Claude (Anthropic).

## Key finding

Across 6,400 trials, no persuasion technique outperformed a plain, direct request (the `control` condition). Four techniques matched or nearly matched it; three (`commitment`, `scarcity`, `unity`) performed substantially worse. A "secure" system prompt reduced compliance for `unity` almost to zero, but *increased* compliance for `commitment` and `scarcity`. This is likely because its conditional wording ("unless required by the user's original task") gave those two techniques a built-in exception to argue through.

I've written up the findings and discussed the results in more detail on LinkedIn.

## Prerequisites

Requires [Ollama](https://ollama.com) with `qwen2.5:7b` pulled:

```bash
ollama pull qwen2.5:7b
```

The model is not hardcoded to Qwen. To test a different Ollama model, for example Mistral, pull it instead:

```bash
ollama pull mistral
```

Then change the `MODEL` constant near the top of `agent.py` and `connectivity_agent.py` to match, for example:

```python
MODEL = "mistral"
```

By default, the scripts expect Ollama to be running on `localhost:11434`. If it is running elsewhere, set the `OLLAMA_URL` environment variable:

```bash
export OLLAMA_URL="http://<your-host>:11434/api/chat"
```

You can check that Ollama is reachable with:

```bash
curl http://localhost:11434/api/tags
```

## Setup

Clone the repo and work from its root:

```bash
git clone https://github.com/mariokhawam/prompt-injection-project.git
cd prompt-injection-project
```

### Environment

Create the virtual environment inside the repo folder:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install requests
```

Deactivate it when you're finished:

```bash
deactivate
```

## Running the experiment

### Connectivity checks

First, check that Ollama and the tool-calling setup are working:

```bash
python connectivity_experiment_runner.py
```

### Main experiment

Once the connectivity checks complete successfully, start the main experiment:

```bash
python experiment_runner.py 1
```

After it completes, increment the experiment number and continue through `20`:

```bash
python experiment_runner.py 2
python experiment_runner.py 3
# ...
python experiment_runner.py 20
```

Each experiment is resumable and crash-safe. Re-entering the same number skips trials already logged in `results.csv`.

## Repository structure

* `agent_core.py`: shared tool-calling, scoring, and logging logic
* `agent.py` / `experiment_runner.py`: main experiment scripts (7 persuasion techniques + non-persuasive control, baseline/secure system prompts)
* `connectivity_agent.py` / `connectivity_experiment_runner.py`: checks that Ollama and the tool-calling setup work before the main experiment; not part of the experimental findings
* `Documents/`: task documents and the protected dummy target file
* `attack_prompts/`: the 16 injected prompts (7 techniques x 2 variants, plus 2 control variants)
* `test_prompts/`: 10 neutral prompts used for the connectivity check
* `responses/`: plaintext response logs from every trial across all 20 runs
* `connectivity-responses/`: plaintext response logs from the connectivity checks

## Results files

The scripts automatically generate the response folders and CSV result files during the experiments.

The repository includes `results.csv` and `connectivity-results.csv` from my own experiments for documenting the findings. If you are cloning the repository to run your own experiments, delete these files before starting so that your results are generated from a clean slate.

## Ethics and scope

The "protected" resource is a dummy value stored in `secrets.txt` within a local sandbox built for this project. No real system or data was targeted.
