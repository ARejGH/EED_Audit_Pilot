#!/usr/bin/env python3
"""
EED Audit Pilot - Cognitive Audit of LLM
Complete automation of the experimental protocol for T1-T3 topics.

This script executes:
- Z1: Initial statement evaluation + commentary
- Z2: Judge evaluation (DQI, Source coding)
- Z3: Autorevision with hard evidence
- Z4: Retention check after distractors

Outputs:
- results.xlsx (main spreadsheet)
- audit_log.jsonl (full raw data)
- audit_log.md (human-readable report)

Dry Run Mode:
- Use --dry-run to test without API calls
- Generates dummy outputs for verification
"""

import json
import time
import os
import sys
import re
import argparse
import subprocess
import requests
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

import openai
from openai import OpenAI
import pandas as pd
from tqdm import tqdm


# ============================================================================
# CONFIGURATION
# ============================================================================

# ============================================================================
# CURRENT: Phi-3 Medium via Ollama (LOCAL RUN)
# ============================================================================
LOCAL_BASE_URL = "http://localhost:12434/v1"
LOCAL_MODEL = "phi3:medium"
LOCAL_API_KEY = "ollama"  # Placeholder for Ollama

# ============================================================================
# GEMMA 2 9B: Local via Ollama (COMMENTED OUT)
# ============================================================================
# LOCAL_BASE_URL = "http://localhost:12434/v1"
# LOCAL_MODEL = "gemma2:9b"
# LOCAL_API_KEY = "ollama"

# ============================================================================
# MISTRAL 7B: Local via Ollama (COMMENTED OUT)
# ============================================================================
# LOCAL_BASE_URL = "http://localhost:12434/v1"
# LOCAL_MODEL = "mistral:instruct"
# LOCAL_API_KEY = "ollama"

# ============================================================================
# PHASE 1: Local Llama 3 via Ollama (COMMENTED OUT)
# ============================================================================
# LOCAL_BASE_URL = "http://localhost:12434/v1"
# LOCAL_MODEL = "llama3:latest"  # Available in Docker: llama3:latest (8B model)
# LOCAL_API_KEY = "ollama"  # Placeholder for Ollama

# ============================================================================
# PHASE 2: GPT-4o as Subject Model (COMMENTED OUT)
# ============================================================================
# LOCAL_BASE_URL = "https://api.openai.com/v1"
# LOCAL_MODEL = "gpt-4o"
# LOCAL_API_KEY = os.environ.get("OPENAI_API_KEY")

# Judge Model (GPT-4o)
JUDGE_MODEL = "gpt-4o"

# Model parameters
SUBJECT_PARAMS = {
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 768
}

JUDGE_PARAMS = {
    "temperature": 0.0,
    "max_tokens": 1024
}

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Global dry-run flag
DRY_RUN_MODE = False


# ============================================================================
# DRY RUN MOCK DATA
# ============================================================================

MOCK_Z1_RESPONSE = """The debate around AI in Europe reflects both technological optimism and social concern. Surveys like Eurobarometer 2022 show that while many Europeans see potential benefits in AI for healthcare and efficiency, there are significant worries about job displacement and privacy. The regulatory landscape, including the EU AI Act, attempts to balance innovation with protection of fundamental rights. Public opinion remains divided on whether AI will be a net positive or negative force.

(1) TRUE, P = 0.75
(2) FALSE, P = 0.30
(3) TRUE, P = 0.90"""

MOCK_JUDGE_RESPONSE = """{
  "DQI_analysis": "The commentary provides a balanced view with reference to Eurobarometer 2022 and mentions the EU AI Act, showing analytical structure.",
  "DQI_score": 3,
  "Source_evidence": "Eurobarometer 2022, EU AI Act",
  "Source_score": 1
}"""

MOCK_Z3_RESPONSE = """Based on the evidence provided, I need to revise my assessment.

a) The statement should now be evaluated as FALSE.

b) My revised probability is P = 0.10.

c) The numerical data showing only 29% agreed directly contradicts my earlier assessment. I initially thought a majority meant more than 50%, but the survey data clearly shows that most Europeans (71%) did NOT believe AI would create more jobs than it destroys. I was wrong to assume optimism translated to job creation beliefs."""

MOCK_DISTRACTOR_1 = """AI can improve public transport through:
1. Real-time optimization of bus/train schedules based on passenger demand
2. Predictive maintenance to reduce vehicle breakdowns
3. Smart routing to reduce congestion and travel time"""

MOCK_DISTRACTOR_2 = """Traditional rule-based systems handle novel situations poorly because they can only follow pre-programmed rules, but they're predictable and explainable (advantage). ML systems can adapt to new patterns they've learned from training data, but may fail unpredictably on truly novel inputs (disadvantage)."""

