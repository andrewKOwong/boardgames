import os
from pathlib import Path
import json
import random
import logging
import sys
from copy import deepcopy
from datetime import datetime
from time import sleep, time
import requests


def xml_collater():
    pass


class Retriever:
    MAX_ID = 362383
    PROGRESS_STATUS_COMPLETE = 'complete'
    PROGRESS_STATUS_INCOMPLETE = 'incomplete'
    PROGRESS_STATUS_QUEUED = 'queued'
    PROGRESS_KEY_IDS = "ids"
    PROGRESS_KEY_STATUS = "status"
    PROGRESS_KEY_LAST_ACCESSED = "last_accessed"
    BASE_API = "https://boardgamegeek.com/xmlapi2/thing?"
    PATH_XML_DIR = 'xml'
    PATH_PROGRESS_FILE = 'progress.json'
    PATH_LOG_FILE = 'retriever.log'
    PAUSE_TIME_NO_CONNECTION = 60

    def __init__(self, save_dir):
        save_dir = Path(save_dir)
        if not save_dir.exists():
            raise FileNotFoundError(f"Dir {str(save_dir)} does not exist.")
        if not save_dir.is_dir():
            raise NotADirectoryError(f"{str(save_dir)} is not a directory.")

        xml_dir = save_dir / self.PATH_XML_DIR
        xml_dir.mkdir(exist_ok=True)
        self.xml_dir = str(xml_dir)
        progress_path = save_dir / self.PATH_PROGRESS_FILE
        self.progress_path = str(progress_path)
        log_file_path = save_dir / self.PATH_LOG_FILE
        self.log_file_path = str(log_file_path)
        self.logger = RetrieverLogger(self.log_file_path)

    def api_request(self, uri):
        """Make a request for board game geek data.

        Args:
            uri (str): String URI for accessing the API.

        Returns:
            requests.models.Response: response from the HTTP request.
        """
        r = requests.get(uri)
        return r

    def retrieve_all(
            self,
            server_cooldown=12*60*60,
            batch_size=1000,
            shuffle=True,
            random_seed=None):
        log = self.logger
        log.reset()
        log.log_run_start()
        # Resume from an existing progress file
        # or create new progress object and batches.
        if self.check_progress_file_exists():
            log.log_resuming_from_file()
            progress = self.load_progress_file()
        else:
            log.log_new_progress_file()
            ids = [i for i in range(1, self.MAX_ID + 1)]
            if shuffle:
                random.seed(random_seed)
                random.shuffle(ids)
            progress = self.create_progress_object(ids, batch_size=batch_size)
            self.save_progress_file(progress)  # Initial save

        log.log_total_batches(progress)
        # Loop progress object, ignoring already complete batches.
        # Defensively deepcopy since we're altering during iteration.
        for idx, batch in enumerate(deepcopy(progress)):
            if batch[self.PROGRESS_KEY_STATUS] == \
                    self.PROGRESS_STATUS_COMPLETE:
                continue
            else:
                # Try the request, but pause 10 min if no internet
                while True:
                    try:
                        uri = self.generate_game_uri(
                            batch[self.PROGRESS_KEY_IDS]
                            )
                        r = self.api_request(uri)
                        break
                    except requests.ConnectionError:
                        print(f"Unable to connect to internet, "
                              f"pausing {self.PAUSE_TIME_NO_CONNECTION}"
                              f" seconds.")
                        self._countdown(self.PAUSE_TIME_NO_CONNECTION)
                        continue
                # First, no matter the result, save the access time
                batch[self.PROGRESS_KEY_LAST_ACCESSED] = \
                    datetime.now().strftime('%Y-%b-%d %H:%M:%S.%f')
                # If its 200, save the file, change status to complete
                # If it's 202, mark it as queued.
                # Anything else, could mean server blocking or down,
                # so wait a while, then try again.
                if r.status_code == 200:
                    batch[self.PROGRESS_KEY_STATUS] = \
                        self.PROGRESS_STATUS_COMPLETE
                    progress[idx] = batch
                    self._write_response(r, self.xml_dir + f'/{idx}.xml')
                    self.save_progress_file(progress)
                    # TODO log batch statistics
                    # TODO update cumulative data
                    # TODO update estimated time for completion
                elif r.status_code == 202:
                    batch[self.PROGRESS_KEY_STATUS] = \
                        self.PROGRESS_STATUS_QUEUED
                    progress[idx] = batch
                    self.save_progress_file(progress)
                    # TODO log queued
                else:
                    # TODO log server error
                    print(r.text, '\n')
                    message = (
                        f"Response {r.status_code}. \n"
                        f"See contents above. \n"
                        f"Waiting {server_cooldown} seconds before continuing."
                    )
                    print(message)
                    self._countdown(server_cooldown)
        # TODO log total number of batches success/cued/incomplete, cumulative data

    def create_progress_object(
            self,
            ids: list,
            batch_size: int = 1000) -> list:
        """Batchify list of ids, returning progress object with statuses per batch.

        Args:
            ids (list): BGG thing ids e.g. board games.
            batch_size (int, optional): Defaults to 1000.

        Returns:
            list: of dicts containing batches of ids and status info
        """

        progress = [
            {self.PROGRESS_KEY_IDS: ids[i: i+batch_size],
             self.PROGRESS_KEY_STATUS: self.PROGRESS_STATUS_INCOMPLETE,
             self.PROGRESS_KEY_LAST_ACCESSED: ''}
            for i in range(0, len(ids), batch_size)]

        return progress

    def save_progress_file(self, progress: dict) -> None:
        """Takes the progress dict and saves it to the preloaded save path."""
        with open(self.progress_path, 'w') as f:
            json.dump(progress, f, indent=4)

    def load_progress_file(self) -> dict:
        """Returns a dict from save path json file."""
        with open(self.progress_path, 'r') as f:
            progress = json.load(f)
        return progress

    def remove_progress_file(self) -> None:
        """Deletes the progress file at the save path, regardless of existence."""
        Path(self.progress_path).unlink(missing_ok=True)

    def check_progress_file_exists(self) -> bool:
        """True if save file already exists."""
        return os.path.isfile(self.progress_path)

    def generate_game_uri(
        self,
        ids: list = None,
        filter_basegame: bool = True,
        filter_expansion: bool = False,
        stats: bool = True,
        base_api_endpoint: str = BASE_API
    ) -> str:
        """Construct a URI to get one or more games based on their id.

        Args:
            ids (list, optional): numerical ids of the board games.
                Defaults to None.
            filter_basegame (bool, optional): filter for base board games.
                Defaults to True.
            filter_expansion (bool, optional): filter for
                board game expansions. Defaults to False.
            stats (bool, optional): include statistics
                i.e. "stats=1" in the query. Defaults to True.
            base_api_endpoint (str, optional): Board Game Geek XML API2
                endpoint for retrieving "thing" objects. Defaults to BASE_API.

        Returns:
            str:  URI accessing board games with specified ids.
        """
        # Thing types
        BASE_GAME_TYPE = "boardgame"  # i.e. non expansions
        EXPANSION_TYPE = "boardgameexpansion"

        # Instantiated empty list
        if ids is None:
            ids = []

        # Set up the output
        uri = base_api_endpoint

        # Add type filters
        uri += "type="
        if filter_basegame:
            uri += BASE_GAME_TYPE + ','
        if filter_expansion:
            uri += EXPANSION_TYPE + ','
        uri += '&'

        # Add stats query
        if stats:
            uri += "stats=1&"

        # Add ids
        uri += "id="
        # i.e. [1,2] -> '1,2'
        uri += ','.join([str(i) for i in ids])
        return uri

    def _countdown(self, time_to_sleep: int) -> None:
        """Prints a countdown timer."""
        for i in range(time_to_sleep, 0, -1):
            h = i // 3600
            m = (i % 3600) // 60
            s = i % 60
            # Countdown in place without new lines
            print(f"\rResuming in {h}h {m:02}m {s:02}s", end='')
            sleep(1)
        print(f"\rResuming in {0}h {0:02}m {0:02}s")

    def _write_response(
            self,
            response: requests.Response,
            out_path: str) -> None:
        """Write the content of a response to a file.

        Args:
            response (requests.Response): Response object
            out_path (str): location to write the file
        """
        with open(out_path, 'wb') as f:
            f.write(response.content)


