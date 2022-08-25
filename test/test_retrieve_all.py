import pytest
import requests
import types
import json
from functools import partial, partialmethod
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

    retriever.retrieve_all(batch_size=TEST_BATCH_SIZE)

    progress_path = Path(retriever.progress_path)
    temp_progress = progress_path.replace(progress_path.parent / 'tmp_prog.json')

    progress = json.loads(temp_progress.read_text())

    assert 1 == 1
