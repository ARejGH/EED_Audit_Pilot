# 🚀 INTERACTIVE CLI - QUICK START GUIDE

**EED Audit Pilot - Interactive Experiment Manager**  
**Version:** 2.0 (Refactored CLI)

---

## ⚡ QUICK START

```bash
cd /home/alex/projects/research/EED_Audit_Pilot
source venv/bin/activate
python run_audit.py
```

**You'll see an interactive menu with 9 options.**

---

## 📋 MENU OPTIONS

### STANDARD RUNS (Neutral Persona + Hard Mode Distractors)

**Option 1: Llama 3 8B Instruct (Local)**
- Model: `llama3:latest`
- Persona: Neutral fact-checker
- Output: `results_llama3_hard.xlsx`
- Cost: $0.03 (judge only)
- Time: ~30s

**Option 2: Mistral 7B Instruct (Local)**
- Model: `mistral:instruct`
- Persona: Neutral fact-checker
- Output: `results_mistral_hard.xlsx`
- Cost: $0.03
- Time: ~30s

**Option 3: Gemma 2 9B (Local)**
- Model: `gemma2:9b`
- Persona: Neutral fact-checker
- Output: `results_gemma2_hard.xlsx`
- Cost: $0.03
- Time: ~30s

**Option 4: Phi-3 Medium (Local)**
- Model: `phi3:medium`
- Persona: Neutral fact-checker
- Output: `results_phi3_hard.xlsx`
- Cost: $0.03
- Time: ~60s

**Option 5: GPT-4o (Cloud Benchmark)**
- Model: `gpt-4o`
- Persona: Neutral fact-checker
- Output: `results_gpt4o_hard.xlsx`
- Cost: ~$0.18
- Time: ~60s

---

### ADVANCED

**Option 6: Pull & Run New Model**
- Interactive: Enter any model tag
- Automatically pulls from Docker
- Runs with neutral persona
- Output: `results_{modelname}_hard.xlsx`

**Example models:**
- `codellama`
- `openhermes`
- `qwen`
- `deepseek-coder`

---

### SHADOW RUNS (Biased Persona Testing)

**Option 7: Llama 3 8B - Biased Mode** ⚠️
- Model: `llama3:latest`
- Persona: **Cynical commentator** (conspiratorial)
- Output: `results_llama3_biased.xlsx`
- Purpose: Test persona framing effects
- Cost: $0.03

**Option 8: GPT-4o - Biased Mode** ⚠️
- Model: `gpt-4o`
- Persona: **Cynical commentator** (conspiratorial)
- Output: `results_gpt4o_biased.xlsx`
- Purpose: Test if SOTA resists bias
- Cost: ~$0.18

---

### OTHER

**Option 0: Exit**
- Cleanly exits the program

---

## 🎯 USAGE SCENARIOS

### Scenario 1: Quick Single Run

```bash
$ python run_audit.py

Enter your choice (0-8): 1

[Llama 3 experiment runs]

✅ Results saved to:
   - results_llama3_hard.xlsx
   - audit_log_llama3_hard.jsonl
   - audit_log_llama3_hard.md
```

---

### Scenario 2: Compare Multiple Models

```bash
# Run 1: Llama 3
$ python run_audit.py
Enter your choice: 1
[Wait ~30s]

# Run 2: Gemma 2
$ python run_audit.py
Enter your choice: 3
[Wait ~30s]

# Run 3: GPT-4o
$ python run_audit.py
Enter your choice: 5
[Wait ~60s]

# Compare results
$ python3 compare_results.py results_llama3_hard.xlsx results_gemma2_hard.xlsx results_gpt4o_hard.xlsx
```

---

### Scenario 3: Shadow Run (Persona Effect)

```bash
# Step 1: Run neutral version
$ python run_audit.py
Enter your choice: 1  # Llama 3 Neutral
[Results: results_llama3_hard.xlsx]

# Step 2: Run biased version
$ python run_audit.py
Enter your choice: 7  # Llama 3 Biased
[Results: results_llama3_biased.xlsx]

# Step 3: Compare
# Open both Excel files and compare F, A, R columns
```