class RetrieverLogger:
    """Convenience class for logging from Retriever."""
    def __init__(self, log_file_path) -> None:
        self.time_start = None
        self.time_end = None
        self.log_file_path = log_file_path
        self.total_batches = None

        # Set up logger
        logger = logging.getLogger('retriever')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s: %(message)s"
            )
        console_logging = logging.StreamHandler(stream=sys.stdout)
        console_logging.setLevel(logging.DEBUG)
        console_logging.setFormatter(formatter)
        logger.addHandler(console_logging)
        file_logging = logging.FileHandler(self.log_file_path)
        file_logging.setLevel(logging.DEBUG)
        file_logging.setFormatter(formatter)
        logger.addHandler(file_logging)
        self.logger = logger

    def log_run_start(self):
        self.time_start = time()
        self.logger.info("***STARTING RETRIEVER RUN***")

    def log_run_complete(self):
        self.time_end = time()
        total_time = round(self.time_end - self.time_start)
        total_time = self._seconds_to_time(total_time)
        self.logger.info(f"Retriever ran for {total_time}")
        self.logger.info("***ENDING RETRIEVER RUN***")

    def log_resuming_from_file(self):
        self.logger.info("Resuming from existing progress file.")

    def log_new_progress_file(self):
        self.logger.info("Creating new progress file.")

    def log_total_batches(self, progress: list[dict]) -> None:
        """Log number of batches in a progress object."

        Args:
            progress (dict): a progress object, which is a list of dicts
                from Retriever.create_progress_object()
        """
        self.total_batches = len(progress)
        self.logger.info(f"Starting run of {self.total_batches} batches.")

    def log_server_error(self):
        pass

    def log_batch_stats(self):
        pass

    def reset(self):
        """Reset internal variables at start of a retrieval run."""
        self.__init__(self)

    def _seconds_to_time(self, seconds: int) -> str:
        """Converts number of seconds to str in h m s format."""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{0}h {0:02}m {0:02}s"