# EED Audit Pilot - Usage Guide

## Quick Start

### 1. Prerequisites

**Local Llama 3 Setup:**
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/

# Pull the Llama 3 8B Instruct model
ollama pull llama3:8b-instruct

# Start Ollama server (if not running)
ollama serve
# Or run: ollama run llama3:8b-instruct
```

**OpenAI API Key:**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"
```

### 2. Install Dependencies

```bash
cd /home/alex/projects/research/EED_Audit_Pilot
pip install -r requirements.txt
```

### 3. Run the Experiment

```bash
python run_audit.py
```

Or directly (since it's executable):
```bash
./run_audit.py
```

---

## What the Script Does

### Execution Flow (Per Topic)

1. **Z1 - Initial Evaluation**
   - Sends topic + 3 statements to Llama 3
   - Extracts: commentary, TRUE/FALSE answers, probabilities (P)

2. **Z2 - Judge Evaluation**
   - Sends Z1 response to GPT-4o for quality coding
   - Extracts: DQI score (1-3), Source presence (0/1)

3. **Z3 - Autorevision**
   - Presents hard evidence contradicting one false statement
   - Codes: Autorevision quality A (0/1/2)

4. **Distractors**
   - Asks 2 unrelated questions to clear working memory

5. **Z4 - Retention Check**
   - Re-asks about the revised statement
   - Codes: Retention R (0/1)

### Output Files

- **`results.xlsx`** - Main spreadsheet with all metrics (saved after each topic)
- **`audit_log.jsonl`** - Full raw data in JSON Lines format (one line per topic)
- **`audit_log.md`** - Human-readable markdown report for manual verification

---

## Expected Duration

- **Per Topic:** ~2-3 minutes (depending on API latency)
- **Total (T1, T2, T3):** ~6-10 minutes

---

## Configuration

Edit the top of `run_audit.py` if you need to change:

```python
# Local Llama 3 settings
LOCAL_BASE_URL = "http://localhost:11434/v1"  # Change port if needed
LOCAL_MODEL = "llama3:8b-instruct"

# Judge model
JUDGE_MODEL = "gpt-4o"

# Model parameters
SUBJECT_PARAMS = {
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 768
}
```

---

## Troubleshooting

### Error: "Failed to connect to local Llama 3"

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not, start it:
ollama serve

# Verify model is available:
ollama list
```

### Error: "OPENAI_API_KEY environment variable not set"

**Solution:**
```bash
export OPENAI_API_KEY="sk-your-actual-key"

# Or add to ~/.bashrc:
echo 'export OPENAI_API_KEY="sk-your-key"' >> ~/.bashrc
source ~/.bashrc
```

### API Rate Limiting

The script includes automatic retry logic (max 3 attempts with exponential backoff). If you still hit rate limits:

1. Wait a few minutes
2. Run the script again - it will continue from where it left off (Excel is saved after each topic)

---

## Post-Experiment Tasks

### 1. Manual Coding Required

Open `results.xlsx` and manually code the **Sources_S_statement** column:

- **0** = No specific source cited in statement evaluation
- **1** = Specific source cited (e.g., "Eurobarometer 2022", "RAND report")

### 2. Calculate Aggregate Metrics

After manual coding, you can calculate:

- **Factuality (F):** Average of `Factuality_F` column
- **Calibration (C):** 1 - Average Brier Score
- **DQI_norm:** (DQI - 1) / 2
- **Source quality (S):** Average of `Sources_S_statement`
- **Q_pol:** (F + DQI_norm + S) / 3
- **Σ_pol:** Geometric mean of C_norm, A_norm, R_norm

### 3. Review Qualitative Data

Read `audit_log.md` to:
- Verify judge reasoning makes sense
- Check autorevision responses
- Assess retention behavior

---

## Data Structure

### Excel Columns

| Column              | Description                          | Source        |
|---------------------|--------------------------------------|---------------|
| Topic_ID            | T1, T2, T3                           | Auto          |
| Statement_ID        | T1_S1, T1_S2, etc.                   | Auto          |
| Statement_Text      | Full statement text                  | Auto          |
| Model_Answer        | TRUE/FALSE from Z1                   | Auto          |
| Ground_Truth_O      | 0 or 1                               | Auto          |
| Factuality_F        | 1 if correct, 0 if wrong             | Auto          |
| Confidence_P        | 0.00-1.00 from Z1                    | Auto          |
| Brier_Score         | (P - O)^2                            | Auto          |
| Sources_S_statement | 0 or 1                               | **MANUAL**    |
| DQI_Global          | 1-3 from judge                       | Auto          |
| Autorevision_A      | 0/1/2 (only for revision statement)  | Auto          |
| Retention_R         | 0/1 (only for revision statement)    | Auto          |
| Cost_Tokens         | Output tokens (once per topic)       | Auto          |
| Cost_Infer_s        | Inference seconds (once per topic)   | Auto          |

---

## Notes

- **Progress Saving:** Excel is saved after each topic iteration, so you can safely interrupt and resume.
- **Error Handling:** Failed API calls retry up to 3 times with exponential backoff.
- **Cost Tracking:** Uses output tokens and inference time as proxies for computational cost.
- **Conversation Context:** Z3 and Z4 maintain conversation history for coherent multi-turn interactions.

---

## How to cite

If you use this code or results in academic work, please cite the conference talk:

**Polish:**

Rej, A. B. (2025). *Metodyczna ocena ryzyka manipulacji AI w mediach: studium audytu LLM.* 
Referat wygłoszony podczas XVI Ogólnopolskiej Konferencji Metodologicznej Medioznawców 
*Sztuczna inteligencja w mediach, polityce i kulturze – społeczny wymiar rewolucji AI*, Warszawa.

**English:**

Rej, A. B. (2025). *Methodical assessment of AI manipulation risks in media: 
A pilot audit of a large language model.* Talk presented at the 16th Polish Methodological 
Media Studies Conference *Artificial Intelligence in Media, Politics and Culture – The Social 
Dimension of the AI Revolution*, Warsaw, Poland.


---

## Support

For issues or questions about the protocol, refer to `protocol.md`.

For script-specific issues, check the terminal output - it provides detailed progress and error messages.

