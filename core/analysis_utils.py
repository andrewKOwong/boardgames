from IPython.display import display, HTML
import pandas as pd


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


def print_spacer(num_lines: int = 2) -> None:
    """Print blank lines to space content appropriately.

    Args:
        num_lines (int): Number of blank lines to print.
    """
    print('\n'*num_lines)


def display_id_link(id: int) -> None:
    """Display a clickable link in a Jupyter notebook from boardgame id.

    Parameters
    ----------
    id : int
        The game id of interest.
    """
    BASE_URL = "https://boardgamegeek.com/boardgame/"
    display(HTML(f"<a href={BASE_URL + str(id)}>ID: {id}</a>"))


def print_null_count(
        df: pd.DataFrame,
        omit_zero_count: bool = True) -> None:
    print_titled_text("null counts")
    for colname, count in df.isnull().sum().items():
        if omit_zero_count and (count == 0):
            continue
        print(f"{colname}: {count}")
