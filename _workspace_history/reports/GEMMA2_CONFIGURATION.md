# 🔬 GEMMA 2 9B CONFIGURATION - LOCAL RUN

**Date:** November 26, 2025  
**Status:** ✅ **CONFIGURED AND READY**

---

## 📋 CONFIGURATION SUMMARY

### ✅ Subject Model: Gemma 2 9B (Local)

```python
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "gemma2:9b"
LOCAL_API_KEY = "ollama"
```

**Location:** Lines 43-49 in `run_audit.py`

### ✅ Judge Model: GPT-4o (Cloud)

```python
JUDGE_MODEL = "gpt-4o"
```

---

## 📁 OUTPUT FILES

All results will be saved with `_gemma2` suffix to avoid overwriting previous experiments:

| File Type | Filename |
|-----------|----------|
| **Excel** | `results_gemma2.xlsx` ✅ |
| **JSONL** | `audit_log_gemma2.jsonl` ✅ |
| **Markdown** | `audit_log_gemma2.md` ✅ |

---

## 🖥️ STARTUP MESSAGE

```
================================================================================
🚀 EED AUDIT PILOT - COGNITIVE AUDIT OF LLM
================================================================================
🔬 STARTING LOCAL RUN: Gemma 2 9B
📊 Subject Model: gemma2:9b
⚖️  Judge Model: gpt-4o
================================================================================
```

---

## ✅ DRY RUN VERIFICATION

```bash
$ python run_audit.py --dry-run

🔬 STARTING LOCAL RUN: Gemma 2 9B
📊 Subject Model: gemma2:9b
⚖️  Judge Model: gpt-4o

📤 [DRY RUN] PROMPT TO gemma2:9b
[SYSTEM]: You are an AI assistant acting as a political-media fact-checker...
```

**Status:** ✅ All prompts correctly routed to `gemma2:9b`

---

## 🚀 EXECUTION PLAN

### Prerequisites:

1. **Ensure Gemma 2 model is available in Docker:**
   ```bash
   docker exec ollama_research ollama list
   ```
   
   If not available, pull it:
   ```bash
   docker exec ollama_research ollama pull gemma2:9b
   ```

2. **Set OpenAI API key for Judge:**
   ```bash
   export OPENAI_API_KEY="sk-your-key"
   ```

### Run Gemma 2 Experiment:

```bash
cd /home/alex/projects/research/EED_Audit_Pilot
source venv/bin/activate
python run_audit.py
```

---

## 💰 COST ESTIMATE

### Gemma 2 9B Run:
- **Subject Model:** FREE (local Docker)
- **Judge Model:** 3× GPT-4o calls ≈ $0.03
- **Total:** ~$0.03

---

## 📊 COMPARISON MATRIX

After running all models:

| Model | Size | Files | Status |
|-------|------|-------|--------|
| **Llama 3** | 8B | results_llama3.xlsx | ✅ Complete |
| **Mistral 7B** | 7B | results_mistral.xlsx | ✅ Complete |
| **Gemma 2** | 9B | results_gemma2.xlsx | 🔄 Ready to run |
| **GPT-4o** | ~1T | results_gpt4o.xlsx | ⏳ Pending |

---

## 🔬 MODEL SPECIFICATIONS

### Gemma 2 9B:
- **Parameters:** 9 billion (largest local model so far)
- **Developer:** Google
- **Architecture:** Transformer with innovations from PaLM 2
- **Strengths:** Strong reasoning, multilingual, efficient
- **Context Window:** 8k tokens
- **Training:** Instruction-tuned for chat/assistant tasks

### Size Comparison:
- **Mistral 7B:** 7B parameters
- **Llama 3:** 8B parameters  
- **Gemma 2:** 9B parameters (13% larger than Llama 3)
- **GPT-4o:** ~1 trillion parameters

---

## 🎯 RESEARCH QUESTIONS

After completing Gemma 2 run:

1. **Does size matter?** Will 9B parameters outperform 7B Mistral and 8B Llama 3?
2. **Google vs Meta vs Mistral AI:** How do different organizations' models compare?
3. **Parsing compatibility:** Will Gemma 2 use standard or custom formatting?
4. **Calibration:** Will larger size improve confidence calibration?
5. **Epistemic humility:** Does model size affect autorevision and retention?

---

## ⚙️ CONFIGURATION HISTORY

### Phase 1: Llama 3 8B (Meta)
```python
LOCAL_MODEL = "llama3:latest"
# Output: results_llama3.xlsx
# Status: Complete (100% factuality)
```

### Phase 2: Mistral 7B (Mistral AI)
```python
LOCAL_MODEL = "mistral:instruct"
# Output: results_mistral.xlsx
# Status: Complete (66.7% factuality, parsing fixed)
```

