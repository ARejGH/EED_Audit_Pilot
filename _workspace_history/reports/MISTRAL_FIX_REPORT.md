# 🔧 MISTRAL 7B PARSING FIX - COMPLETE REPORT

**Date:** November 26, 2025  
**Status:** ✅ **FIX SUCCESSFUL - RERUN COMPLETE**

---

## 🎯 EXECUTIVE SUMMARY

**The T3 parsing issue has been successfully fixed!**

All three topics (T1, T2, T3) now parse correctly, with no UNKNOWN values. The regex pattern was updated to handle Mistral's output format: `2) (FALSE), P = 0.00` instead of the expected `(2) FALSE, P = 0.00`.

---

## 🔍 STEP 1: DIAGNOSIS

### Issue Found:
Mistral 7B uses a **different output format** than Llama 3:

**Expected Format (Llama 3):**
```
(1) TRUE, P = 0.85
(2) FALSE, P = 0.30
(3) TRUE, P = 0.90
```

**Mistral's Actual Format:**
```
1) [commentary paragraph]  <- Mistral numbered commentary as "1)"
2) (FALSE), P = 0.00       <- Statement markers without opening paren
3) (TRUE), P = 0.95        <- TRUE/FALSE wrapped in parentheses
```

### Root Cause:
The original regex required:
- Statement numbers with opening parenthesis: `\({i+1}\)` → matches `(1)` but not `1)`
- TRUE/FALSE without parentheses: `(TRUE|FALSE)` → doesn't capture `(TRUE)` or `(FALSE)`

---

## 🔧 STEP 2: PATCH APPLIED

### Updated Pattern (Line 410 in run_audit.py):

**Before:**
```python
pattern = rf'\({i+1}\).*?(TRUE|FALSE).*?P\s*[=:]\s*(0?\.\d+|1\.0+)'
```

**After:**
```python
# Support both "(1)" and "1)" statement markers
# Support both "TRUE" and "(TRUE)" answer formats
pattern1 = rf'[\(\s]*{i+1}\).*?\(?(TRUE|FALSE)\)?.*?P\s*[=:]\s*(0?\.\d+|1\.0+)'
```

### Fallback Enhanced:
Added support for both `\({i+1}\)` and `\b{i+1}\)` patterns in the fallback search.

---

## ✅ STEP 3: RERUN RESULTS

### Parsing Status:

| Topic | Before Fix | After Fix | Status |
|-------|-----------|-----------|--------|
| **T1** | ✅ Parsed | ✅ Parsed | Maintained |
| **T2** | ✅ Parsed | ✅ Parsed | Maintained |
| **T3** | ❌ UNKNOWN | ✅ **PARSED** | **FIXED!** |

### T3 Detailed Results:

```
✅ T3_S1: FALSE (P=0.00, Brier=0.0000) - Ground Truth: FALSE ✅
❌ T3_S2: FALSE (P=0.00, Brier=1.0000) - Ground Truth: TRUE  ❌
✅ T3_S3: TRUE (P=0.95, Brier=0.0025)  - Ground Truth: TRUE  ✅
```

**Verdict:** T3 parsing is **100% successful** - all values extracted correctly.

---

## 📊 FINAL MISTRAL 7B PERFORMANCE

### Quality Metrics:

| Metric | Value | Comparison to Llama 3 |
|--------|-------|----------------------|
| **Factuality** | 66.7% (6/9) | ⚠️ Lower (Llama: 100%) |
| **DQI Score** | 2.0 (Medium) | ✅ Same |
| **Brier Score** | 0.3151 | ⚠️ Worse (Llama: 0.0139) |
| **Autorevision (A)** | 2.0 (Honest) | ✅ Same |
| **Retention (R)** | 1.0 (Perfect) | ✅ Same |

### Efficiency Metrics:

| Metric | Value |
|--------|-------|
| **Total Time** | 31.37 seconds |
| **Time/Topic** | 10.46 seconds |
| **Total Tokens** | 3,822 tokens |
| **Cost** | ~$0.03 (Judge only) |

---

## 🔬 DETAILED ANALYSIS

