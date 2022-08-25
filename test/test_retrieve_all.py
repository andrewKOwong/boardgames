import pytest
import requests
import types
import json
from functools import partial, partialmethod
from math import ceil
from pathlib import Path

from core.bgg import Retriever


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def test_200(monkeypatch, tmp_path):
    TEST_BATCH_SIZE = 2
    TEST_MAX_ID = 10
    TEST_DIR = Path('./exp')  # or tmp_path

    def mock_get(url):
        return MockResponse(status_code=200)

    monkeypatch.setattr(requests, 'get', mock_get)

    retriever = Retriever(save_dir=TEST_DIR)
    retriever.MAX_ID = TEST_MAX_ID

    retriever.retrieve_all(batch_size=TEST_BATCH_SIZE,
                           shuffle=True,
                           random_seed=7)

    progress_path = Path(retriever.progress_path)

    # Reload from the progress file
    progress = json.loads(progress_path.read_text())
    # Test the number of batches
    assert len(progress) == ceil(TEST_MAX_ID/TEST_BATCH_SIZE)
    # Test the first batch ids
    assert progress[0][retriever.PROGRESS_KEY_IDS] == [9, 4]
    # Test the last batch ids
    assert progress[-1][retriever.PROGRESS_KEY_IDS] == [3, 6]
    # Test all status are 'complete'
    statuses = set([e[retriever.PROGRESS_KEY_STATUS] for e in progress])
    assert len(statuses) == 1
    assert statuses.pop() == 'complete'

    temp_progress = progress_path.replace(progress_path.parent / 'tmp_prog.json')