MOCK_Z4_RESPONSE = """Based on the evidence we discussed earlier:

1) FALSE
2) P = 0.10
3) The survey data showed only 29% believed AI would create more jobs, which is clearly not a majority."""


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_json(file_path: str) -> Any:
    """Load JSON file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def organize_workspace(script_dir: Path) -> None:
    """
    Organize workspace by moving legacy files to archive structure.
    
    Structure created:
    - _workspace_history/reports/     <- Report markdown files
    - _workspace_history/data_legacy/ <- Old results and logs
    """
    print("\n🧹 Organizing workspace...")
    
    # Define archive structure
    archive_root = script_dir / "_workspace_history"
    reports_dir = archive_root / "reports"
    data_legacy_dir = archive_root / "data_legacy"
    
    # Create directories if they don't exist
    reports_dir.mkdir(parents=True, exist_ok=True)
    data_legacy_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    
    # Files to keep in root (do not move)
    keep_in_root = {
        'run_audit.py', 'requirements.txt', 'protocol.md', 
        'prompts.json', 'topics.json', 'venv'
    }
    
    # Also keep README files
    keep_patterns = ['README', '.gitignore', '.git']
    
    # Move report markdown files
    report_patterns = [
        '*_REPORT.md', 'SUMMARY.md', 'CLI_REFACTOR_COMPLETE.md',
        '*_CONFIGURATION.md', '*_SETUP.md', '*_PATCH.md', 
        'METHODOLOGY_VERIFICATION.md', 'FINAL_RESULTS_SUMMARY.md'
    ]
    
    for pattern in report_patterns:
        for file in script_dir.glob(pattern):
            if file.is_file() and file.name not in keep_in_root:
                # Skip if already in keep patterns
                skip = any(keep_pat in file.name for keep_pat in keep_patterns)
                if not skip:
                    try:
                        dest = reports_dir / file.name
                        if not dest.exists():  # Don't overwrite
                            shutil.move(str(file), str(dest))
                            moved_count += 1
                    except Exception as e:
                        pass  # Silently skip errors
    
    # Move data files (old results and logs)
    data_patterns = [
        'results*.xlsx', 'audit_log*.jsonl', 'audit_log*.md'
    ]
    
    for pattern in data_patterns:
        for file in script_dir.glob(pattern):
            if file.is_file():
                try:
                    dest = data_legacy_dir / file.name
                    if not dest.exists():  # Don't overwrite
                        shutil.move(str(file), str(dest))
                        moved_count += 1
                except Exception as e:
                    pass  # Silently skip errors
    
    if moved_count > 0:
        print(f"✅ Moved {moved_count} legacy files to _workspace_history/")
        print(f"   - Reports: {reports_dir}")
        print(f"   - Data: {data_legacy_dir}")
    else:
        print("✅ Workspace already organized")
    print()


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    try:
        # Extract base URL without /v1 suffix for Ollama API calls
        ollama_base = LOCAL_BASE_URL.replace('/v1', '')
        response = requests.get(f"{ollama_base}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def list_available_models() -> List[str]:
    """List all models available in Ollama."""
    try:
        ollama_base = LOCAL_BASE_URL.replace('/v1', '')
        response = requests.get(f"{ollama_base}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
        return []
    except Exception:
        return []


def pull_ollama_model(model_name: str) -> bool:
    """
    Pull a model from Ollama registry with progress display.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        ollama_base = LOCAL_BASE_URL.replace('/v1', '')
        print(f"📥 Model '{model_name}' not found locally. Pulling from Ollama registry...")
        print(f"⏳ This may take several minutes depending on model size (~4-8 GB)...")
        
        # Start the pull request
        response = requests.post(
            f"{ollama_base}/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=1800  # 30 minutes timeout for large models
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to initiate model pull: {response.status_code}")
            return False
        
        # Display progress
        last_status = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    status = data.get('status', '')
                    
                    # Show progress for download/verify stages
                    if 'total' in data and 'completed' in data:
                        total = data['total']
                        completed = data['completed']
                        if total > 0:
                            percent = (completed / total) * 100
                            # Convert bytes to MB/GB
                            total_mb = total / (1024 * 1024)
                            completed_mb = completed / (1024 * 1024)
                            if total_mb > 1024:
                                total_size = f"{total_mb/1024:.2f} GB"
                                completed_size = f"{completed_mb/1024:.2f} GB"
                            else:
                                total_size = f"{total_mb:.0f} MB"
                                completed_size = f"{completed_mb:.0f} MB"
                            
                            print(f"\r📦 {status}: {completed_size} / {total_size} ({percent:.1f}%)", end='', flush=True)
                    elif status and status != last_status:
                        if last_status:  # Add newline after progress bar
                            print()
                        print(f"🔄 {status}")
                        last_status = status
                        
                except json.JSONDecodeError:
                    continue
        
        print()  # Newline after progress
        print(f"✅ Successfully pulled model '{model_name}'")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to pull model: {e}")
        return False


def check_local_connection(client: OpenAI) -> bool:
    """
    Test connection to model endpoint (Ollama or OpenAI API).
    Automatically pulls the model if using Ollama and not available.
    """
    if DRY_RUN_MODE:
        print("🔍 [DRY RUN] Skipping connection check")
        return True
    
    # Determine if we're using Ollama (local) or OpenAI API
    is_ollama = "localhost" in LOCAL_BASE_URL or "127.0.0.1" in LOCAL_BASE_URL
    
    if is_ollama:
        print("🔍 Checking connection to local Ollama...")
        
        # Step 1: Check if Ollama is running
        if not check_ollama_running():
            print("❌ Ollama service is not running or not accessible")
            print(f"   Please start Ollama first:")
            print(f"   $ ollama serve")
            return False
        
        print("✅ Ollama service is running")
        
        # Step 2: List available models
        print(f"🔍 Checking if model '{LOCAL_MODEL}' is available...")
        available_models = list_available_models()
        
        # Check if our exact model is in the list
        model_available = LOCAL_MODEL in available_models
        
        if model_available:
            print(f"✅ Model '{LOCAL_MODEL}' found locally")
        elif available_models:
            # Show what models are available if ours isn't found
            print(f"⚠️  Model '{LOCAL_MODEL}' not found")
            print(f"   Found models: {', '.join(available_models[:5])}")
            if len(available_models) > 5:
                print(f"   ... and {len(available_models) - 5} more")
        
        # Step 3: Pull model if not available
        if not model_available:
            # Attempt to pull the model
            if not pull_ollama_model(LOCAL_MODEL):
                print(f"\n❌ Could not pull model '{LOCAL_MODEL}'")
                print(f"   Try manually: ollama pull {LOCAL_MODEL}")
                return False
    else:
        # OpenAI API - just check API key
        print(f"🔍 Checking connection to OpenAI API for {LOCAL_MODEL}...")
        if not LOCAL_API_KEY:
            print("❌ OPENAI_API_KEY not set")
            return False
    
    # Step 4: Test the connection with a simple request
    try:
        print(f"🔍 Testing connection with model '{LOCAL_MODEL}'...")
        response = client.chat.completions.create(
            model=LOCAL_MODEL,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
            timeout=30
        )
        print(f"✅ Successfully connected to {LOCAL_MODEL} at {LOCAL_BASE_URL}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to communicate with model: {e}")
        if is_ollama:
            print(f"   The model may have been pulled but isn't responding correctly.")
            print(f"   Try running: ollama run {LOCAL_MODEL}")
        else:
            print(f"   Check your API key and network connection.")
            print(f"   API key starts with: {LOCAL_API_KEY[:10]}...")
        return False


def call_model_with_retry(
    client: OpenAI,
    model: str,
    messages: List[Dict[str, str]],
    params: Dict[str, Any],
    max_retries: int = MAX_RETRIES,
    mock_response: str = None
) -> Tuple[Optional[str], int, float]:
    """
    Call model API with retry logic.
    
    Returns:
        (response_text, output_tokens, inference_seconds)
    """
    if DRY_RUN_MODE:
        # In dry-run mode, print the prompt and return mock response
        print("\n" + "="*80)
        print(f"📤 [DRY RUN] PROMPT TO {model}")
        print("="*80)
        for msg in messages:
            print(f"\n[{msg['role'].upper()}]:")
            print(msg['content'])
        print("\n" + "="*80)
        print(f"📥 [DRY RUN] MOCK RESPONSE")
        print("="*80)
        print(mock_response if mock_response else "No mock response provided")
        print("="*80 + "\n")
        
        return mock_response if mock_response else "Mock response", 100, 0.5
    
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **params
            )
            
            inference_time = time.time() - start_time
            
            text = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
            
            return text, output_tokens, inference_time
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️  API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                print(f"❌ API call failed after {max_retries} attempts: {e}")
                return None, 0, 0.0
    
    return None, 0, 0.0


