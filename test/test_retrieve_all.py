import requests
import json
from math import ceil
from pathlib import Path
from itertools import cycle

from core.bgg import Retriever


class MockResponse:
    """Mock of requests.Response"""
    def __init__(self, status_code: int, text: str):
        """Init MockResponse with desired values.

        Args:
            status_code (int): mocking requests.Response.status_code.
            text (str): mocking requests.Response.text. Will also be
                converted to a bytes object mocking requests.Response.content.
        """
        self.status_code = status_code
        self.text = text
        self.content = bytes(text, encoding='utf-8')


class MockServer:
    """Use MockServer.get_response as monkeypatch for requests.get"""
    def __init__(self) -> None:
        # This is a cyclic iterator that will
        # yield items in a loop when calling next() on it
        self.response_cycle = cycle([
            (200, 'DOWNLOADED'),
            (202, 'QUEUED'),
            (429, 'RATE_LIMITED'),
            (502, 'try again in 30 seconds'),
            (502, 'OTHER ERROR'),
            (503, 'SERVICE UNAVAILABLE')
            ])

    def get_response(self, uri) -> MockResponse:
        """Get the next MockReponse in the cycle.

        Returns:
            MockResponse: mocking request.Response, with .status_code,
                .text, and .content.
        """
        code, text = next(self.response_cycle)
        return MockResponse(code, text)


def test_retrieve_all_progress(monkeypatch, tmp_path):
    TEST_BATCH_SIZE = 2
    TEST_MAX_ID = 13
    TEST_BATCH_COOLDOWN = 1
    TEST_SERVER_COOLDOWN = 1
    # On Linux, tmp_path for most recent test should be at
    # /tmp/pytest-of-<user>/pytest-current
    TEST_DIR = tmp_path
    TEST_RANDOM_SEED = 7

    # Patch out requests.get
    server = MockServer()
    monkeypatch.setattr(requests, 'get', server.get_response)

    # Run retrieve all, but with a smaller max id,
    # so a smaller amount of items are returned.
    retriever = Retriever(save_dir=TEST_DIR)
    retriever.retrieve_all(
        batch_size=TEST_BATCH_SIZE,
        shuffle=True,
        random_seed=TEST_RANDOM_SEED,
        max_id=TEST_MAX_ID,
        batch_cooldown=TEST_BATCH_COOLDOWN,
        server_cooldown=TEST_SERVER_COOLDOWN
    )

    # Reload from the progress file for testing
    progress_path = Path(retriever.progress_path)
    progress = json.loads(progress_path.read_text())
    # Test the number of batches
    assert len(progress) == ceil(TEST_MAX_ID/TEST_BATCH_SIZE)
    # Test the first batch ids
    assert progress[0][retriever.PROGRESS_KEY_IDS] == [4, 11]
    # Test the last batch ids
    assert progress[-1][retriever.PROGRESS_KEY_IDS] == [6]
    # Test all status are correct
    correct_statuses = [
        'complete', 'queued', 'incomplete',
        'incomplete', 'incomplete', 'incomplete', 'complete']
    test_statuses = [e[retriever.PROGRESS_KEY_STATUS] for e in progress]
    assert test_statuses == correct_statuses

    # Print the progress object for convenience in inspection
    print(progress)
