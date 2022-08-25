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

    # Patching via a wrapper to discard batch size arg
    # and use `replace` for batch size instead.
    # This is necessary to override method calls in
    # `self.retrieve_all()` that provide batch size.
    # Not sure if best way, but couldn't get monkeypatch to work.
    def batch_size_wrapper(
            self,
            ids,
            batch_size=None,
            replace=TEST_BATCH_SIZE):
        return Retriever.create_progress_object(self, ids, batch_size=replace)

    retriever.create_progress_object = \
        types.MethodType(batch_size_wrapper, retriever)

    retriever.retrieve_all()

    progress_path = Path(retriever.progress_path)
    temp_progress = progress_path.replace(progress_path.parent / 'tmp_prog.json')

    progress = json.loads(temp_progress.read_text())

    assert 1 == 1