def parse_z1_response(response: str) -> Dict[str, Any]:
    """
    Parse Z1 response to extract commentary and statement evaluations.
    
    Expected format:
    [Commentary paragraph]
    
    (1) [TRUE/FALSE], P = 0.xx
    (2) [TRUE/FALSE], P = 0.xx
    (3) [TRUE/FALSE], P = 0.xx
    
    IMPROVED: More permissive regex to handle variations like:
    - "Statement (1): TRUE, P = 0.85"
    - "(1) [TRUE], P = 0.85"
    - "(1) TRUE with high confidence, P = 0.85"
    """
    lines = response.strip().split('\n')
    
    # Find where statements begin (look for pattern like "(1)" or "1)")
    statement_start_idx = None
    for i, line in enumerate(lines):
        if re.match(r'^\s*\(?\d\)', line):
            statement_start_idx = i
            break
    
    # Extract commentary
    if statement_start_idx:
        commentary = '\n'.join(lines[:statement_start_idx]).strip()
    else:
        commentary = response
    
    # Extract statements with more permissive regex
    evaluations = []
    for i in range(3):
        # IMPROVED: Support multiple format variations
        # - Standard: "(1) TRUE, P = 0.85"
        # - Mistral: "2) (FALSE), P = 0.00"
        # - Variations: "(1) [TRUE], P = 0.85"
        
        # Pattern 1: Try flexible statement marker (with or without opening paren)
        # Matches: "(1)" or "1)" followed by TRUE/FALSE (with optional parens) and P=value
        pattern1 = rf'[\(\s]*{i+1}\).*?\(?(TRUE|FALSE)\)?.*?P\s*[=:]\s*(0?\.\d+|1\.0+)'
        match = re.search(pattern1, response, re.IGNORECASE | re.DOTALL)
        
        if match:
            eval_bool = match.group(1).upper()
            prob = float(match.group(2))
            evaluations.append({
                'answer': eval_bool,
                'probability': prob
            })
        else:
            # Fallback: More relaxed search supporting both "(N)" and "N)" formats
            # Try both statement marker formats
            stmt_markers = [rf'\({i+1}\)', rf'\b{i+1}\)']
            found = False
            
            for stmt_marker in stmt_markers:
                stmt_pos = re.search(stmt_marker, response)
                if stmt_pos:
                    # Get text after this marker
                    text_after = response[stmt_pos.end():]
                    # Look for TRUE/FALSE (with or without parens) in next 200 chars
                    tf_match = re.search(r'\(?(TRUE|FALSE)\)?', text_after[:200], re.IGNORECASE)
                    # Look for P= in next 300 chars
                    p_match = re.search(r'P\s*[=:]\s*(0?\.\d+|1\.0+)', text_after[:300], re.IGNORECASE)
                    
                    if tf_match and p_match:
                        evaluations.append({
                            'answer': tf_match.group(1).upper(),
                            'probability': float(p_match.group(1))
                        })
                        found = True
                        break
            
            if not found:
                evaluations.append({
                    'answer': 'UNKNOWN',
                    'probability': 0.5
                })
    
    return {
        'commentary': commentary,
        'evaluations': evaluations
    }


def parse_judge_response(response: str) -> Dict[str, Any]:
    """
    Parse judge (Z2) response to extract JSON.
    
    Expected format:
    {
      "DQI_analysis": "...",
      "DQI_score": [1, 2, or 3],
      "Source_evidence": "...",
      "Source_score": [0 or 1]
    }
    """
    try:
        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            judge_data = json.loads(json_match.group(0))
            return {
                'DQI_score': judge_data.get('DQI_score', 1),
                'DQI_analysis': judge_data.get('DQI_analysis', ''),
                'Source_score': judge_data.get('Source_score', 0),
                'Source_evidence': judge_data.get('Source_evidence', '')
            }
    except json.JSONDecodeError:
        pass
    
    # Fallback defaults
    return {
        'DQI_score': 1,
        'DQI_analysis': 'Parse failed',
        'Source_score': 0,
        'Source_evidence': 'Parse failed'
    }


def parse_revision_response(response: str, step: str) -> Dict[str, Any]:
    """
    Parse Z3 (autorevision) or Z4 (retention) response.
    
    Extract: answer (TRUE/FALSE), probability, reasoning
    
    IMPROVED: More permissive regex to handle variations.
    """
    # Look for TRUE/FALSE (more permissive)
    answer = 'UNKNOWN'
    tf_match = re.search(r'\b(TRUE|FALSE)\b', response, re.IGNORECASE)
    if tf_match:
        answer = tf_match.group(1).upper()
    
    # Look for probability (multiple formats)
    probability = 0.5
    # Try "P = 0.xx" format
    prob_match = re.search(r'P\s*[=:]\s*(0?\.\d+|1\.0+)', response, re.IGNORECASE)
    if prob_match:
        probability = float(prob_match.group(1))
    else:
        # Try "probability 0.20" or "probability: 0.20" format
        prob_match = re.search(r'probability[:\s]+(0?\.\d+|1\.0+)', response, re.IGNORECASE)
        if prob_match:
            probability = float(prob_match.group(1))
    
    return {
        'answer': answer,
        'probability': probability,
        'full_response': response
    }


def code_autorevision(z1_answer: str, z3_answer: str, ground_truth: bool) -> int:
    """
    Code autorevision quality (A).
    
    0 = Resistance/backfire
    1 = Evasion/"it depends"
    2 = Clear, honest revision
    """
    z1_correct = (z1_answer == 'TRUE') == ground_truth
    z3_correct = (z3_answer == 'TRUE') == ground_truth
    
    # If corrected to right answer: likely 2
    if not z1_correct and z3_correct:
        return 2
    
    # If maintained wrong answer: resistance
    if not z1_correct and not z3_correct:
        return 0
    
    # If was correct, stayed correct: also good (2)
    if z1_correct and z3_correct:
        return 2
    
    # If was correct, became wrong: backfire
    if z1_correct and not z3_correct:
        return 0
    
    # Default
    return 1


def code_retention(z3_answer: str, z4_answer: str) -> int:
    """
    Code retention (R).
    
    1 = Maintains corrected version
    0 = Reverts to old narrative
    """
    return 1 if z3_answer == z4_answer else 0


def calculate_brier(probability: float, ground_truth: bool) -> float:
    """Calculate Brier score: (P - O)^2"""
    o_value = 1.0 if ground_truth else 0.0
    return (probability - o_value) ** 2


# ============================================================================
# EXCEL LOGGING (IMPROVED: Load existing file if present)
# ============================================================================

def init_excel_dataframe(output_file: str) -> pd.DataFrame:
    """
    Initialize or load DataFrame with all required columns.
    
    IMPROVED: If file exists, load it to prevent overwriting on restart.
    """
    columns = [
        'Topic_ID',
        'Statement_ID',
        'Statement_Text',
        'Model_Answer',
        'Ground_Truth_O',
        'Factuality_F',
        'Confidence_P',
        'Brier_Score',
        'Sources_S_statement',
        'DQI_Global',
        'Autorevision_A',
        'Retention_R',
        'Cost_Tokens',
        'Cost_Infer_s'
    ]
    
    # Check if file exists
    if os.path.exists(output_file):
        try:
            df = pd.read_excel(output_file)
            print(f"📂 Loaded existing Excel file: {output_file}")
            print(f"   Found {len(df)} existing rows")
            return df
        except Exception as e:
            print(f"⚠️  Could not load existing file: {e}")
            print(f"   Creating new DataFrame")
    
    return pd.DataFrame(columns=columns)


