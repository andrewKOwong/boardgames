import os

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


def file_utility_of_some_sort():
    """
    Track progress somehow.
    JSON would be straight forward.

    Keep track of batches, status of batches (200, 202, rejection).

    list of {batch id, game ids, status (complete, incomplete, queued, last accessed)}

    Inefficient solution is to loop through and do the ones that are queued.

    Random state should be optional.

    """
    pass


class Retriever:
    def __init__(self, save_path):
        self.save_path = save_path

    def api_request(self):
        pass

    def sample(self):
        pass

    def retrieve_all(self):
        pass

    def create_progress_file(self):
        pass

    def load_progress_file(self):
        pass

    def check_progress_file_exists(self):
        """True if save file already exists."""
        return os.path.isfile(self.save_path)
