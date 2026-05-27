# Agent Operational Degradation Guard Spec

## Purpose

Detect and prevent operational degradation (Routine Drift) in AI agents caused by continuous task repetition and familiarity.

This spec defines the design principles, monitoring signals, and countermeasures for AI agents that maintain quality during ramp-up phases but begin to skip verification steps as tasks become routine.

---

## Design Philosophy

In manual-intensive manufacturing operations, two opposing forces shape operational quality over time.

**Ramp-up phase:**
Workers improve in both speed and quality as they become familiar with the task. Defect rates decrease, throughput increases.

**Routine drift phase:**
After a certain period of familiarity, quality begins to decline. Workers skip verification steps, rely on assumed patterns, and lose the attention they had during the ramp-up phase. Defect rates increase silently, without any change in the task itself.

The countermeasure in manufacturing is not to push for more concentration, but to **intentionally insert different work, different verification, or different stimulus** between repetitive tasks. This restores attention and restores quality.

**Critical principle:**
Continuous repetition causes operational drift.
Routine work requires intentional interruption.
Familiarity reduces verification quality.
A successful previous step does not guarantee stable process quality.

---

## Manufacturing Ramp-Up and Routine Drift

### Background

In manual-intensive manufacturing operations, two opposing forces shape operational quality over time.

**Ramp-up phase:**
Workers improve in both speed and quality as they become familiar with the task. Defect rates decrease, throughput increases.

**Routine drift phase:**
After a certain period of familiarity, quality begins to decline. Workers skip verification steps, rely on assumed patterns, and lose the attention they had during the ramp-up phase. Defect rates increase silently, without any change in the task itself.

The countermeasure in manufacturing is not to push for more concentration, but to **intentionally insert different work, different verification, or different stimulus** between repetitive tasks. This restores attention and restores quality.

### Application to AI Agents

AI agents exhibit the same pattern when performing repetitive tasks:

- Assume the current task is the same as the previous one
- Skip reading input / instruction carefully
- Skip file path verification
- Skip canonical source verification
- Skip evidence verification
- Skip completion verification
- Conflate implemented / designed / planned states
- Miss backup sync or report items
- Report "completed" while leaving sub-tasks unfinished

This is not hallucination. This is **Routine Drift** —
operational degradation caused by repetition and familiarity.

---

## Core Concepts (Added 2026-05-27)

### 1. Routine Drift

A state in which an AI agent skips verification steps and biases toward past patterns due to continuous execution of similar tasks.

### 2. Attention Reset Checkpoint

A deliberate insertion of a different verification mode during long or repetitive work, designed to switch the agent's processing mode and restore verification quality.

### 3. Forced Different-Mode Verification

A design pattern where verification is performed in a different mode than generation, rather than in the same flow.

Examples:
- Generation mode → Inspection mode
- Edit mode → Diff verification mode
- Implementation mode → Canonical source matching mode
- Summarization mode → Evidence verification mode
- Continuous file editing → CANONICAL_FILES.md cross-check
- Continuous spec creation → Existing spec duplication check
- Before commit → git diff / git status verification only

---

## Core Principles

Continuous repetition causes operational drift.
Routine work requires intentional interruption.
Familiarity reduces verification quality.
A successful previous step does not guarantee stable process quality.

### Japanese translation (reference)

```
# 同じ作業の連続は、運用品質を劣化させる。
# 慣れは確認品質を下げる。
# 惰性を止めるには、意図的な割り込み工程が必要。
# 直前の成功は、安定工程を意味しない。
```

---

## Example: Routine Drift Observed in Practice

During iterative work on the AI Agent Payment Safety Stack project, multiple instances of Routine Drift were observed:

- An AI assistant transferred an unrelated time-period figure ("3-4 weeks") from one context (Pinterest evaluation period) to another (spec promotion timing) without verification.
- A coding agent skipped a required backup sync step, judging it as "separate work" based on familiarity with the previous task.
- A coding agent waited for explicit authorization on a fully specified task, overcompensating after a previous instance of skipped work.

Each case occurred during continuous task execution, not during initial task interpretation. This is consistent with the manufacturing pattern: quality degrades during routine phase, not during ramp-up phase.

The countermeasure applied was insertion of a different verification mode (canonical source check, sync verification by Compare-Object, explicit single-pass execution mode declaration).

---

## Status

- This is a design specification.
- It does not indicate that a runtime API has already been implemented.
- It is part of the 13 confirmed design specs.
- It does not add a new Live API.
- Spec version: 2026-05-27 revision
- Revision content: Added Routine Drift concepts and Manufacturing Ramp-Up section