---

### Scenario 4: Test New Model

```bash
$ python run_audit.py

Enter your choice: 6

Enter model tag: codellama

[Docker pulls codellama with live progress]
[Experiment runs automatically]

✅ Results: results_codellama_hard.xlsx
```

---

## 🔬 WHAT'S DIFFERENT NOW?

### Before Refactor:

```python
# Had to manually edit configuration (lines 43-49)
LOCAL_MODEL = "phi3:medium"  # Change this for each run

# Run script
$ python run_audit.py
```

### After Refactor:

```bash
# Just run and select from menu
$ python run_audit.py

[Interactive menu appears]
Enter your choice: 4  # Phi-3

[Runs automatically with correct configuration]
```

**No code editing required!**

---

## 📊 OUTPUT FILES EXPLAINED

### File Naming Convention:

```
results_{model}_{mode}.xlsx
```

**Examples:**
- `results_llama3_hard.xlsx` ← Neutral persona, Hard distractors
- `results_llama3_biased.xlsx` ← Biased persona, Hard distractors
- `results_gpt4o_hard.xlsx` ← Neutral GPT-4o, Hard distractors
- `results_mistral_hard.xlsx` ← Neutral Mistral, Hard distractors

**Suffix Meanings:**
- `_hard` = Neutral persona + Hard Mode distractors (current standard)
- `_biased` = Cynical persona + Hard Mode distractors (Shadow Run)

---

## ⚠️ IMPORTANT NOTES

### Shadow Runs Are Experimental:

The biased persona is **intentionally adversarial** to test:
- Resistance to evidence
- Belief persistence
- Instruction tuning robustness

**Not for production use** - research purposes only.

---

### Prerequisites:

**For Local Models (Options 1-4, 6):**
- Docker container running (`ollama_research`)
- Models available or will be auto-pulled

**For Cloud Models (Options 5, 8):**
- `OPENAI_API_KEY` environment variable set

**For Dry-Run:**
- No prerequisites, uses mock responses

---

## 🎓 TIPS & TRICKS

### Tip 1: Quick Model Comparison

Run all local models back-to-back:
```bash
for i in 1 2 3 4; do
    echo $i | python run_audit.py
done
```

### Tip 2: Check Before Running

Verify models available:
```bash
docker exec ollama_research ollama list
```

### Tip 3: Monitor Progress

Output shows:
- ✅ Connection status
- 📊 Progress bar
- ⏱️  Time per topic
- 💾 Files saved

### Tip 4: Interrupt-Safe

Press `Ctrl+C` anytime:
- Current topic completes
- Results saved
- Safe to resume

---

## 🏆 ADVANTAGES OF NEW CLI

### User Experience:
- ✅ No code editing required
- ✅ Clear menu options
- ✅ Immediate feedback
- ✅ Error messages helpful

### Flexibility:
- ✅ Easy model switching
- ✅ Persona selection
- ✅ New model testing
- ✅ Multiple workflows

### Safety:
- ✅ Clear file naming (no overwrites)
- ✅ All previous features preserved
- ✅ Dry-run mode available
- ✅ Graceful error handling

### Research:
- ✅ Standard benchmarking (options 1-5)
- ✅ Persona effect studies (options 7-8)
- ✅ Exploratory testing (option 6)
- ✅ Methodological rigor maintained

---

## 📚 DOCUMENTATION

### Core Documents:
1. `protocol.md` - Experimental protocol
2. `README_INTERACTIVE_CLI.md` - This quick start guide
3. `CLI_REFACTOR_COMPLETE.md` - Technical details
4. `SHADOW_RUN_SETUP.md` - Biased persona documentation

### Verification Documents:
5. `METHODOLOGY_VERIFICATION.md` - Meta-audit certification
6. `FINAL_RESULTS_SUMMARY.md` - Complete findings

---

## ✅ YOU'RE READY!

Just run:
```bash
python run_audit.py
```

And select your experiment from the menu.

**The interactive CLI is ready for comprehensive LLM cognitive auditing.** 🚀

