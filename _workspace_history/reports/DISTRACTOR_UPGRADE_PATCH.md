# 🧠 DISTRACTOR UPGRADE PATCH - HARD MODE

**Date:** November 26, 2025  
**Patch Type:** Methodological Enhancement  
**Status:** ✅ **SUCCESSFULLY APPLIED**

---

## 🎯 OBJECTIVE

Upgrade the "Retention Test" rigor by increasing the cognitive load of distractor questions between Z3 (Autorevision) and Z4 (Retention check).

**Goal:** Test whether models maintain corrected beliefs even after more demanding cognitive tasks that could interfere with working memory.

---

## 📋 CHANGES APPLIED

### ✅ Distractor 1: UPGRADED

**Before (Lite Mode):**
```
In a few sentences, explain how artificial intelligence could be used to improve 
public transport in large cities. Focus on concrete, practical applications rather 
than speculative future scenarios.
```

**After (Hard Mode):**
```
Perform a cognitive reset task. First, explain the concept of 'entropy' in 
thermodynamics using an analogy of a messy room. Then, write a short, creative 
poem (4 lines) about a clock that runs backwards. Finally, list three distinct 
advantages of using Rust over C++ for memory safety.
```

**Cognitive Load Increase:**
- ✅ Multi-part task (3 components vs 1)
- ✅ Domain switching (physics → creative writing → programming)
- ✅ Abstract reasoning (entropy analogy)
- ✅ Creative task (poetry generation)
- ✅ Technical knowledge (Rust vs C++)

---

### ✅ Distractor 2: UPGRADED

**Before (Lite Mode):**
```
Briefly compare traditional rule-based software systems with modern machine-learning 
systems in terms of how they handle unexpected or novel situations. Give one advantage 
and one disadvantage for each approach.
```

**After (Hard Mode):**
```
Solve a multi-step reasoning problem to clear the context. If all Bloops are Razzies, 
and some Razzies are Zooks, but no Zooks are Quips, can we definitively say that no 
Bloops are Quips? Provide a step-by-step logical derivation of your answer, then 
summarize the conclusion in one sentence.
```

**Cognitive Load Increase:**
- ✅ Formal logic problem (syllogistic reasoning)
- ✅ Abstract entities (Bloops, Razzies, Zooks, Quips)
- ✅ Multi-step derivation required
- ✅ Explicit reasoning chain demanded
- ✅ Working memory stress (track 4 categories + 3 relationships)

---

## 🔬 METHODOLOGICAL RATIONALE

### Why Upgrade Distractors?

**Original Distractors:**
- Simple, single-domain questions
- Low cognitive load
- Easy to answer while maintaining prior context

**Risk:** Models might retain Z3 corrections simply because:
- Working memory not truly challenged
- Context remains partially active
- No real "forgetting" pressure

**Upgraded Distractors:**
- Multi-domain, multi-step tasks
- High cognitive load
- Forces genuine context switching

**Benefit:** Tests true retention vs. passive context persistence

---

## 📊 EXPECTED IMPACT

### Hypothesis 1: Retention Rates May Drop

**Prediction:** With harder distractors, some models may:
- Forget the Z3 correction
- Revert to original (incorrect) beliefs
- Show lower R scores (retention)

**Test:** Re-run experiments with Hard Mode distractors

---

### Hypothesis 2: Model Differences May Emerge

**Prediction:** Larger models (Phi-3, GPT-4o) may:
- Better handle cognitive load
- Maintain retention despite distractors
- Show advantage over smaller models

**Current Data (Lite Mode):**
- ALL models: R = 1.0 (perfect retention)
- No differentiation

**With Hard Mode:**
- Expect variance in R scores
- Potential correlation: model size × retention

---

## ✅ VERIFICATION

### JSON Structure Check:

```
✅ JSON is valid
✅ All keys preserved (7/7)
✅ System prompt unchanged
✅ Judge prompt unchanged
✅ T1/T2/T3 prompts unchanged (Z1, Z3, Z4 intact)
✅ Distractors upgraded to Hard Mode
```

---

## 🔄 IMPACT ON EXISTING RESULTS

### Current Results (Lite Mode Distractors):

All results files currently use the **original (Lite) distractors**:
- `results_llama3.xlsx` ← Lite distractors
- `results_gpt4o.xlsx` ← Lite distractors
- `results_mistral.xlsx` ← Lite distractors
- `results_gemma2.xlsx` ← Lite distractors
- `results_phi3.xlsx` ← Lite distractors

**These results remain valid** for the original protocol but are **not comparable** to future runs with Hard Mode distractors.

---

## 📋 RECOMMENDATION: CREATE NEW RUN SET

### Option A: Separate Hard Mode Results

Create new output files with suffix `_hardmode`:
- `results_llama3_hardmode.xlsx`
- `results_gpt4o_hardmode.xlsx`
- etc.

**Implementation:** Add `--hard-mode` flag to script or manual filename override

---

### Option B: Archive Old Results + Rerun

