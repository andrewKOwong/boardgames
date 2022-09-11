from IPython.display import display, HTML


def display_id_link(id: int) -> None:
    """Display a clickable link in a Jupyter notebook from boardgame id.

    Parameters
    ----------
    id : int
        The game id of interest.
    """
    BASE_URL = "https://boardgamegeek.com/boardgame/"
    display(HTML(f"<a href={BASE_URL + str(id)}>ID: {id}</a>"))
