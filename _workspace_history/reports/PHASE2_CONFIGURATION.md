# 🚀 PHASE 2 CONFIGURATION - GPT-4o BENCHMARKING

**Date:** November 26, 2025  
**Status:** ✅ **CONFIGURED AND READY**

---

## 📋 CHANGES SUMMARY

### ✅ 1. Subject Model Configuration

**Changed from:**
```python
# PHASE 1: Local Llama 3
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "llama3:latest"
LOCAL_API_KEY = "ollama"
```

**Changed to:**
```python
# PHASE 2: GPT-4o as Subject Model
LOCAL_BASE_URL = "https://api.openai.com/v1"
LOCAL_MODEL = "gpt-4o"
LOCAL_API_KEY = os.environ.get("OPENAI_API_KEY")
```

**Location:** Lines 43-51 in `run_audit.py`

---

### ✅ 2. Output Filenames

To avoid overwriting Phase 1 (Llama 3) results:

| File Type | Phase 1 (Llama 3) | Phase 2 (GPT-4o) |
|-----------|-------------------|------------------|
| Excel | `results.xlsx` | `results_gpt4o.xlsx` |
| JSONL | `audit_log.jsonl` | `audit_log_gpt4o.jsonl` |
| Markdown | `audit_log.md` | `audit_log_gpt4o.md` |

**Logic:** Lines 1224-1233 in `run_audit.py`
```python
if DRY_RUN_MODE:
    suffix = '_dry'
elif LOCAL_MODEL == "gpt-4o":
    suffix = '_gpt4o'
else:
    suffix = ''  # For llama3 or other models
```

---

### ✅ 3. Startup Message

Added model identification at startup:

```
================================================================================
🚀 EED AUDIT PILOT - COGNITIVE AUDIT OF LLM
================================================================================
📊 Running experiment on model: gpt-4o
================================================================================
```

**Location:** Lines 1165-1169 in `run_audit.py`

---

### ✅ 4. API Client Optimization

Since both Subject and Judge are now using GPT-4o:

**Before:**
- Subject: Separate client
- Judge: Separate client

**After (Phase 2):**
- Both: Shared OpenAI client (more efficient)

```python
if LOCAL_MODEL == "gpt-4o":
    judge_client = subject_client  # Reuse same client
    print(f"✅ Subject and Judge both using {LOCAL_MODEL}")
```

**Location:** Lines 1218-1220 in `run_audit.py`

---

### ✅ 5. Connection Check Updated

Updated `check_local_connection()` to handle both:
- **Ollama (local):** Check service, list models, auto-pull if needed
- **OpenAI API:** Check API key, test connection

**Detection logic:**
```python
is_ollama = "localhost" in LOCAL_BASE_URL or "127.0.0.1" in LOCAL_BASE_URL
```

**Location:** Lines 228-308 in `run_audit.py`

---

## 🔍 VERIFICATION

### Dry Run Test ✅

```bash
$ python run_audit.py --dry-run

🧪 DRY RUN MODE ACTIVATED
================================================================================
🚀 EED AUDIT PILOT - COGNITIVE AUDIT OF LLM
================================================================================
📊 Running experiment on model: gpt-4o
================================================================================

🔌 Initializing API clients...
🔍 [DRY RUN] Skipping connection check
✅ [DRY RUN] Judge model (gpt-4o) mock initialized

📝 Output files initialized:
   - results_dry.xlsx
   - audit_log_dry.jsonl
   - audit_log_dry.md

📤 [DRY RUN] PROMPT TO gpt-4o
[SYSTEM]: You are an AI assistant acting as a political-media fact-checker...
```

**Status:** ✅ All prompts correctly routed to `gpt-4o`

---

## 🎯 PHASE 2 EXECUTION PLAN

### Prerequisites:

1. ✅ **API Key Set:**
   ```bash
   export OPENAI_API_KEY="sk-your-key"
   ```

2. ✅ **Phase 1 Results Backed Up:**
   - `results.xlsx` (Llama 3 results preserved)
   - `audit_log.jsonl`
   - `audit_log.md`

### Run Phase 2:

```bash
cd /home/alex/projects/research/EED_Audit_Pilot
source venv/bin/activate
python run_audit.py
```

### Expected Output:

```
📊 Running experiment on model: gpt-4o

✅ Successfully connected to gpt-4o at https://api.openai.com/v1
✅ Subject and Judge both using gpt-4o

📝 Output files initialized:
   - results_gpt4o.xlsx
   - audit_log_gpt4o.jsonl
   - audit_log_gpt4o.md
```

---

## 💰 COST ESTIMATE

### Phase 1 (Llama 3 - Local):
- **Subject Model:** FREE (local Docker)
- **Judge Model:** 3× GPT-4o calls ≈ $0.03
- **Total:** ~$0.03

### Phase 2 (GPT-4o - OpenAI API):
- **Subject Model:** 15× GPT-4o calls ≈ $0.15
- **Judge Model:** 3× GPT-4o calls ≈ $0.03
- **Total:** ~$0.18

**Note:** Actual cost depends on token usage. These are estimates based on Phase 1 token counts.

---

## 📊 COMPARISON STRUCTURE

After Phase 2 completes, you'll have:

### Phase 1 Results (Llama 3):
```
results.xlsx          - 9 rows (3 topics × 3 statements)
audit_log.jsonl       - 3 JSON objects
audit_log.md          - Qualitative report
```

**Key Metrics:**
- DQI: 2 (Medium)
- Autorevision (A): 2 (Honest)
- Retention (R): 1 (Maintained)
- Avg Brier: 0.0139

### Phase 2 Results (GPT-4o):
```
results_gpt4o.xlsx          - 9 rows (3 topics × 3 statements)
audit_log_gpt4o.jsonl       - 3 JSON objects
audit_log_gpt4o.md          - Qualitative report
```

**Metrics:** (TBD after run)
- DQI: ?
- Autorevision (A): ?
- Retention (R): ?
- Avg Brier: ?

---

## 🔬 SCIENTIFIC COMPARISON

### Variables to Compare:

| Metric | Llama 3 | GPT-4o | Better? |
|--------|---------|--------|---------|
| **Factuality (F)** | TBD | TBD | - |
| **DQI Score** | 2 | TBD | - |
| **Source Citations** | 1 | TBD | - |
| **Calibration (Brier)** | 0.0139 | TBD | - |
| **Autorevision (A)** | 2 | TBD | - |
| **Retention (R)** | 1 | TBD | - |
| **Q_pol** | TBD | TBD | - |

### Analysis Questions:

1. Does GPT-4o show better **factual accuracy** (F)?
2. Does GPT-4o produce **higher quality commentary** (DQI)?
3. Is GPT-4o **better calibrated** (lower Brier score)?
4. Does GPT-4o show **better epistemic humility** (autorevision A)?
5. Does GPT-4o have **better retention** of corrections (R)?

---

## ⚠️ IMPORTANT NOTES

### Phase 1 Configuration (Commented Out):

The Llama 3 configuration is preserved but commented out:

```python
# ============================================================================
# PHASE 1: Local Llama 3 via Ollama (COMMENTED OUT FOR PHASE 2)
# ============================================================================
# LOCAL_BASE_URL = "http://localhost:12434/v1"
# LOCAL_MODEL = "llama3:latest"
# LOCAL_API_KEY = "ollama"
```

**To revert to Phase 1:**
1. Comment out GPT-4o configuration
2. Uncomment Llama 3 configuration
3. Run script (will generate `results.xlsx` again)

### File Safety:

✅ **Phase 1 files are safe** - Different suffix prevents overwriting  
✅ **Interrupt-safe** - Saves after each topic  
✅ **Restart-safe** - Loads existing `results_gpt4o.xlsx` if present

---

## 🚀 READY TO RUN

**Status:** ✅ **CONFIGURATION COMPLETE**

All changes applied:
1. ✅ Subject model switched to GPT-4o
2. ✅ Output filenames updated (_gpt4o suffix)
3. ✅ Startup message shows model
4. ✅ API client optimized
5. ✅ Connection check updated

**Next Command:**
```bash
python run_audit.py
```

**Expected Duration:** ~30-60 seconds (3 topics)

---

## 📁 FILES MODIFIED

1. **`run_audit.py`** (1,306 lines)
   - Configuration section (lines 43-56)
   - Output file logic (lines 1224-1233)
   - Startup message (lines 1165-1169)
   - API client setup (lines 1191-1233)
   - Connection check (lines 228-308)

2. **`PHASE2_CONFIGURATION.md`** (this file)
   - Documentation of all changes

---

**Ready for Phase 2 execution!** 🚀

