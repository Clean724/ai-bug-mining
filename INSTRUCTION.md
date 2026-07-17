# AI-Assisted Vulnerability Detection Submission

## 1. Environment Preparation

This submission is a report-first software defect detection workflow. It does not modify the target project and does not require any network-security scenario.

Expected target project layout:

```text
code/
└── tensorflow_v2_11_0/
```

If the target project is not already present, prepare it outside this submission with the competition-provided assets or with:

```bash
git clone https://github.com/tensorflow/tensorflow code/tensorflow_v2_11_0
cd code/tensorflow_v2_11_0
git checkout -b competition v2.11.0
```

Python 3 is required to run the helper scripts.

## 2. Execution

Run the static candidate collector when a new target tree is supplied:

```bash
python work/scripts/collect_candidates.py --repo code/tensorflow_v2_11_0 --out work/candidate_findings_v2_11_0.md
```

The script scans high-risk source areas for candidate crash, input-validation, bounds, integer-overflow, and shape-handling issues. The generated candidate list is then reviewed with an LLM and validated with AI-generated reproducer tests.

Generate reproducible LLM audit prompts:

```bash
python work/scripts/generate_audit_prompts.py --repo code/tensorflow_v2_11_0 --candidates work/candidate_findings_v2_11_0.md --out-dir work/audit_prompts --limit 20
```

Feed the generated `work/audit_prompts/prompt_*.md` prompts to the LLM without adding project name, version number, known CVEs, known issues, or known fixes. Record the complete, unedited platform export into `work/llm_chat_log.json`.

Run the AI-generated, process-level black-box reproducers:

```bash
python work/run_blackbox_repros.py
```

The reproducers start `configure.py` as a child process. They do not import target modules or mock target functions. Exit code `0` means all applicable defects were observed; exit code `1` means a defect was not reproduced; exit code `2` means the result is inconclusive.

Detailed operator guidance is in:

```text
work/audit_playbook.md
work/chat_log_template.md
```

## 3. Completion Criteria

Execution is complete when these files exist:

```text
work/vulnerability_list.md
work/llm_chat_log.json
work/vulnerability_report.md
```

Optional intermediate output:

```text
work/candidate_findings.md
work/audit_prompts/
```

## 4. Result Location

Final deliverables are located in:

```text
work/vulnerability_list.md
work/llm_chat_log.json
work/vulnerability_report.md
```

The submitted work focuses on discovering and proving software defects. It does not require a patched TensorFlow tree unless the judge explicitly asks for fixes.
