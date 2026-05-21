from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.session import Base


class EvaluationRunStatus(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Prompt(TimestampMixin, Base):
    __tablename__ = 'prompts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    versions: Mapped[list['PromptVersion']] = relationship(
        back_populates='prompt',
        cascade='all, delete-orphan',
    )


class PromptVersion(Base):
    __tablename__ = 'prompt_versions'
    __table_args__ = (
        UniqueConstraint('prompt_id', 'version', name='uq_prompt_version'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prompt_id: Mapped[int] = mapped_column(
        ForeignKey('prompts.id'),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    variables_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    prompt: Mapped[Prompt] = relationship(back_populates='versions')
    evaluation_runs: Mapped[list['EvaluationRun']] = relationship(
        back_populates='prompt_version',
    )


class Dataset(TimestampMixin, Base):
    __tablename__ = 'datasets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    examples: Mapped[list['DatasetExample']] = relationship(
        back_populates='dataset',
        cascade='all, delete-orphan',
    )
    evaluation_runs: Mapped[list['EvaluationRun']] = relationship(
        back_populates='dataset',
    )


class DatasetExample(Base):
    __tablename__ = 'dataset_examples'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey('datasets.id'),
        nullable=False,
        index=True,
    )
    input_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_metadata: Mapped[dict | None] = mapped_column(
        'metadata',
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    dataset: Mapped[Dataset] = relationship(back_populates='examples')
    evaluation_results: Mapped[list['EvaluationResult']] = relationship(
        back_populates='dataset_example',
    )


class ModelProvider(TimestampMixin, Base):
    __tablename__ = 'model_providers'
    __table_args__ = (
        UniqueConstraint('provider', 'model_name', name='uq_provider_model'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    configurations: Mapped[list['ModelConfiguration']] = relationship(
        back_populates='model_provider',
        cascade='all, delete-orphan',
    )


class ModelConfiguration(TimestampMixin, Base):
    __tablename__ = 'model_configurations'
    __table_args__ = (
        UniqueConstraint(
            'model_provider_id',
            'parameter_hash',
            name='uq_model_configuration_parameter_hash',
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_provider_id: Mapped[int] = mapped_column(
        ForeignKey('model_providers.id'),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    parameter_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    model_provider: Mapped[ModelProvider] = relationship(
        back_populates='configurations',
    )
    evaluation_runs: Mapped[list['EvaluationRun']] = relationship(
        back_populates='model_configuration',
    )


class EvaluationRun(Base):
    __tablename__ = 'evaluation_runs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prompt_version_id: Mapped[int] = mapped_column(
        ForeignKey('prompt_versions.id'),
        nullable=False,
        index=True,
    )
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey('datasets.id'),
        nullable=False,
        index=True,
    )
    model_configuration_id: Mapped[int] = mapped_column(
        ForeignKey('model_configurations.id'),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=EvaluationRunStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    model_parameters_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    evaluation_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    total_examples: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed_examples: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_examples: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    prompt_version: Mapped[PromptVersion] = relationship(
        back_populates='evaluation_runs',
    )
    dataset: Mapped[Dataset] = relationship(back_populates='evaluation_runs')
    model_configuration: Mapped[ModelConfiguration] = relationship(
        back_populates='evaluation_runs',
    )
    results: Mapped[list['EvaluationResult']] = relationship(
        back_populates='evaluation_run',
        cascade='all, delete-orphan',
    )


class EvaluationResult(Base):
    __tablename__ = 'evaluation_results'
    __table_args__ = (
        UniqueConstraint(
            'evaluation_run_id',
            'dataset_example_id',
            name='uq_evaluation_run_dataset_example',
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    evaluation_run_id: Mapped[int] = mapped_column(
        ForeignKey('evaluation_runs.id'),
        nullable=False,
        index=True,
    )
    dataset_example_id: Mapped[int] = mapped_column(
        ForeignKey('dataset_examples.id'),
        nullable=False,
        index=True,
    )
    rendered_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    evaluation_run: Mapped[EvaluationRun] = relationship(back_populates='results')
    dataset_example: Mapped[DatasetExample] = relationship(
        back_populates='evaluation_results',
    )
    metrics: Mapped[list['MetricResult']] = relationship(
        back_populates='evaluation_result',
        cascade='all, delete-orphan',
    )


class MetricResult(Base):
    __tablename__ = 'metric_results'
    __table_args__ = (
        UniqueConstraint(
            'evaluation_result_id',
            'metric_name',
            name='uq_metric_result_name_per_evaluation_result',
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    evaluation_result_id: Mapped[int] = mapped_column(
        ForeignKey('evaluation_results.id'),
        nullable=False,
        index=True,
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    evaluation_result: Mapped[EvaluationResult] = relationship(
        back_populates='metrics',
    )
