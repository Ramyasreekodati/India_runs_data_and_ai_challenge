# Engineering Playbook: Redrob AI Ranker (v1.2)

> **Engineering Philosophy: Every component must justify its existence.**
> If a module doesn't improve ranking, explainability, runtime, or maintainability, it shouldn't exist. Complexity must earn its place. The winning system is the simplest architecture that satisfies all constraints.

## 1. Success Criteria & Final Acceptance
- **Technical**: Ranking completes under 5 mins; Memory < 16 GB; Format passes validator; Top 100 looks genuinely relevant.
- **Engineering**: Modular code, test coverage, reproducible deterministic results.
- **Presentation**: Judges understand architecture < 5 mins; repository is clean; every decision is defensible.

## 2. Definition of Done (DoD) & Review Gates
Every phase must pass an explicit exit criterion before advancing. After every phase, we stop and ask:

- **Architecture Review**: Does this satisfy the JD? Does this satisfy runtime? Did we introduce bias? Do we have evidence? Can we explain it?
- **Code Review**: Is it readable, modular, reusable, configurable?
- **Data Review**: Are there unexpected distributions, leakage, missing values, or outliers?
- **Experiment Review**: Did this actually improve results, or only increase complexity?
- **Documentation Review**: Are the README, Decision Log, ADR, and Experiment Log updated?

## 3. Dependency Map
Development strictly follows this dependency chain:
`README & JD Understanding` → `Schema Analysis & Profiling` → `Candidate Parser` → `Feature Engineering` → `Retrieval` → `Multi-Level Ranking` → `Reasoning Generation` → `Submission & Evaluation`

## 4. Interface Contracts & Configuration
- Modules must remain decoupled (e.g., `Input (Raw JSON) -> Output (Candidate Feature Object)`).
- **Configuration Management**: No hardcoded weights. All heuristic thresholds (e.g., `tech_score: 0.45`) live in external config files to enable rapid experiment tracking without mutating logic.

## 5. Risk Register & Failure Recovery Plan
| Risk | Mitigation / Recovery |
|------|-----------------------|
| **Compute constraint exceeded** | Select retrieval algorithms based on candidate profiling benchmarks (avoiding full-dataset LLMs if memory is tight). |
| **Keyword Stuffers** | Use continuous contradiction detection rather than rigid hard-drops. |
| **Reasoning column hallucinates** | Generate from evidence only. |
| **Malformed JSON record** | Exception handling in the parser: log, skip corrupted record, and continue. |

## 6. Error Analysis & Bias Review
- Systematically audit the "Wrong Top 20" (false positives) and False Negatives.
- Ensure geography or institutional tiering do not dominate over actual production experience.

## 7. Architecture Decision Records (ADR)
Specific algorithms (e.g., BM25 vs Min-Heap) are NOT predefined here. They belong in the ADR *only after* experiments and dataset profiling prove their worth.

## 8. Reproducibility & Testing
- Before comparisons: fix random seeds, document config weights, and use the same evaluation framework.
- Independent testing for missing fields and boundary outputs.

## 9. Observability & Interview Readiness
- Log progression metrics across all pipeline stages (Loaded -> Filtered -> Retrieved -> Ranked -> Exported).
- For every choice, be prepared to defend: Why this? Why not that? What are the trade-offs?
