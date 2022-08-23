import os
import sys
from pathlib import Path
import json
from time import sleep
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
    DIR_XML_PATH_STR = 'xml'
    DIR_PROGRESS_PATH = 'progress'

    def __init__(self, save_dir):
        save_dir = Path(save_dir)
        if not save_dir.exists():
            raise FileNotFoundError(f"Dir {str(save_dir)} does not exist.")
        if not save_dir.is_dir():
            raise NotADirectoryError(f"{str(save_dir)} is not a directory.")

        xml_dir = save_dir / self.DIR_XML_PATH_STR
        self.xml_dir = str(xml_dir)
        progress_path = save_dir / self.DIR_PROGRESS_PATH
        self.progress_path = str(progress_path)

    def api_request(self, uri):
        """Make a request for board game geek data.

        Args:
            uri (str): String URI for accessing the API.

        Returns:
            requests.models.Response: response from the HTTP request.
        """
        r = requests.get(uri)
        return r

    def retrieve_all(self, server_cooldown=12*60*60):
        # Resume from an existing progress file
        # or create new progress object and batches.
        if self.check_progress_file_exists():
            progress = self.load_progress_file()
        else:
            ids = [i for i in range(1, self.MAX_ID + 1)]
            progress = self.create_progress_object(ids, batch_size=1000)

        self.save_progress_file(progress)  # Initial save
        # Loop progress object, ignoring already complete batches.
        for idx, batch in enumerate(progress.copy()):
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
                        pause_time = 600
                        print(f"Unable to connect to internet, "
                              f"pausing {pause_time} seconds.")
                        sleep(pause_time)
                        continue
                # If its 200, save the file, change status to complete
                # If it's 202, mark it as queued.
                # Anything else, could mean server blocking or down,
                # so wait a while, then try again.
                if r.status_code == 200:
                    batch[self.PROGRESS_KEY_STATUS] == \
                        self.PROGRESS_STATUS_COMPLETE
                    progress[idx] = batch
                    self.save_progress_file(progress)
                if r.status_code == 202:
                    batch[self.PROGRESS_KEY_STATUS] == \
                        self.PROGRESS_STATUS_QUEUED
                    progress[idx] = batch
                    self.save_progress_file(progress)
                else:
                    message = (
                        f"Response {r.status_code}. "
                        f"Waiting {server_cooldown} seconds before continuing."
                    )
                    print(message)
                    self._countdown(server_cooldown)

            # Load progress file at the end and count up how many incompletes.
            # Also, data actually has to be saved somehow.

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
            json.dump(progress, f)

    def load_progress_file(self) -> dict:
        """Returns a dict from save path json file."""
        with open(self.progress_path, 'r') as f:
            progress = json.load(f)
        return progress

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

    def _countdown(time_to_sleep: int) -> None:
        """Prints a countdown timer."""
        for i in range(time_to_sleep, 0, -1):
            h = i // 3600
            m = (i % 3600) // 60
            s = (i % 3600) % 60
            # Countdown in place without new lines
            print(f"\rResuming in {h}h {m}m {s}s", end='')
            sleep(1)
        print(f"\rResuming in {0}h {0}m {0}s")
