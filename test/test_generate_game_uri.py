from core.bgg import Retriever


# Testing that game URIs are generated correctly
def test_get_game_uri(tmp_path):
    API_ROOT = "https://boardgamegeek.com/xmlapi2/thing?"

    retriever = Retriever(tmp_path)
    func = retriever.generate_game_uri

    ids = [1, 2]

    # Get base games only
    assert func(
        ids) == API_ROOT + "type=boardgame,&stats=1&id=1,2"

    # Get expansions only
    assert func(
        ids,
        filter_basegame=False,
        filter_expansion=True) == API_ROOT + \
        "type=boardgameexpansion,&stats=1&id=1,2"

    # Get base + expansions
    assert func(
        ids,
        filter_basegame=True,
        filter_expansion=True) == API_ROOT + \
        "type=boardgame,boardgameexpansion,&stats=1&id=1,2"

    # No filter
    assert func(
        ids,
        filter_basegame=False,
        filter_expansion=False) == API_ROOT + "type=&stats=1&id=1,2"

    # no stats
    assert func(
        ids,
        stats=False) == API_ROOT + "type=boardgame,&id=1,2"

    # single id only
    assert func(
        ids=[35],
        stats=False) == API_ROOT + "type=boardgame,&id=35"
