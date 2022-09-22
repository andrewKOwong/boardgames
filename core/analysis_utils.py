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


def display_id_link(id: int, name: str = "") -> None:
    """Display a clickable link in a Jupyter notebook from boardgame id.

    Args:
        id (int): Game id.
        name (str, optional): Name of the game.
            Defaults to "".
    """
    BASE_URL = "https://boardgamegeek.com/boardgame/"
    display(HTML(f"<a href={BASE_URL + str(id)}>ID: {id} {name}</a>"))


def display_id_links_from_df(
        df: pd.DataFrame,
        id_key: str = 'id',
        name_key: str = 'name') -> None:
    """Display clickable links in a Jupyter notebook from a dataframe.

    Best used with a small length dataframe (such as df.head() or df.samp(10)),
    to keep print length reasonable.

    Args:
        df (pd.DataFrame): Dataframe to print from
        id_key (str, optional): Key of id column.
            Defaults to 'id'.
        name_key (str, optional): Key of name column.
            Defaults to 'name'.
    """
    for row in df.loc[:, [id_key, name_key]].iterrows():
        display_id_link(row[1][id_key], name=row[1][name_key])


def print_null_count(
        df: pd.DataFrame,
        omit_zero_count: bool = True) -> None:
    print_titled_text("null counts")
    for colname, count in df.isnull().sum().items():
        if omit_zero_count and (count == 0):
            continue
        print(f"{colname}: {count}")
