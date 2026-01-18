# Product Requirements Document: AgentEvals

## Project Overview

**Project Name**: AgentEvals

**Description**: A three-tiered evaluation framework for multi-agent AI systems that provides objective benchmarking of autonomous agent teams. Uses the PeerRead dataset to generate and evaluate scientific paper reviews through traditional metrics, LLM-as-a-Judge assessment, and graph-based complexity analysis.

**Goals**:
- Provide standardized, reproducible evaluation of multi-agent system outputs
- Enable objective comparison of different agent implementations
- Deliver multi-tiered insights combining performance, semantic, and structural metrics

**Target Users**: AI Researchers and ML Engineers working with multi-agent systems

## Technical Requirements

### Core Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| pydantic-ai-slim | >=0.8.1 | Agent framework with OpenAI/Tavily plugins |
| pydantic | >=2.10.6 | Data validation |
| pydantic-settings | >=2.9.1 | Configuration management |

### Graph Analysis
| Package | Version | Purpose |
|---------|---------|---------|
| networkx | >=3.6 | Graph creation, manipulation, complexity metrics |

### Evaluation Metrics
| Package | Version | Purpose |
|---------|---------|---------|
| rapidfuzz | >=3.0 | Fast string similarity (Levenshtein, Jaro-Winkler) |
| scikit-learn | >=1.7 | ML metrics (F1, precision, recall, cosine similarity) |

### Observability (Layered Approach)
| Package | Version | Purpose |
|---------|---------|---------|
| loguru | >=0.7 | Local structured logging |
| logfire | >=3.16 | PydanticAI tracing (optional cloud export) |
| weave | >=0.51 | W&B integration (optional) |

### Data Processing
| Package | Version | Purpose |
|---------|---------|---------|
| httpx | >=0.28 | Async HTTP client for API calls |

## Functional Requirements

### Core Features

#### Feature 1: Traditional Performance Metrics

**Description**: Measure agent system performance with standard metrics for objective comparison of implementations.

**User Stories**:
- As an ML engineer, I want to measure agent system performance with standard metrics so that I can compare different implementations objectively

**Acceptance Criteria**:
- [ ] Calculate execution time metrics for agent task completion
- [ ] Measure task success rate across evaluation runs
- [ ] Assess coordination quality between agents
- [ ] Output metrics in structured JSON format
- [ ] Support batch evaluation of multiple agent outputs

**Technical Requirements**:
- Use PydanticAI for agent implementation
- JSON output format for metrics
- Deterministic results with seed configuration

**Files Expected**:
- `src/agenteval/metrics/traditional.py` - Traditional metrics calculation
- `tests/test_traditional.py` - Tests for traditional metrics

---

#### Feature 2: LLM-as-a-Judge Evaluation

**Description**: Evaluate semantic quality of agent-generated reviews using LLM-based assessment against human baselines from PeerRead dataset.

**User Stories**:
- As a researcher, I want LLM-based quality assessment so that I can evaluate semantic review quality beyond traditional metrics

**Acceptance Criteria**:
- [ ] Load and parse PeerRead dataset papers and reviews
- [ ] Evaluate semantic quality of agent-generated reviews
- [ ] Compare agent outputs against human baseline reviews
- [ ] Provide scoring with justification from LLM judge
- [ ] Support configurable evaluation criteria

**Technical Requirements**:
- PeerRead dataset integration for scientific reviews
- PydanticAI for LLM judge agent
- Structured evaluation output with scores and reasoning

**Files Expected**:
- `src/agenteval/data/peerread.py` - PeerRead dataset loader
- `src/agenteval/judges/llm_judge.py` - LLM-as-a-Judge implementation
- `tests/test_llm_judge.py` - Tests for LLM judge

---

#### Feature 3: Graph-Based Complexity Analysis

**Description**: Analyze agent interaction patterns through graph-based structural analysis to understand coordination complexity.

**User Stories**:
- As a data scientist, I want graph-based structural analysis so that I can understand agent interaction patterns and coordination complexity

**Acceptance Criteria**:
- [ ] Model agent interactions as graph structures using NetworkX
- [ ] Calculate complexity metrics (density, centrality, clustering coefficient) from interaction graphs
- [ ] Identify coordination patterns between agents
- [ ] Export graph data for external analysis

**Technical Requirements**:
- Use NetworkX for graph representation of agent interactions
- NetworkX-based complexity metrics (graph density, degree centrality, betweenness centrality, clustering coefficient)
- JSON/GraphML export format

**Files Expected**:
- `src/agenteval/metrics/graph.py` - Graph-based metrics
- `tests/test_graph.py` - Tests for graph metrics

---

#### Feature 4: Unified Evaluation Pipeline

**Description**: Combine all three evaluation tiers into a unified pipeline with consolidated reporting.

**User Stories**:
- As a researcher, I want a unified evaluation pipeline so that I can run all three evaluation approaches together

**Acceptance Criteria**:
- [ ] Run all three evaluation tiers in sequence
- [ ] Generate consolidated evaluation report
- [ ] Support reproducible runs with seed configuration
- [ ] Output combined results in structured format
- [ ] Provide local console tracing by default
- [ ] Support optional Logfire/Weave cloud export via configuration

**Technical Requirements**:
- Pipeline orchestration for all three tiers
- Consolidated JSON report format
- Seed-based reproducibility
- Local console tracing by default (loguru)
- Optional Logfire/Weave cloud export via config

**Files Expected**:
- `src/agenteval/pipeline.py` - Unified evaluation pipeline
- `src/agenteval/report.py` - Report generation
- `tests/test_pipeline.py` - Pipeline integration tests

---

## Non-Functional Requirements

### Performance
- Evaluation runs efficiently on standard research computing resources
- Batch processing of multiple papers without memory issues

### Reproducibility
- Consistent evaluation results across multiple runs with same seed
- Version-locked dependencies via uv.lock

### Code Quality
- All code must pass `make validate` (ruff, pyright, pytest)
- Follow KISS, DRY, YAGNI principles
- Python 3.13+ with modern typing features
- Test-driven development with pytest

## Out of Scope

- Production deployment infrastructure or scaling
- Real-time streaming evaluation of agent outputs
- Support for agent frameworks beyond PydanticAI
- Multi-language support for non-English reviews

## Notes for Ralph Loop

When using the `generating-prd` skill to convert this PRD to `docs/ralph/prd.json`:

1. Each feature becomes a separate sprint/phase
2. Stories should be implementable in a single context window
3. Acceptance criteria become the `acceptance` field
4. Files expected become the `files` field

Suggested story breakdown:
- STORY-001: PeerRead dataset loader
- STORY-002: Traditional performance metrics
- STORY-003: LLM-as-a-Judge evaluation
- STORY-004: Graph-based complexity analysis
- STORY-005: Unified evaluation pipeline