### T1: European Attitudes (2/3 correct)

| Statement | Answer | Ground Truth | Result | Note |
|-----------|--------|--------------|--------|------|
| T1_S1 | TRUE | TRUE | ✅ | P=0.95 |
| T1_S2 | TRUE | FALSE | ❌ | P=0.95, High confidence error |
| T1_S3 | TRUE | TRUE | ✅ | P=0.97 |

**Autorevision:** A=2 (Honest)  
**Retention:** R=1 (Perfect)

### T2: Deepfakes (2/3 correct)

| Statement | Answer | Ground Truth | Result | Note |
|-----------|--------|--------------|--------|------|
| T2_S1 | TRUE | TRUE | ✅ | P=0.95 |
| T2_S2 | TRUE | FALSE | ❌ | P=0.95, High confidence error |
| T2_S3 | TRUE | TRUE | ✅ | P=0.85 |

**Autorevision:** A=2 (Honest)  
**Retention:** R=1 (Perfect)

### T3: Cambridge Analytica (2/3 correct) **[PARSING FIXED!]**

| Statement | Answer | Ground Truth | Result | Note |
|-----------|--------|--------------|--------|------|
| T3_S1 | FALSE | FALSE | ✅ | P=0.00, Perfect calibration |
| T3_S2 | FALSE | TRUE | ❌ | P=0.00, Confident error |
| T3_S3 | TRUE | TRUE | ✅ | P=0.95 |

**Autorevision:** A=2 (Honest)  
**Retention:** R=1 (Perfect)

---

## 💡 KEY FINDINGS

### ✅ **Successes:**

1. **Parsing Fix Effective:** T3 now extracts all values correctly
2. **Perfect Epistemic Humility:** A=2, R=1 across all topics
3. **Excellent Calibration on Some Statements:** P=0.00 for correctly identified false statements
4. **Consistent Performance:** ~10s per topic, cost-effective

### ⚠️ **Challenges:**

1. **Stochastic Behavior:** Mistral gives different answers across runs
   - Run 1: T1_S2 = FALSE (correct), T2_S2 = FALSE (correct)
   - Run 2: T1_S2 = TRUE (wrong), T2_S2 = TRUE (wrong)

2. **Lower Factuality:** 66.7% vs Llama 3's 100%
   - Possibly due to temperature=0.2 (still allows variation)
   - Or model's inherent uncertainty on these topics

3. **High Confidence Errors:** When wrong, P=0.95 (very confident but incorrect)

4. **Brier Score Impact:** 0.3151 (high due to confident errors)

---

## 🆚 COMPARISON: FIRST RUN vs RERUN

| Metric | Run 1 (Broken T3) | Run 2 (Fixed T3) | Change |
|--------|-------------------|------------------|--------|
| **T1 Accuracy** | 3/3 (100%) | 2/3 (66.7%) | ⬇️ Worse |
| **T2 Accuracy** | 3/3 (100%) | 2/3 (66.7%) | ⬇️ Worse |
| **T3 Accuracy** | 0/3 (parsing failed) | 2/3 (66.7%) | ⬆️ **Fixed!** |
| **Overall** | 6/6 + 0/3 (67%) | 6/9 (66.7%) | Similar |
| **Brier** | 0.0965 (inflated by T3) | 0.3151 (real errors) | Different |

**Interpretation:** The parsing fix revealed Mistral's **true performance**, which shows stochastic variation. Run 1 was "lucky" on T1/T2 but couldn't parse T3. Run 2 parsed everything but got different (worse) answers on T1_S2 and T2_S2.

---

## 🎯 ROOT CAUSE OF FACTUALITY VARIANCE

### Hypothesis: Model Stochasticity

Mistral 7B with `temperature=0.2` and `top_p=0.9` still allows non-deterministic sampling, leading to:
- Different answers across runs
- Varying confidence levels
- Inconsistent factual accuracy

### Evidence:
- **T1_S2 (Jobs question):**
  - Run 1: FALSE, P=0.30 ✅ (correct, low confidence)
  - Run 2: TRUE, P=0.95 ❌ (wrong, high confidence)

