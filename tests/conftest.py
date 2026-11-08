from __future__ import annotations

import pytest

from data_eval_factory.evaluation.runner import Runtime, execute
from data_eval_factory.schemas.evaluation import FactoryReport


@pytest.fixture(scope="session")
def runtime() -> Runtime:
    return execute()


@pytest.fixture(scope="session")
def report(runtime: Runtime) -> FactoryReport:
    return runtime.report
