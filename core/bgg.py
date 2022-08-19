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