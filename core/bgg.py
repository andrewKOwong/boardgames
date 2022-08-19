import os
import json

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
    def __init__(self, save_path):
        self.save_path = save_path

    def api_request(self):
        pass

    def sample(self):
        pass

    def retrieve_all(self):
        # Pseudo code:
        # 1) Check if save_path file exists
        # 2) If it exists, load a progress object from it.
        # 3) If it doesn't exist, generate list of ids from 1 to max id,
        #, then create a progress object that batchifies this
        # 4) Loop through progress object, updating it and saving it everytime.

        pass

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
            {'ids': ids[i: i+batch_size],
             'status': '',
             'last_accessed': ''}
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
