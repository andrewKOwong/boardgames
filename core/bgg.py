import os
import sys
import json
from time import sleep
import requests

def generate_game_uri(
    ids: list = None,
    filter_basegame: bool = True,
    filter_expansion: bool = False,
    stats: bool = True,
    base_api_endpoint: str = "https://boardgamegeek.com/xmlapi2/thing?"
    ) -> str:
    """Construct a URI to get one or more games based on their id.

    Parameters
    ----------
    ids : list, optional
        list of numerical ids of the board games, by default []
    filter_basegame : boolean, optional
        filter for base board games, by default True.
    filter_expansion : boolean, optional
        filter for board game expansions, by default False.
    stats : boolean, optional
        include statistics i.e. "stats=1" in the query.
    base_api_endpoint : str, optional
        Board Game Geek XML API2 endpoint for retrieving "thing" objects.
        Can be swapped for testing.

    Returns
    -------
    str URI
        URI accessing board games with specified ids.
    """
    # Thing types
    # Non-expansion games
    BASE_GAME_TYPE = "boardgame"
    # Expansions
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


    def __init__(self, save_path):
        self.save_path = save_path

    def api_request(self, uri):
        """Make a request for board game geek data.

        Parameters
        ----------
        uri : str
            String URI for accessing the API.

        Returns
        -------
        Response object
            The resulting response from the HTTP request.
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
                        uri = generate_game_uri(batch[self.PROGRESS_KEY_IDS])
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
                    sleep(server_cooldown)

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
            list: _description_
        """

        progress = [
            {self.PROGRESS_KEY_IDS: ids[i: i+batch_size],
             self.PROGRESS_KEY_STATUS: self.PROGRESS_STATUS_INCOMPLETE,
             self.PROGRESS_KEY_LAST_ACCESSED: ''}
            for i in range(0, len(ids), batch_size)]

        return progress

    def save_progress_file(self, progress: dict) -> None:
        """Takes the progress dict and saves it to the preloaded save path."""
        with open(self.save_path, 'w') as f:
            json.dump(progress, f)

    def load_progress_file(self) -> dict:
        """Returns a dict from save path json file."""
        with open(self.save_path, 'r') as f:
            progress = json.load(f)
        return progress

    def check_progress_file_exists(self) -> bool:
        """True if save file already exists."""
        return os.path.isfile(self.save_path)