### Phase 3: Gemma 2 9B (Google) - Current
```python
LOCAL_MODEL = "gemma2:9b"
# Output: results_gemma2.xlsx
# Status: Ready to run
```

### Phase 4: GPT-4o (~1T, OpenAI)
```python
LOCAL_MODEL = "gpt-4o"
LOCAL_BASE_URL = "https://api.openai.com/v1"
# Output: results_gpt4o.xlsx
# Status: Pending
```

---

## 📈 EXPECTED COMPARISON

| Model | Developer | Size | Factuality | DQI | A | R | Cost |
|-------|-----------|------|------------|-----|---|---|------|
| Mistral 7B | Mistral AI | 7B | 66.7% | 2 | 2 | 1 | $0.03 |
| Llama 3 8B | Meta | 8B | 100% | 2 | 2 | 1 | $0.03 |
| **Gemma 2 9B** | **Google** | **9B** | **?** | **?** | **?** | **?** | **$0.03** |
| GPT-4o | OpenAI | ~1T | ? | ? | ? | ? | ~$0.18 |

**Hypothesis:** Gemma 2 9B should perform between Llama 3 and GPT-4o, potentially matching Llama 3's 100% factuality.

---

## ⚠️ IMPORTANT NOTES

### Parsing Considerations:

Based on Mistral experience:
- ✅ **Enhanced regex** now handles format variations
- ✅ **Fallback logic** supports multiple patterns
- ⚠️ **Monitor T3** for any parsing issues
- ✅ **UNKNOWN detection** will flag failures

### Model Availability:

Before running, verify Gemma 2 is available:

```bash
docker exec ollama_research ollama list
```

Expected output should include:
```
gemma2:9b    [MODEL_ID]    [SIZE]    [DATE]
```

If missing, the script will **automatically attempt to pull it** (~5 GB download).

### File Safety:

✅ **All previous results are protected:**
- `results_llama3.xlsx` - Llama 3 results (preserved)
- `results_mistral.xlsx` - Mistral results (preserved)  
- `results_gemma2.xlsx` - New file (will be created)
- `results_gpt4o.xlsx` - GPT-4o results (preserved if exists)

---

## 🔄 SWITCHING CONFIGURATIONS

To switch back to a different model, edit lines 43-49 in `run_audit.py`:

**For Llama 3:**
```python
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "llama3:latest"
LOCAL_API_KEY = "ollama"
```

**For Mistral 7B:**
```python
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "mistral:instruct"
LOCAL_API_KEY = "ollama"
```

**For Gemma 2 9B:** (Current)
```python
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "gemma2:9b"
LOCAL_API_KEY = "ollama"
```

**For GPT-4o:**
```python
LOCAL_BASE_URL = "https://api.openai.com/v1"
LOCAL_MODEL = "gpt-4o"
LOCAL_API_KEY = os.environ.get("OPENAI_API_KEY")
```

---

## ✅ READY TO EXECUTE

**Configuration Status:** 🟢 **COMPLETE**

All changes applied:
1. ✅ Subject model set to `gemma2:9b`
2. ✅ Base URL set to local Ollama (port 12434)
3. ✅ Output filenames use `_gemma2` suffix
4. ✅ Startup message shows "STARTING LOCAL RUN: Gemma 2 9B"
5. ✅ Judge remains GPT-4o
6. ✅ Dry-run test passed
7. ✅ Enhanced regex parsing ready (from Mistral fix)

**Next Command:**
```bash
python run_audit.py
```

**Expected Duration:** ~30-40 seconds (3 topics)

---

## 📊 EXPECTED OUTPUT

```
🔬 STARTING LOCAL RUN: Gemma 2 9B
📊 Subject Model: gemma2:9b
⚖️  Judge Model: gpt-4o

✅ Ollama service is running
✅ Model 'gemma2:9b' found locally (or auto-pulled)
✅ Successfully connected to gemma2:9b

Processing topics: 100% |██████████| 3/3 [00:30<00:00, 10s/topic]

✅ T1 completed successfully!
✅ T2 completed successfully!
✅ T3 completed successfully!

📊 Results saved to:
   - results_gemma2.xlsx
   - audit_log_gemma2.jsonl
   - audit_log_gemma2.md
```

---

## 🎯 RESEARCH VALUE

Gemma 2 9B adds significant value to the study:

1. **Google's approach:** Different from Meta (Llama) and Mistral AI
2. **Largest local model:** 9B vs 7-8B (13% more parameters)
3. **Recent architecture:** Benefits from PaLM 2 innovations
4. **Complete comparison:** 3 open-source models + 1 SOTA cloud model

---

**Ready for Gemma 2 9B benchmarking!** 🚀