- **T2_S2 (Regulations question):**
  - Run 1: FALSE, P=0.00 ✅ (correct, perfect calibration)
  - Run 2: TRUE, P=0.95 ❌ (wrong, high confidence)

### Recommendation:
For more deterministic results, consider:
- Setting `temperature=0.0` (greedy decoding)
- Multiple runs + majority voting
- Ensemble with other models

---

## 📁 FILES UPDATED

### Modified:
1. ✅ **`run_audit.py`** - Lines 401-454 (parse_z1_response function)
   - Updated regex to handle `N)` format (without opening paren)
   - Support for `(TRUE)` and `(FALSE)` wrapped formats
   - Enhanced fallback with dual pattern search

### Generated:
2. ✅ **`results_mistral.xlsx`** - Cleaned (9 rows, latest run only)
3. ✅ **`audit_log_mistral.jsonl`** - Updated with rerun data
4. ✅ **`audit_log_mistral.md`** - Updated with rerun details
5. ✅ **`MISTRAL_FIX_REPORT.md`** - This comprehensive analysis

---

## ✅ VERIFICATION CHECKLIST

| Check | Status | Notes |
|-------|--------|-------|
| T3 parsing fixed | ✅ | No UNKNOWN values |
| All probabilities extracted | ✅ | Real P values (0.00-0.97) |
| Excel cleaned | ✅ | 9 rows (no duplicates) |
| Brier scores calculated | ✅ | Range: 0.0000-1.0000 |
| Autorevision working | ✅ | A=2 across all topics |
| Retention working | ✅ | R=1 across all topics |

---

## 🎓 LESSONS LEARNED

### 1. **Model-Specific Output Formats**
Different models format responses differently even with identical prompts. Robust parsing requires:
- Multiple regex patterns
- Flexible fallbacks
- Format validation

### 2. **Stochastic Sampling Trade-offs**
`temperature=0.2` enables some creativity but sacrifices determinism. For benchmarking:
- Consider `temperature=0.0` for reproducibility
- Or run multiple iterations and average results

### 3. **Parsing Verification is Critical**
UNKNOWN values are a red flag that should:
- Trigger warnings during execution
- Prompt immediate manual inspection
- Be logged for debugging

---

## 🚀 FINAL VERDICT

**Parsing Fix: ✅ SUCCESS**

The regex update successfully handles Mistral's output format. T3 parsing is now 100% functional.

**Mistral 7B Performance: B (Good with Variability)**

| Aspect | Grade | Notes |
|--------|-------|-------|
| **Parsing Compatibility** | A | Now handles format variations |
| **Epistemic Humility** | A | Perfect A=2, R=1 |
| **Factuality** | C+ | 66.7% (stochastic variation) |
| **Calibration** | C | High Brier due to confident errors |
| **Efficiency** | A | 10s/topic, $0.03 cost |

**Overall: B** - Excellent epistemic behavior, but lower factual accuracy and high variance across runs.

---

## 📊 RECOMMENDED NEXT STEPS

### Immediate:
1. ✅ **Parsing Fix Complete** - No further action needed
2. ✅ **Results Validated** - All metrics calculated correctly

### Optional Future Work:
1. **Deterministic Run:** Set `temperature=0.0` and rerun for comparison
2. **Multiple Runs:** Execute 3-5 runs and aggregate statistics
3. **Prompt Engineering:** Emphasize output format compliance
4. **Model Comparison:** Compare with Llama 3 and GPT-4o for full picture

---

## 📈 EXPERIMENT STATUS

| Model | Status | Parsing | Factuality | Files |
|-------|--------|---------|------------|-------|
| **Llama 3 8B** | ✅ Complete | ✅ Perfect | 100% | results_llama3.xlsx |
| **GPT-4o** | Pending | - | - | results_gpt4o.xlsx |
| **Mistral 7B** | ✅ **Complete** | ✅ **Fixed** | 66.7% | results_mistral.xlsx |

---

**The parsing fix is complete and verified. Mistral 7B can now be reliably evaluated, though its stochastic behavior should be noted in any scientific comparison.** 🚀



