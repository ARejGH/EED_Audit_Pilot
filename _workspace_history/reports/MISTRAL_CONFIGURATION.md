# 🔬 MISTRAL 7B CONFIGURATION - LOCAL RUN

**Date:** November 26, 2025  
**Status:** ✅ **CONFIGURED AND READY**

---

## 📋 CONFIGURATION SUMMARY

### ✅ Subject Model: Mistral 7B Instruct (Local)

```python
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "mistral:instruct"
LOCAL_API_KEY = "ollama"
```

**Location:** Lines 43-49 in `run_audit.py`

### ✅ Judge Model: GPT-4o (Cloud)

```python
JUDGE_MODEL = "gpt-4o"
```

---

## 📁 OUTPUT FILES

All results will be saved with `_mistral` suffix to avoid overwriting previous experiments:

| File Type | Filename |
|-----------|----------|
| **Excel** | `results_mistral.xlsx` ✅ |
| **JSONL** | `audit_log_mistral.jsonl` ✅ |
| **Markdown** | `audit_log_mistral.md` ✅ |

---

## 🖥️ STARTUP MESSAGE

```
================================================================================
🚀 EED AUDIT PILOT - COGNITIVE AUDIT OF LLM
================================================================================
🔬 STARTING LOCAL RUN: Mistral 7B
📊 Subject Model: mistral:instruct
⚖️  Judge Model: gpt-4o
================================================================================
```

---

## ✅ DRY RUN VERIFICATION

```bash
$ python run_audit.py --dry-run

🔬 STARTING LOCAL RUN: Mistral 7B
📊 Subject Model: mistral:instruct
⚖️  Judge Model: gpt-4o

📤 [DRY RUN] PROMPT TO mistral:instruct
[SYSTEM]: You are an AI assistant acting as a political-media fact-checker...
```

**Status:** ✅ All prompts correctly routed to `mistral:instruct`

---

## 🚀 EXECUTION PLAN

### Prerequisites:

1. **Ensure Mistral model is available in Docker:**
   ```bash
   docker exec ollama_research ollama list
   ```
   
   If not available, pull it:
   ```bash
   docker exec ollama_research ollama pull mistral:instruct
   ```

2. **Set OpenAI API key for Judge:**
   ```bash
   export OPENAI_API_KEY="sk-your-key"
   ```

### Run Mistral Experiment:

```bash
cd /home/alex/projects/research/EED_Audit_Pilot
source venv/bin/activate
python run_audit.py
```

---

## 💰 COST ESTIMATE

### Mistral 7B Run:
- **Subject Model:** FREE (local Docker)
- **Judge Model:** 3× GPT-4o calls ≈ $0.03
- **Total:** ~$0.03

---

## 📊 COMPARISON MATRIX

After running all three experiments:

| Model | Files | Status |
|-------|-------|--------|
| **Llama 3 8B** | results.xlsx<br>audit_log.jsonl<br>audit_log.md | ✅ Complete |
| **GPT-4o** | results_gpt4o.xlsx<br>audit_log_gpt4o.jsonl<br>audit_log_gpt4o.md | ⏳ Pending |
| **Mistral 7B** | results_mistral.xlsx<br>audit_log_mistral.jsonl<br>audit_log_mistral.md | 🔄 Ready to run |

---

## 🔬 COMPARATIVE ANALYSIS STRUCTURE

### Expected Metrics to Compare:

| Metric | Llama 3 | GPT-4o | Mistral 7B |
|--------|---------|--------|------------|
| **Factuality (F)** | 100% | ? | ? |
| **DQI Score** | 2 | ? | ? |
| **Source Citations** | 1 | ? | ? |
| **Calibration (Brier)** | 0.0139 | ? | ? |
| **Autorevision (A)** | 2 | ? | ? |
| **Retention (R)** | 1 | ? | ? |
| **Q_pol** | TBD | ? | ? |
| **Inference Time** | ~10s/topic | ? | ? |
| **Cost** | $0.03 | ~$0.18 | ~$0.03 |

---

## 📝 MODEL SPECIFICATIONS

