# Runs a batch of pipeline smoke tests. Resumable and crash-safe.
# Run after any code change and before a full experiment run, to
# confirm Ollama is reachable and tool-calling works end to end.
#
# Do not run concurrently with experiment_runner.py — both write
# to Documents/notes-2.txt.

import os
import shutil
import csv
import connectivity_agent

CONNECTIVITY_TESTS = 10

BASE = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(BASE, "test_prompts")
TARGET = os.path.join(BASE, "Documents", "notes-2.txt")
BACKUP = os.path.join(BASE, "Documents", "notes-2-backup.txt")
LOG_FILE = os.path.join(BASE, "connectivity-results.csv")

completed = set()

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                completed.add(int(row["test_number"]))
            except (KeyError, ValueError):
                print("Warning: ignoring malformed results row.")

print(f"{len(completed)} completed connectivity tests already logged.")

if not os.path.exists(TARGET):
    raise FileNotFoundError(f"Target document not found: {TARGET}")

if not os.path.exists(PROMPT_DIR):
    raise FileNotFoundError(f"Prompt directory not found: {PROMPT_DIR}")

missing_prompt_files = [
    os.path.join(PROMPT_DIR, f"test_{n}.txt")
    for n in range(1, CONNECTIVITY_TESTS + 1)
    if not os.path.exists(os.path.join(PROMPT_DIR, f"test_{n}.txt"))
]
if missing_prompt_files:
    raise FileNotFoundError(
        "Missing prompt file(s), fix before running any tests:\n"
        + "\n".join(missing_prompt_files)
    )

# Only backs up if no backup exists — prevents a crash-and-restart
# from overwriting the genuine original with a mid-test payload.
if not os.path.exists(BACKUP):
    shutil.copy(TARGET, BACKUP)
    print("Created original-document backup.")
else:
    print("Using existing original-document backup (not overwriting).")

try:
    for test_number in range(1, CONNECTIVITY_TESTS + 1):
        if test_number in completed:
            print("Skipping test:", test_number)
            continue

        prompt_file = os.path.join(PROMPT_DIR, f"test_{test_number}.txt")
        with open(prompt_file, "r") as f:
            payload = f.read()

        with open(TARGET, "w") as f:
            f.write(payload)

        print(f"\nRunning connectivity test {test_number}/{CONNECTIVITY_TESTS}")

        connectivity_agent.run({"test_number": test_number})
        completed.add(test_number)

finally:
    # Runs even on crash/interrupt, so a failed run never leaves
    # notes-2.txt holding a test payload.
    if os.path.exists(BACKUP):
        shutil.copy(BACKUP, TARGET)
        print("\nOriginal notes-2.txt restored.")

print("Connectivity test batch complete.")
