import requests
import json
from math import ceil
from pathlib import Path

from core.bgg import Retriever


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


# Testing if a mock server returns all 200 statuses
def test_200(monkeypatch, tmp_path):
    TEST_BATCH_SIZE = 2
    TEST_MAX_ID = 10
    TEST_DIR = tmp_path  # system temporary files
    TEST_STATUS_CODE = 200
    TEST_RANDOM_SEED = 7
    TEST_STATUS_STR = 'complete'
    # Manually change this to true if you want to inspect
    # the progress file.
    # This will dump the files into the stated directory,
    # as well as moving the progress file into a 'tmp_prog.json'
    # at the end of this test.
    INSPECT_PROGRESS_FILE = False
    TEST_DIR_INSPECT = Path('./exp')
    if INSPECT_PROGRESS_FILE:
        TEST_DIR = TEST_DIR_INSPECT

    # Patch out requests.get
    def mock_get(url):
        return MockResponse(status_code=TEST_STATUS_CODE)

    monkeypatch.setattr(requests, 'get', mock_get)

    # Run retrieve all, but with a smaller max id,
    # so a smaller amount of items are returned.
    retriever = Retriever(save_dir=TEST_DIR)
    retriever.MAX_ID = TEST_MAX_ID
    retriever.retrieve_all(batch_size=TEST_BATCH_SIZE,
                           shuffle=True,
                           random_seed=TEST_RANDOM_SEED)

    # Reload from the progress file for testing
    progress_path = Path(retriever.progress_path)
    progress = json.loads(progress_path.read_text())
    # Test the number of batches
    assert len(progress) == ceil(TEST_MAX_ID/TEST_BATCH_SIZE)
    # Test the first batch ids
    assert progress[0][retriever.PROGRESS_KEY_IDS] == [9, 4]
    # Test the last batch ids
    assert progress[-1][retriever.PROGRESS_KEY_IDS] == [3, 6]
    # Test all status are correct
    statuses = set([e[retriever.PROGRESS_KEY_STATUS] for e in progress])
    assert len(statuses) == 1
    assert statuses.pop() == TEST_STATUS_STR

    # Swap out the progress file so you can inspect it without
    # reloading the func
    if INSPECT_PROGRESS_FILE:
        progress_path.replace(progress_path.parent / 'tmp_prog.json')


# Testing if a mock server returns all 202 statuses
def test_202(monkeypatch, tmp_path):
    TEST_BATCH_SIZE = 2
    TEST_MAX_ID = 10
    TEST_DIR = tmp_path  # system temporary files
    TEST_STATUS_CODE = 202
    TEST_RANDOM_SEED = 7
    TEST_STATUS_STR = 'queued'
    # Manually change this to true if you want to inspect
    # the progress file.
    # This will dump the files into the stated directory,
    # as well as moving the progress file into a 'tmp_prog.json'
    # at the end of this test.
    INSPECT_PROGRESS_FILE = False
    TEST_DIR_INSPECT = Path('./exp')
    if INSPECT_PROGRESS_FILE:
        TEST_DIR = TEST_DIR_INSPECT

    # Patch out requests.get
    def mock_get(url):
        return MockResponse(status_code=TEST_STATUS_CODE)

    monkeypatch.setattr(requests, 'get', mock_get)

    # Run retrieve all, but with a smaller max id,
    # so a smaller amount of items are returned.
    retriever = Retriever(save_dir=TEST_DIR)
    retriever.MAX_ID = TEST_MAX_ID
    retriever.retrieve_all(batch_size=TEST_BATCH_SIZE,
                           shuffle=True,
                           random_seed=TEST_RANDOM_SEED)

    # Reload from the progress file for testing
    progress_path = Path(retriever.progress_path)
    progress = json.loads(progress_path.read_text())
    # Test the number of batches
    assert len(progress) == ceil(TEST_MAX_ID/TEST_BATCH_SIZE)
    # Test the first batch ids
    assert progress[0][retriever.PROGRESS_KEY_IDS] == [9, 4]
    # Test the last batch ids
    assert progress[-1][retriever.PROGRESS_KEY_IDS] == [3, 6]
    # Test all status are correct
    statuses = set([e[retriever.PROGRESS_KEY_STATUS] for e in progress])
    assert len(statuses) == 1
    assert statuses.pop() == TEST_STATUS_STR

    # Swap out the progress file so you can inspect it without
    # reloading the func
    if INSPECT_PROGRESS_FILE:
        progress_path.replace(progress_path.parent / 'tmp_prog.json')
