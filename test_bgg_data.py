import bgg_data as b


def test_get_game_uri():
    ids = [1, 2]
    "https://boardgamegeek.com/xmlapi2/thing?"

    # Get base games only
    assert b.generate_game_uri(
        ids) == "https://boardgamegeek.com/xmlapi2/thing?type=boardgame,&stats=1&id=1,2"

    # Get expansions only
    assert b.generate_game_uri(
        ids,
        filter_basegame=False,
        filter_expansion=True) == "https://boardgamegeek.com/xmlapi2/thing?type=boardgameexpansion,&stats=1&id=1,2"

    # Get base + expansions
    assert b.generate_game_uri(
        ids,
        filter_basegame=True,
        filter_expansion=True) == "https://boardgamegeek.com/xmlapi2/thing?type=boardgame,boardgameexpansion,&stats=1&id=1,2"

    # No filter
    assert b.generate_game_uri(
        ids,
        filter_basegame=False,
        filter_expansion=False) == "https://boardgamegeek.com/xmlapi2/thing?type=&stats=1&id=1,2"

    # no stats
    assert b.generate_game_uri(
        ids,
        stats=False) == "https://boardgamegeek.com/xmlapi2/thing?type=boardgame,&id=1,2"

    # single id only
    assert b.generate_game_uri(
        ids=[35],
        stats=False) == "https://boardgamegeek.com/xmlapi2/thing?type=boardgame,&id=35"
