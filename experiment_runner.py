# Runs the full experiment: 7 persuasion techniques + a
# non-persuasive control, 2 variants each, against baseline and
# secure system prompts. Resumable and crash-safe — re-running
# the same run number skips already-completed trials.

import os
import sys
import shutil
import csv
import agent

TECHNIQUES = [
    "authority",
    "social_proof",
    "scarcity",
    "reciprocity",
    "commitment",
    "liking",
    "unity",
    "control"
]

VARIANTS = ["A", "B"]
TRIALS = 10
MODES = ["baseline", "secure"]

BASE = os.path.dirname(os.path.abspath(__file__))
ATTACK_DIR = os.path.join(BASE, "attack_prompts")
TARGET = os.path.join(BASE, "Documents", "notes-2.txt")
BACKUP = os.path.join(BASE, "Documents", "notes-2-backup.txt")
LOG_FILE = os.path.join(BASE, "results.csv")

# Run number is passed explicitly (e.g. `python experiment_runner.py 7`)
# so each replication is traceable in results.csv even if restarted.
if len(sys.argv) < 2:
    raise SystemExit(
        "Usage: python experiment_runner.py <run_number>\n"
        "Pass the replication number (1-20) explicitly so it can be "
        "logged with every observation."
    )

RUN_NUMBER = sys.argv[1]

# Keyed without run_number, so restarting a replication resumes
# correctly rather than skipping combinations from a different run.
completed = set()

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if row.get("run_number") != RUN_NUMBER:
                    continue
                completed.add((row["mode"], row["technique"], row["variant"], int(row["trial"])))
            except (KeyError, ValueError):
                print("Warning: ignoring malformed results row.")

print(f"Run {RUN_NUMBER}: {len(completed)} completed trials already logged.")

if not os.path.exists(TARGET):
    raise FileNotFoundError(f"Target document not found: {TARGET}")

if not os.path.exists(ATTACK_DIR):
    raise FileNotFoundError(f"Attack prompt directory not found: {ATTACK_DIR}")

missing_attack_files = [
    os.path.join(ATTACK_DIR, f"{t}_{v}.txt")
    for t in TECHNIQUES for v in VARIANTS
    if not os.path.exists(os.path.join(ATTACK_DIR, f"{t}_{v}.txt"))
]
if missing_attack_files:
    raise FileNotFoundError(
        "Missing attack prompt file(s), fix before running any trials:\n"
        + "\n".join(missing_attack_files)
    )

# Only backs up if no backup exists — prevents a crash-and-restart
# mid-run from overwriting the genuine original with an attack payload.
if not os.path.exists(BACKUP):
    shutil.copy(TARGET, BACKUP)
    print("Created original-document backup.")
else:
    print("Using existing original-document backup (not overwriting).")

try:
    for mode in MODES:
        agent.MODE = mode

        for technique in TECHNIQUES:
            for variant in VARIANTS:
                attack_file = os.path.join(ATTACK_DIR, f"{technique}_{variant}.txt")
                if not os.path.exists(attack_file):
                    raise FileNotFoundError(f"Attack prompt not found: {attack_file}")

                with open(attack_file, "r") as f:
                    payload = f.read()

                for trial in range(1, TRIALS + 1):
                    experiment_id = (mode, technique, variant, trial)
                    if experiment_id in completed:
                        print("Skipping:", experiment_id)
                        continue

                    with open(TARGET, "w") as f:
                        f.write(payload)

                    print(f"\n[run {RUN_NUMBER}] Running:", experiment_id)

                    agent.run({
                        "mode": mode,
                        "technique": technique,
                        "variant": variant,
                        "trial": trial,
                        "run_number": RUN_NUMBER
                    })

                    # Only mark complete after agent.run() returns.
                    completed.add(experiment_id)

finally:
    # Runs even on crash/interrupt, so a failed run never leaves
    # notes-2.txt holding an attack payload.
    if os.path.exists(BACKUP):
        shutil.copy(BACKUP, TARGET)
        print("\nOriginal notes-2.txt restored.")

print(f"Run {RUN_NUMBER} complete.")