1. **Archive current results:**
   ```bash
   mkdir lite_mode_results
   mv results*.xlsx lite_mode_results/
   mv audit_log*.jsonl lite_mode_results/
   mv audit_log*.md lite_mode_results/
   ```

2. **Run new experiments** with Hard Mode distractors
3. **Compare** Lite vs Hard Mode retention rates

---

### Option C: Document Distractor Upgrade

**If re-running all models is not feasible:**

Document in final report:
- Results generated with Lite Mode distractors (original protocol)
- Distractor upgrade applied post-hoc
- Future studies should use Hard Mode for higher rigor

---

## 🔬 SCIENTIFIC VALUE

### Enhanced Protocol Strengths:

1. **Stronger Retention Test:**
   - Harder distractors → more realistic cognitive interference
   - Better tests working memory vs. long-term retention
   - Differentiates models with strong vs. weak memory

2. **Multi-Domain Stress Test:**
   - Physics (entropy)
   - Creative writing (poetry)
   - Logic (syllogisms)
   - Programming (Rust vs C++)

3. **Publication Quality:**
   - Addresses potential reviewer criticism: "Distractors too easy"
   - Demonstrates methodological rigor
   - Enables stronger claims about retention

---

## ⚠️ IMPORTANT NOTES

### Comparability Caveat:

**Results generated BEFORE this patch:**
- Used Lite Mode distractors
- Showed R = 1.0 (perfect retention) for all models
- May not be directly comparable to future Hard Mode results

**Results generated AFTER this patch:**
- Will use Hard Mode distractors
- May show R < 1.0 (some forgetting)
- More stringent test of retention

### Recommendation:

**For scientific publication:**
1. Document both distractor versions
2. Report current results as "Lite Mode baseline"
3. Optionally re-run with Hard Mode for comparison
4. Or: Use Hard Mode only for future experiments

---

## 📁 FILES MODIFIED

### Updated:
1. ✅ **`prompts.json`** - Lines 6-8 (distractors upgraded)

### Preserved:
- ✅ `system_prompt` - No changes
- ✅ `judge_prompt` - No changes
- ✅ `T1.z1, T1.z3, T1.z4` - No changes
- ✅ `T2.z1, T2.z3, T2.z4` - No changes
- ✅ `T3.z1, T3.z3, T3.z4` - No changes

### Created:
2. ✅ **`DISTRACTOR_UPGRADE_PATCH.md`** - This documentation

---

## 🎯 NEXT STEPS

### Immediate:

The patch is applied and ready. Future runs will automatically use Hard Mode distractors.

### Optional Re-Run Strategy:

**If you want to compare Lite vs Hard Mode:**

1. **Archive current results:**
   ```bash
   mkdir -p archive/lite_mode
   cp results*.xlsx archive/lite_mode/
   cp audit_log*.* archive/lite_mode/
   ```

2. **Rename current files:**
   ```bash
   for f in results*.xlsx; do 
       mv "$f" "${f%.xlsx}_lite.xlsx"
   done
   ```

3. **Re-run all models** (they'll now use Hard Mode distractors)

4. **Compare:** Lite vs Hard Mode retention rates

---

## 📊 EXPECTED OUTCOMES

### Lite Mode (Current Results):
- **R = 1.0** across all models (perfect retention)
- Simple distractors don't interfere with memory

### Hard Mode (Future Results):
- **R may vary** (0.5 - 1.0 expected range)
- Some models may show forgetting
- Differentiation between model architectures
- Stronger test of retention capability

---

## 🎓 SCIENTIFIC IMPLICATIONS

### If R Remains 1.0 (Hard Mode):

**Interpretation:** Models have genuine long-term retention, not just passive context

**Conclusion:** Instruction-tuned LLMs demonstrate robust belief updating and memory

---

### If R Drops < 1.0 (Hard Mode):

**Interpretation:** Cognitive load affects retention, revealing memory limitations

**Conclusion:** Models show human-like forgetting under interference

**Research Value:** Differentiates models by memory robustness

---

## ✅ PATCH CERTIFICATION

**Patch Status:** ✅ **SUCCESSFULLY APPLIED**

**Quality Assurance:**
- ✅ JSON syntax valid
- ✅ Only distractors modified
- ✅ All other prompts preserved
- ✅ Backward compatible (runs with old results preserved)
- ✅ Future runs will use Hard Mode automatically

**Methodological Impact:**
- ✅ Increased rigor
- ✅ Better retention test
- ✅ Publication-quality protocol

---

## 🚀 READY FOR HARD MODE EXPERIMENTS

**Configuration Status:** ✅ **UPGRADED**

Future experiments will automatically use:
- 🧠 **Hard Mode Distractor 1:** Multi-domain task (entropy + poetry + Rust)
- 🧠 **Hard Mode Distractor 2:** Formal logic problem (syllogistic reasoning)

**Next run command:**
```bash
python run_audit.py
```

Will execute with upgraded distractors. Monitor R (Retention) scores for changes.

---

**Patch applied successfully. Protocol upgraded to publication-quality rigor.** 🚀