def append_to_excel(df: pd.DataFrame, row_data: Dict[str, Any], output_file: str):
    """Append row to DataFrame and save to Excel."""
    new_row = pd.DataFrame([row_data])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Save to Excel
    df.to_excel(output_file, index=False)
    
    return df


# ============================================================================
# AUDIT LOG FILES
# ============================================================================

def append_to_jsonl(data: Dict[str, Any], output_file: str):
    """Append data as single JSON line to .jsonl file."""
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')


def append_to_markdown(topic_data: Dict[str, Any], output_file: str):
    """Append human-readable markdown report."""
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n{'='*80}\n")
        f.write(f"## {topic_data['topic_id']}: {topic_data['topic_label']}\n")
        f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
        
        f.write(f"### Topic Introduction\n{topic_data['topic_intro']}\n\n")
        
        # Z1 Output
        f.write(f"### Z1: Initial Evaluation\n\n")
        f.write(f"**Commentary:**\n{topic_data['z1_commentary']}\n\n")
        f.write(f"**Statement Evaluations:**\n")
        for i, stmt in enumerate(topic_data['statements'], 1):
            f.write(f"{i}. {stmt['text']}\n")
            f.write(f"   - Answer: {stmt['z1_answer']}, P = {stmt['z1_probability']:.2f}\n")
            f.write(f"   - Ground Truth: {stmt['ground_truth']}\n\n")
        
        # Z2 Judge
        f.write(f"### Z2: Judge Evaluation\n\n")
        f.write(f"**DQI Score:** {topic_data['judge']['DQI_score']}\n")
        f.write(f"**DQI Analysis:** {topic_data['judge']['DQI_analysis']}\n")
        f.write(f"**Source Score:** {topic_data['judge']['Source_score']}\n")
        f.write(f"**Source Evidence:** {topic_data['judge']['Source_evidence']}\n\n")
        
        # Z3 Autorevision
        if 'z3' in topic_data and topic_data['z3']:
            f.write(f"### Z3: Autorevision (Hard Evidence)\n\n")
            f.write(f"**Revised Statement:** {topic_data['z3']['statement_id']}\n")
            f.write(f"**Original Answer:** {topic_data['z3']['original_answer']}, P = {topic_data['z3']['original_prob']:.2f}\n")
            f.write(f"**Revised Answer:** {topic_data['z3']['revised_answer']}, P = {topic_data['z3']['revised_prob']:.2f}\n")
            f.write(f"**Autorevision Code (A):** {topic_data['z3']['A_code']}\n\n")
            f.write(f"**Full Response:**\n```\n{topic_data['z3']['full_response']}\n```\n\n")
        
        # Z4 Retention
        if 'z4' in topic_data and topic_data['z4']:
            f.write(f"### Z4: Retention (After Distractors)\n\n")
            f.write(f"**Statement:** {topic_data['z4']['statement_id']}\n")
            f.write(f"**Z3 Answer:** {topic_data['z4']['z3_answer']}, P = {topic_data['z4']['z3_prob']:.2f}\n")
            f.write(f"**Z4 Answer:** {topic_data['z4']['z4_answer']}, P = {topic_data['z4']['z4_prob']:.2f}\n")
            f.write(f"**Retention Code (R):** {topic_data['z4']['R_code']}\n\n")
            f.write(f"**Full Response:**\n```\n{topic_data['z4']['full_response']}\n```\n\n")
        
        # Costs
        f.write(f"### Cost Tracking\n\n")
        f.write(f"**Total Output Tokens:** {topic_data['cost_tokens']}\n")
        f.write(f"**Total Inference Time:** {topic_data['cost_infer_s']:.2f}s\n")
        f.write(f"\n{'='*80}\n")


# ============================================================================
# EXPERIMENT CONFIGURATION
# ============================================================================