### Mistral 7B Instruct:
- **Parameters:** 7 billion
- **Context Window:** 8k tokens
- **Strengths:** Efficient, good reasoning
- **Architecture:** Transformer with sliding window attention
- **Training:** Instruction-tuned for chat/assistant tasks

### Comparison:
- **Llama 3 8B:** 8B parameters, general purpose
- **GPT-4o:** ~1T parameters, SOTA performance
- **Mistral 7B:** 7B parameters, optimized efficiency

---

## ⚙️ CONFIGURATION HISTORY

### Phase 1: Llama 3 (Initial)
```python
LOCAL_MODEL = "llama3:latest"
# Output: results.xlsx
```

### Phase 2: GPT-4o (Benchmarking)
```python
LOCAL_MODEL = "gpt-4o"
LOCAL_BASE_URL = "https://api.openai.com/v1"
# Output: results_gpt4o.xlsx
```

### Phase 3: Mistral 7B (Current)
```python
LOCAL_MODEL = "mistral:instruct"
LOCAL_BASE_URL = "http://localhost:12434/v1"
# Output: results_mistral.xlsx
```

---

## 🎯 SCIENTIFIC QUESTIONS

After completing Mistral run:

1. **Accuracy:** Does Mistral match Llama 3's factuality?
2. **Quality:** How does Mistral's DQI compare?
3. **Calibration:** Is Mistral better/worse calibrated than Llama 3?
4. **Epistemic Humility:** Does Mistral revise beliefs as well as Llama 3?
5. **Retention:** Does Mistral maintain corrections?
6. **Size vs Performance:** Can 7B match 8B performance?

---

## ⚠️ IMPORTANT NOTES

### Model Availability:

Before running, verify Mistral is available:

```bash
docker exec ollama_research ollama list
```

Expected output should include:
```
mistral:instruct    [MODEL_ID]    [SIZE]    [DATE]
```

If missing, the script will **automatically attempt to pull it**.

### File Safety:

✅ **All previous results are safe:**
- `results.xlsx` (Llama 3) - Protected
- `results_gpt4o.xlsx` (GPT-4o) - Protected  
- `results_mistral.xlsx` (Mistral) - New file

### Switching Between Configurations:

To switch back to a different model, edit lines 43-49 in `run_audit.py`:

**For Llama 3:**
```python
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "llama3:latest"
LOCAL_API_KEY = "ollama"
```

**For GPT-4o:**
```python
LOCAL_BASE_URL = "https://api.openai.com/v1"
LOCAL_MODEL = "gpt-4o"
LOCAL_API_KEY = os.environ.get("OPENAI_API_KEY")
```

**For Mistral:** (Current)
```python
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "mistral:instruct"
LOCAL_API_KEY = "ollama"
```

---

## ✅ READY TO EXECUTE

**Configuration Status:** 🟢 **COMPLETE**

All changes applied:
1. ✅ Subject model set to `mistral:instruct`
2. ✅ Base URL set to local Ollama (port 12434)
3. ✅ Output filenames use `_mistral` suffix
4. ✅ Startup message shows "STARTING LOCAL RUN: Mistral 7B"
5. ✅ Judge remains GPT-4o
6. ✅ Dry-run test passed

**Next Command:**
```bash
python run_audit.py
```

**Expected Duration:** ~30-40 seconds (3 topics)

---

## 📊 EXPECTED OUTPUT

```
🔬 STARTING LOCAL RUN: Mistral 7B
📊 Subject Model: mistral:instruct
⚖️  Judge Model: gpt-4o

✅ Ollama service is running
✅ Model 'mistral:instruct' found locally
✅ Successfully connected to mistral:instruct

Processing topics: 100% |██████████| 3/3 [00:30<00:00, 10s/topic]

✅ T1 completed successfully!
✅ T2 completed successfully!
✅ T3 completed successfully!

📊 Results saved to:
   - results_mistral.xlsx
   - audit_log_mistral.jsonl
   - audit_log_mistral.md
```

---

**Ready for Mistral 7B benchmarking!** 🚀

