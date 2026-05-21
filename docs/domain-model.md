# Domain Model

The LLM Evaluation Platform is designed around reproducible evaluation workflows for production-grade AI systems.

## Core Evaluation Flow

```text
PromptVersion + Dataset + ModelConfiguration
                    ↓
            EvaluationRun
                    ↓
          EvaluationResults
                    ↓
             MetricResults
```

## Design Principles

- Prompts are versioned and immutable once evaluated.
- Model configurations are separated from model providers.
- Evaluation runs must be reproducible.
- Results must remain auditable over time.
- Evaluation metrics are extensible.
- JSON fields are used where experimentation and schema evolution are expected.

## Why `ModelConfiguration` Exists

A single model can behave very differently depending on runtime parameters.

Example:

- GPT-4o-mini with temperature 0.2
- GPT-4o-mini with temperature 0.8

The platform treats these as different evaluation configurations while still associating them with the same underlying model provider.

This allows:

- parameter comparison
- reproducible evaluations
- benchmark consistency
- configuration-level analytics

## Reproducibility Strategy

Evaluation runs store:

- prompt version
- dataset
- model configuration
- model parameter snapshot
- evaluation configuration
- rendered prompt

This guarantees that historical evaluation runs remain reproducible even if the platform evolves later.

## Extensibility Considerations

The platform is intentionally designed to support:

- multiple providers
- future RAG evaluations
- multi-agent workflows
- LLM tracing
- observability systems
- online/offline evaluation modes
- asynchronous execution engines
- benchmark datasets
- future human evaluation workflows