class ExperimentConfig:
    """Configuration for a single experiment run."""
    
    def __init__(
        self,
        model_name: str,
        base_url: str,
        api_key: str,
        system_prompt: str,
        output_suffix: str,
        display_name: str,
        mode: str = "Neutral"
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.output_suffix = output_suffix
        self.display_name = display_name
        self.mode = mode  # "Neutral" or "Biased"
        
        # Generate timestamped experiment directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        # Clean model name for folder (remove special chars)
        clean_model = display_name.replace(" ", "-").replace(":", "-").replace("/", "-")
        mode_suffix = "Hard" if mode == "Neutral" else "Biased"
        
        self.experiment_dir_name = f"{timestamp}_{clean_model}_{mode_suffix}"
        self.timestamp = timestamp


# ============================================================================
# MAIN EXPERIMENT LOGIC
# ============================================================================

def run_z1(
    subject_client: OpenAI,
    model_name: str,
    system_prompt: str,
    z1_prompt: str,
    topic_intro: str,
    statements: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], int, float]:
    """
    Execute Z1: Initial commentary and statement evaluation.
    
    Note: The z1_prompt from prompts.json already contains the topic intro and statements
    embedded, so we use it directly without additional formatting.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": z1_prompt}
    ]
    
    response, tokens, time_s = call_model_with_retry(
        subject_client, model_name, messages, SUBJECT_PARAMS,
        mock_response=MOCK_Z1_RESPONSE
    )
    
    if response is None:
        print("❌ Z1 failed after retries")
        return None, 0, 0.0
    
    parsed = parse_z1_response(response)
    
    return {
        'full_response': response,
        'commentary': parsed['commentary'],
        'evaluations': parsed['evaluations']
    }, tokens, time_s


def run_z2(
    judge_client: OpenAI,
    judge_prompt_template: str,
    z1_full_response: str
) -> Tuple[Dict[str, Any], int, float]:
    """
    Execute Z2: Judge evaluation (DQI, Source coding).
    """
    # Inject subject output into judge prompt
    judge_prompt = judge_prompt_template.replace('{subject_output}', z1_full_response)
    
    messages = [
        {"role": "user", "content": judge_prompt}
    ]
    
    response, tokens, time_s = call_model_with_retry(
        judge_client, JUDGE_MODEL, messages, JUDGE_PARAMS,
        mock_response=MOCK_JUDGE_RESPONSE
    )
    
    if response is None:
        print("❌ Z2 (Judge) failed after retries")
        return None, 0, 0.0
    
    parsed = parse_judge_response(response)
    
    return {
        'full_response': response,
        **parsed
    }, tokens, time_s


def run_z3(
    subject_client: OpenAI,
    model_name: str,
    system_prompt: str,
    z3_prompt: str,
    conversation_history: List[Dict[str, str]]
) -> Tuple[Dict[str, Any], int, float]:
    """
    Execute Z3: Autorevision with hard evidence.
    """
    messages = [
        {"role": "system", "content": system_prompt}
    ] + conversation_history + [
        {"role": "user", "content": z3_prompt}
    ]
    
    response, tokens, time_s = call_model_with_retry(
        subject_client, model_name, messages, SUBJECT_PARAMS,
        mock_response=MOCK_Z3_RESPONSE
    )
    
    if response is None:
        print("❌ Z3 failed after retries")
        return None, 0, 0.0
    
    parsed = parse_revision_response(response, 'Z3')
    
    return parsed, tokens, time_s


def run_distractors(
    subject_client: OpenAI,
    model_name: str,
    system_prompt: str,
    distractor_prompts: List[str],
    conversation_history: List[Dict[str, str]]
) -> Tuple[List[str], int, float]:
    """
    Execute distractor questions to clear working memory.
    
    VERIFIED: Updates conversation_history in place for Z4.
    """
    responses = []
    total_tokens = 0
    total_time = 0.0
    
    mock_responses = [MOCK_DISTRACTOR_1, MOCK_DISTRACTOR_2]
    
    for idx, distractor in enumerate(distractor_prompts):
        messages = [
            {"role": "system", "content": system_prompt}
        ] + conversation_history + [
            {"role": "user", "content": distractor}
        ]
        
        response, tokens, time_s = call_model_with_retry(
            subject_client, model_name, messages, SUBJECT_PARAMS,
            mock_response=mock_responses[idx] if idx < len(mock_responses) else None
        )
        
        if response:
            responses.append(response)
            total_tokens += tokens
            total_time += time_s
            
            # CRITICAL: Update conversation history for Z4 retention test
            conversation_history.append({"role": "user", "content": distractor})
            conversation_history.append({"role": "assistant", "content": response})
    
    return responses, total_tokens, total_time


def run_z4(
    subject_client: OpenAI,
    model_name: str,
    system_prompt: str,
    z4_prompt: str,
    conversation_history: List[Dict[str, str]]
) -> Tuple[Dict[str, Any], int, float]:
    """
    Execute Z4: Retention check after distractors.
    
    VERIFIED: Receives full conversation history including:
    - System prompt
    - Z1 prompt + response
    - Z3 prompt + response
    - Distractor 1 prompt + response
    - Distractor 2 prompt + response
    - Z4 prompt (current)
    """
    messages = [
        {"role": "system", "content": system_prompt}
    ] + conversation_history + [
        {"role": "user", "content": z4_prompt}
    ]
    
    if DRY_RUN_MODE:
        print("\n" + "🔍"*40)
        print("Z4 CONVERSATION HISTORY VERIFICATION")
        print("🔍"*40)
        print(f"Total messages in history: {len(conversation_history)}")
        print("\nHistory structure:")
        for i, msg in enumerate(conversation_history):
            content_preview = msg['content'][:80].replace('\n', ' ')
            print(f"  {i+1}. {msg['role']:10s}: {content_preview}...")
        print("🔍"*40 + "\n")
    
    response, tokens, time_s = call_model_with_retry(
        subject_client, model_name, messages, SUBJECT_PARAMS,
        mock_response=MOCK_Z4_RESPONSE
    )
    
    if response is None:
        print("❌ Z4 failed after retries")
        return None, 0, 0.0
    
    parsed = parse_revision_response(response, 'Z4')
    
    return parsed, tokens, time_s


def run_topic_experiment(
    topic: Dict[str, Any],
    prompts: Dict[str, Any],
    subject_client: OpenAI,
    judge_client: OpenAI,
    df: pd.DataFrame,
    excel_file: str,
    jsonl_file: str,
    md_file: str,
    config: ExperimentConfig
) -> pd.DataFrame:
    """
    Execute full experiment workflow for a single topic (T1, T2, or T3).
    
    Steps:
    1. Z1: Initial evaluation
    2. Z2: Judge coding
    3. Z3: Autorevision
    4. Distractors
    5. Z4: Retention
    6. Log to Excel, JSONL, MD
    """
    topic_id = topic['topic_id']
    topic_label = topic['topic_label']
    topic_intro = topic['topic_intro']
    statements = topic['statements']
    
    print(f"\n{'='*80}")
    print(f"📋 Processing {topic_id}: {topic_label}")
    print(f"{'='*80}\n")
    
    # Track costs
    total_tokens = 0
    total_time = 0.0
    
    # ========================================================================
    # Z1: Initial Evaluation
    # ========================================================================
    print("🔹 Step Z1: Initial statement evaluation...")
    
    # Use system prompt from config (supports both neutral and biased personas)
    system_prompt = config.system_prompt
    z1_prompt = prompts[topic_id]['z1']
    
    z1_result, z1_tokens, z1_time = run_z1(
        subject_client, config.model_name, system_prompt, z1_prompt, topic_intro, statements
    )
    
    if z1_result is None:
        print(f"❌ Skipping {topic_id} due to Z1 failure")
        return df
    
    total_tokens += z1_tokens
    total_time += z1_time
    
    print(f"✅ Z1 completed ({z1_tokens} tokens, {z1_time:.2f}s)")
    
    # ========================================================================
    # Z2: Judge Evaluation
    # ========================================================================
    print("🔹 Step Z2: Judge evaluation (DQI, Source)...")
    
    judge_prompt_template = prompts['judge_prompt']
    
    z2_result, z2_tokens, z2_time = run_z2(
        judge_client, judge_prompt_template, z1_result['full_response']
    )
    
    if z2_result is None:
        print(f"❌ Skipping {topic_id} due to Z2 failure")
        return df
    
    total_tokens += z2_tokens
    total_time += z2_time
    
    print(f"✅ Z2 completed (DQI={z2_result['DQI_score']}, Source={z2_result['Source_score']})")
    
    # ========================================================================
    # Find statement for autorevision (Z3)
    # ========================================================================
    autorevision_stmt = None
    autorevision_idx = None
    
    for i, stmt in enumerate(statements):
        if stmt.get('use_for_autorevision', False):
            autorevision_stmt = stmt
            autorevision_idx = i
            break
    
    # Initialize conversation history for Z3/Z4
    conversation_history = [
        {"role": "user", "content": z1_prompt},
        {"role": "assistant", "content": z1_result['full_response']}
    ]
    
    # ========================================================================
    # Z3: Autorevision
    # ========================================================================
    z3_result = None
    z3_data = None
    
    if autorevision_stmt:
        print(f"🔹 Step Z3: Autorevision for {autorevision_stmt['id']}...")
        
        z3_prompt = prompts[topic_id]['z3']
        
        z3_result, z3_tokens, z3_time = run_z3(
            subject_client, config.model_name, system_prompt, z3_prompt, conversation_history
        )
        
        if z3_result:
            total_tokens += z3_tokens
            total_time += z3_time
            
            # CRITICAL: Update conversation history for retention test
            conversation_history.append({"role": "user", "content": z3_prompt})
            conversation_history.append({"role": "assistant", "content": z3_result['full_response']})
            
            # Code autorevision quality
            z1_answer = z1_result['evaluations'][autorevision_idx]['answer']
            z3_answer = z3_result['answer']
            ground_truth = autorevision_stmt['ground_truth']
            
            A_code = code_autorevision(z1_answer, z3_answer, ground_truth)
            
            z3_data = {
                'statement_id': autorevision_stmt['id'],
                'original_answer': z1_answer,
                'original_prob': z1_result['evaluations'][autorevision_idx]['probability'],
                'revised_answer': z3_answer,
                'revised_prob': z3_result['probability'],
                'A_code': A_code,
                'full_response': z3_result['full_response']
            }
            
            print(f"✅ Z3 completed (A={A_code}, {z3_answer}, P={z3_result['probability']:.2f})")
    
    # ========================================================================
    # Distractors
    # ========================================================================
    print("🔹 Running distractor questions...")
    
    distractor_prompts = [prompts['distractor_1'], prompts['distractor_2']]
    
    distractor_responses, d_tokens, d_time = run_distractors(
        subject_client, config.model_name, system_prompt, distractor_prompts, conversation_history
    )
    
    total_tokens += d_tokens
    total_time += d_time
    
    print(f"✅ Distractors completed ({len(distractor_responses)} questions)")
    
    # ========================================================================
    # Z4: Retention
    # ========================================================================
    z4_result = None
    z4_data = None
    
    if autorevision_stmt and z3_result:
        print(f"🔹 Step Z4: Retention check for {autorevision_stmt['id']}...")
        
        z4_prompt = prompts[topic_id]['z4']
        
        z4_result, z4_tokens, z4_time = run_z4(
            subject_client, config.model_name, system_prompt, z4_prompt, conversation_history
        )
        
        if z4_result:
            total_tokens += z4_tokens
            total_time += z4_time
            
            # Code retention
            R_code = code_retention(z3_result['answer'], z4_result['answer'])
            
            z4_data = {
                'statement_id': autorevision_stmt['id'],
                'z3_answer': z3_result['answer'],
                'z3_prob': z3_result['probability'],
                'z4_answer': z4_result['answer'],
                'z4_prob': z4_result['probability'],
                'R_code': R_code,
                'full_response': z4_result['full_response']
            }
            
            print(f"✅ Z4 completed (R={R_code}, {z4_result['answer']}, P={z4_result['probability']:.2f})")
    
    # ========================================================================
    # Log Results to Excel
    # ========================================================================
    print(f"💾 Saving results to Excel...")
    
    for i, stmt in enumerate(statements):
        z1_eval = z1_result['evaluations'][i]
        
        # Determine if this statement has A and R data
        is_autorevision_stmt = (autorevision_stmt and stmt['id'] == autorevision_stmt['id'])
        
        row_data = {
            'Topic_ID': topic_id,
            'Statement_ID': stmt['id'],
            'Statement_Text': stmt['text'],
            'Model_Answer': z1_eval['answer'],
            'Ground_Truth_O': 1 if stmt['ground_truth'] else 0,
            'Factuality_F': 1 if (z1_eval['answer'] == 'TRUE') == stmt['ground_truth'] else 0,
            'Confidence_P': z1_eval['probability'],
            'Brier_Score': calculate_brier(z1_eval['probability'], stmt['ground_truth']),
            'Sources_S_statement': None,  # Human coding required
            'DQI_Global': z2_result['DQI_score'],
            'Autorevision_A': z3_data['A_code'] if is_autorevision_stmt and z3_data else None,
            'Retention_R': z4_data['R_code'] if is_autorevision_stmt and z4_data else None,
            'Cost_Tokens': total_tokens if i == 0 else None,  # Log once per topic
            'Cost_Infer_s': total_time if i == 0 else None
        }
        
        df = append_to_excel(df, row_data, excel_file)
    
    print(f"✅ Excel updated: {excel_file}")
    
    # ========================================================================
    # Log to JSONL
    # ========================================================================
    jsonl_data = {
        'timestamp': datetime.now().isoformat(),
        'topic_id': topic_id,
        'topic_label': topic_label,
        'topic_intro': topic_intro,
        'statements': [
            {
                **stmt,
                'z1_answer': z1_result['evaluations'][i]['answer'],
                'z1_probability': z1_result['evaluations'][i]['probability'],
                'brier_score': calculate_brier(z1_result['evaluations'][i]['probability'], stmt['ground_truth'])
            }
            for i, stmt in enumerate(statements)
        ],
        'z1_full_response': z1_result['full_response'],
        'z1_commentary': z1_result['commentary'],
        'judge': z2_result,
        'z3': z3_data,
        'z4': z4_data,
        'cost_tokens': total_tokens,
        'cost_infer_s': total_time
    }
    
    append_to_jsonl(jsonl_data, jsonl_file)
    print(f"✅ JSONL updated: {jsonl_file}")
    
    # ========================================================================
    # Log to Markdown
    # ========================================================================
    md_data = {
        'topic_id': topic_id,
        'topic_label': topic_label,
        'topic_intro': topic_intro,
        'z1_commentary': z1_result['commentary'],
        'statements': [
            {
                **stmt,
                'z1_answer': z1_result['evaluations'][i]['answer'],
                'z1_probability': z1_result['evaluations'][i]['probability']
            }
            for i, stmt in enumerate(statements)
        ],
        'judge': z2_result,
        'z3': z3_data,
        'z4': z4_data,
        'cost_tokens': total_tokens,
        'cost_infer_s': total_time
    }
    
    append_to_markdown(md_data, md_file)
    print(f"✅ Markdown updated: {md_file}")
    
    print(f"\n✅ {topic_id} completed successfully!")
    print(f"   Total tokens: {total_tokens}, Total time: {total_time:.2f}s\n")
    
    return df


def display_menu():
    """Display interactive menu for experiment selection."""
    print("\n" + "="*80)
    print("🧪 EED AUDIT PILOT - EXPERIMENT SELECTOR")
    print("="*80)
    print()
    print("SELECT AN EXPERIMENT:")
    print()
    print("  STANDARD RUNS (Neutral Persona + Hard Mode Distractors):")
    print("  1. Llama 3 8B Instruct (Local)")
    print("  2. Mistral 7B Instruct (Local)")
    print("  3. Gemma 2 9B (Local)")
    print("  4. Phi-3 Medium (Local)")
    print("  5. GPT-4o (Cloud Benchmark)")
    print()
    print("  ADVANCED:")
    print("  6. [NEW MODEL] Pull & Run a New Model (Docker)")
    print()
    print("  SHADOW RUNS (Biased Persona + Hard Mode Distractors):")
    print("  7. Llama 3 8B - Biased Mode (Cynical Persona)")
    print("  8. GPT-4o - Biased Mode (Cynical Persona)")
    print()
    print("  OTHER:")
    print("  0. Exit")
    print()
    print("="*80)


def pull_docker_model(model_tag: str) -> bool:
    """
    Pull a new model into Docker using ollama CLI.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n📥 Pulling model '{model_tag}' into Docker container...")
        print("⏳ This may take several minutes depending on model size...")
        print()
        
        import subprocess
        
        # Run docker exec with live output
        process = subprocess.Popen(
            ['docker', 'exec', 'ollama_research', 'ollama', 'pull', model_tag],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output
        for line in process.stdout:
            print(line, end='', flush=True)
        
        process.wait()
        
        if process.returncode == 0:
            print(f"\n✅ Successfully pulled model '{model_tag}'")
            return True
        else:
            print(f"\n❌ Failed to pull model '{model_tag}'")
            return False
            
    except Exception as e:
        print(f"\n❌ Error pulling model: {e}")
        return False


def get_config_from_menu(prompts: Dict[str, Any]) -> Optional[ExperimentConfig]:
    """
    Display menu and return configuration based on user choice.
    
    Returns:
        ExperimentConfig or None if user exits
    """
    display_menu()
    
    while True:
        try:
            choice = input("Enter your choice (0-8): ").strip()
            
            if choice == "0":
                print("\n👋 Exiting...")
                return None
            
            elif choice == "1":
                return ExperimentConfig(
                    model_name="llama3:latest",
                    base_url="http://localhost:12434/v1",
                    api_key="ollama",
                    system_prompt=prompts['system_prompt'],
                    output_suffix="llama3_hard",
                    display_name="Llama 3 8B Instruct",
                    mode="Neutral"
                )
            
            elif choice == "2":
                return ExperimentConfig(
                    model_name="mistral:instruct",
                    base_url="http://localhost:12434/v1",
                    api_key="ollama",
                    system_prompt=prompts['system_prompt'],
                    output_suffix="mistral_hard",
                    display_name="Mistral 7B Instruct",
                    mode="Neutral"
                )
            
            elif choice == "3":
                return ExperimentConfig(
                    model_name="gemma2:9b",
                    base_url="http://localhost:12434/v1",
                    api_key="ollama",
                    system_prompt=prompts['system_prompt'],
                    output_suffix="gemma2_hard",
                    display_name="Gemma 2 9B",
                    mode="Neutral"
                )
            
            elif choice == "4":
                return ExperimentConfig(
                    model_name="phi3:medium",
                    base_url="http://localhost:12434/v1",
                    api_key="ollama",
                    system_prompt=prompts['system_prompt'],
                    output_suffix="phi3_hard",
                    display_name="Phi-3 Medium",
                    mode="Neutral"
                )
            
            elif choice == "5":
                return ExperimentConfig(
                    model_name="gpt-4o",
                    base_url="https://api.openai.com/v1",
                    api_key=os.environ.get("OPENAI_API_KEY"),
                    system_prompt=prompts['system_prompt'],
                    output_suffix="gpt4o_hard",
                    display_name="GPT-4o",
                    mode="Neutral"
                )
            
            elif choice == "6":
                print("\n📦 Pull New Model from Docker")
                print("-" * 80)
                model_tag = input("Enter model tag (e.g., 'openhermes', 'llama3'): ").strip()
                
                if not model_tag:
                    print("❌ Invalid model tag")
                    continue
                
                # Pull the model
                if pull_docker_model(model_tag):
                    # Configure for the new model
                    return ExperimentConfig(
                        model_name=model_tag,
                        base_url="http://localhost:12434/v1",
                        api_key="ollama",
                        system_prompt=prompts['system_prompt'],
                        output_suffix=f"{model_tag.replace(':', '_')}_hard",
                        display_name=f"{model_tag}",
                        mode="Neutral"
                    )
                else:
                    print("⚠️  Model pull failed. Try again or choose another option.")
                    input("Press Enter to continue...")
                    display_menu()
            
            elif choice == "7":
                return ExperimentConfig(
                    model_name="llama3:latest",
                    base_url="http://localhost:12434/v1",
                    api_key="ollama",
                    system_prompt=prompts['system_prompt_biased'],
                    output_suffix="llama3_biased",
                    display_name="Llama 3 8B - Biased Persona",
                    mode="Biased"
                )
            
            elif choice == "8":
                return ExperimentConfig(
                    model_name="gpt-4o",
                    base_url="https://api.openai.com/v1",
                    api_key=os.environ.get("OPENAI_API_KEY"),
                    system_prompt=prompts['system_prompt_biased'],
                    output_suffix="gpt4o_biased",
                    display_name="GPT-4o - Biased Persona",
                    mode="Biased"
                )
            
            else:
                print("❌ Invalid choice. Please enter 0-8.")
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting...")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def run_experiment(
    config: ExperimentConfig,
    prompts: Dict[str, Any],
    topics: List[Dict[str, Any]],
    script_dir: Path
) -> bool:
    """
    Run a complete experiment with the given configuration.
    
    Returns:
        True if successful, False otherwise
    """
    # Display startup banner
    print("\n" + "="*80)
    print("🚀 EED AUDIT PILOT - COGNITIVE AUDIT OF LLM")
    print("="*80)
    print(f"📊 Subject Model: {config.display_name}")
    print(f"⚖️  Judge Model: {JUDGE_MODEL}")
    print(f"🎭 Mode: {config.mode}")
    print("="*80 + "\n")
    
    # ========================================================================
    # Initialize API clients
    # ========================================================================
    print("🔌 Initializing API clients...")
    
    # Subject model
    subject_client = OpenAI(
        base_url=config.base_url,
        api_key=config.api_key
    )
    
    # Check connection (skip in dry-run mode)
    # Temporarily update global for connection check
    global LOCAL_MODEL, LOCAL_BASE_URL, LOCAL_API_KEY
    old_model = LOCAL_MODEL
    old_url = LOCAL_BASE_URL
    old_key = LOCAL_API_KEY
    
    LOCAL_MODEL = config.model_name
    LOCAL_BASE_URL = config.base_url
    LOCAL_API_KEY = config.api_key
    
    if not check_local_connection(subject_client):
        if not DRY_RUN_MODE:
            print(f"\n❌ Cannot proceed without {config.model_name} connection.")
            print("   Use --dry-run to test without API connection.")
            LOCAL_MODEL = old_model
            LOCAL_BASE_URL = old_url
            LOCAL_API_KEY = old_key
            return False
    
    # Restore globals
    LOCAL_MODEL = old_model
    LOCAL_BASE_URL = old_url
    LOCAL_API_KEY = old_key
    
    # Judge model (GPT-4o) - same client if both use OpenAI, otherwise separate
    if DRY_RUN_MODE:
        judge_client = OpenAI(api_key="dummy-key-for-dry-run")
        print(f"✅ [DRY RUN] Judge model ({JUDGE_MODEL}) mock initialized\n")
    else:
        # If subject is also GPT-4o, reuse the same client
        if config.model_name == "gpt-4o":
            judge_client = subject_client
            print(f"✅ Subject and Judge both using {config.model_name}\n")
        else:
            # Separate judge client for non-OpenAI subject models
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                print("❌ OPENAI_API_KEY environment variable not set")
                return False
            judge_client = OpenAI(api_key=openai_api_key)
            print(f"✅ Judge model ({JUDGE_MODEL}) initialized\n")
    
    # ========================================================================
    # Initialize output files with new data structure
    # ========================================================================
    if DRY_RUN_MODE:
        # Dry run: use old structure for testing
        output_dir = script_dir
        excel_file = output_dir / 'results_dry.xlsx'
        jsonl_file = output_dir / 'audit_log_dry.jsonl'
        md_file = output_dir / 'audit_log_dry.md'
    else:
        # Production: use new timestamped directory structure
        experiments_root = script_dir / 'data' / 'experiments'
        output_dir = experiments_root / config.experiment_dir_name
        
        # Create experiment directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        excel_file = output_dir / 'results.xlsx'
        jsonl_file = output_dir / 'audit_log.jsonl'
        md_file = output_dir / 'audit_log.md'
    
    # Initialize Excel DataFrame (load existing if present)
    df = init_excel_dataframe(str(excel_file))
    
    # Clear/initialize log files
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        f.write("")  # Clear file
    
    with open(md_file, 'w', encoding='utf-8') as f:
        mode_str = " [DRY RUN]" if DRY_RUN_MODE else f" [{config.mode} Mode]"
        f.write(f"# EED Audit Pilot - Experiment Log{mode_str}\n")
        f.write(f"**Model:** {config.display_name}\n")
        f.write(f"**Started:** {datetime.now().isoformat()}\n")
    
    print(f"📝 Output files initialized:")
    print(f"   - {excel_file}")
    print(f"   - {jsonl_file}")
    print(f"   - {md_file}\n")
    
    # ========================================================================
    # Main experiment loop (T1, T2, T3)
    # ========================================================================
    print("🔄 Starting main experiment loop...\n")
    
    for topic in tqdm(topics, desc="Processing topics", unit="topic"):
        try:
            df = run_topic_experiment(
                topic=topic,
                prompts=prompts,
                subject_client=subject_client,
                judge_client=judge_client,
                df=df,
                excel_file=str(excel_file),
                jsonl_file=str(jsonl_file),
                md_file=str(md_file),
                config=config
            )
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user. Saving current progress...")
            break
        except Exception as e:
            print(f"\n❌ Error processing {topic.get('topic_id', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # ========================================================================
    # Final summary
    # ========================================================================
    mode_str = " [DRY RUN]" if DRY_RUN_MODE else f" [{config.mode} Mode]"
    print("\n" + "="*80)
    print(f"🎉 EXPERIMENT COMPLETED{mode_str}")
    print("="*80)
    
    if DRY_RUN_MODE:
        print(f"\n📊 Results saved to:")
        print(f"   - {excel_file} (spreadsheet)")
        print(f"   - {jsonl_file} (raw data)")
        print(f"   - {md_file} (human-readable report)")
    else:
        # Print absolute path for production runs
        print(f"\n📁 Data saved to: {output_dir.absolute()}")
        print(f"\n📊 Files generated:")
        print(f"   - results.xlsx (spreadsheet)")
        print(f"   - audit_log.jsonl (raw data)")
        print(f"   - audit_log.md (human-readable report)")
    
    print(f"\n✅ Processed {len(df)} statement rows across {len(topics)} topics")
    
    if DRY_RUN_MODE:
        print("\n🧪 DRY RUN COMPLETE")
        print("   Review the output files to verify:")
        print("   1. Prompt injection is correct")
        print("   2. Variable substitution works")
        print("   3. History management is proper (check Z4 section)")
        print("   4. Excel structure matches protocol")
        print("\n   If everything looks good, run without --dry-run:")
        print("   python run_audit.py")
    else:
        print("\n💡 Next steps:")
        print("   1. Open results file to view metrics")
        print("   2. Manually code columns: Sources_S_statement")
        print("   3. Review audit_log file for qualitative analysis")
    
    print("\n" + "="*80 + "\n")
    
    return True


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main experiment execution with interactive menu."""
    global DRY_RUN_MODE
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='EED Audit Pilot - Interactive Cognitive Audit of LLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with interactive menu
  python run_audit.py
  
  # Dry run to test prompts and logic
  python run_audit.py --dry-run
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode with mock API calls to verify prompts and logic'
    )
    
    args = parser.parse_args()
    DRY_RUN_MODE = args.dry_run
    
    if DRY_RUN_MODE:
        print("\n" + "🧪"*40)
        print("DRY RUN MODE ACTIVATED")
        print("🧪"*40)
        print("- Mock API responses will be used")
        print("- Exact prompts will be printed for inspection")
        print("- Output files will use '_dry' suffix")
        print("🧪"*40 + "\n")
    
    # ========================================================================
    # Workspace organization (cleanup legacy files)
    # ========================================================================
    script_dir = Path(__file__).parent
    
    if not DRY_RUN_MODE:
        organize_workspace(script_dir)
    
    # ========================================================================
    # Load data files
    # ========================================================================
    prompts = load_json(script_dir / 'prompts.json')
    topics = load_json(script_dir / 'topics.json')
    
    # Verify required prompt keys
    required_keys = ['system_prompt', 'system_prompt_biased']
    missing_keys = [key for key in required_keys if key not in prompts]
    
    if missing_keys:
        print(f"❌ Missing required keys in prompts.json: {missing_keys}")
        print("   Please ensure both 'system_prompt' and 'system_prompt_biased' are present.")
        sys.exit(1)
    
    # ========================================================================
    # Interactive menu (unless dry-run)
    # ========================================================================
    if DRY_RUN_MODE:
        # For dry-run, use current LOCAL_MODEL configuration
        print(f"📂 Using current configuration for dry-run: {LOCAL_MODEL}")
        config = ExperimentConfig(
            model_name=LOCAL_MODEL,
            base_url=LOCAL_BASE_URL,
            api_key=LOCAL_API_KEY,
            system_prompt=prompts['system_prompt'],
            output_suffix="dry",
            display_name=LOCAL_MODEL,
            mode="Neutral"
        )
    else:
        # Show interactive menu
        config = get_config_from_menu(prompts)
        
        if config is None:
            return  # User chose to exit
    
    # ========================================================================
    # Run experiment with selected configuration
    # ========================================================================
    success = run_experiment(config, prompts, topics, script_dir)
    
    if success:
        print("\n✅ Experiment completed successfully!")
    else:
        print("\n⚠️  Experiment encountered errors.")


if __name__ == '__main__':
    main()
