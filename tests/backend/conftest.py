from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

BASELINE_ACTIVITIES = deepcopy(activities)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(BASELINE_ACTIVITIES))

    yield

    activities.clear()
    activities.update(deepcopy(BASELINE_ACTIVITIES))
