from IPython.display import display, HTML


def print_titled_text(
        title: str,
        underliner='=',
        upper=True):
    """Prints the text underlined to the same length with underliner char.

    Args:
        title (str): String to pring
        underliner (str, optional): Char to underline the title.
            Defaults to '='.
        upper (bool, optional): Convert to all uppercase.
            Defaults to True.
    """
    if upper:
        title = title.upper()
    print(title)
    print(underliner*len(title))


def display_id_link(id: int) -> None:
    """Display a clickable link in a Jupyter notebook from boardgame id.

    Parameters
    ----------
    id : int
        The game id of interest.
    """
    BASE_URL = "https://boardgamegeek.com/boardgame/"
    display(HTML(f"<a href={BASE_URL + str(id)}>ID: {id}</a>"))
