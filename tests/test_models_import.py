from app.db.models import Dataset
from app.db.models import DatasetExample
from app.db.models import EvaluationResult
from app.db.models import EvaluationRun
from app.db.models import MetricResult
from app.db.models import ModelConfiguration
from app.db.models import ModelProvider
from app.db.models import Prompt
from app.db.models import PromptVersion



def test_domain_models_are_importable() -> None:
    assert Prompt is not None
    assert PromptVersion is not None
    assert Dataset is not None
    assert DatasetExample is not None
    assert ModelProvider is not None
    assert ModelConfiguration is not None
    assert EvaluationRun is not None
    assert EvaluationResult is not None
    assert MetricResult is not None
