import argparse
from core.bgg import Retriever


# Use command line args to set retrieve_all() params
parser = argparse.ArgumentParser(
    description="Retrieves all boardgames from Board Game Geek via API.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
    '--save-dir',
    metavar='',
    dest='save_dir',
    type=str,
    default='./data',
    help="Directory to save downloaded data, logs, and other files.")

parser.add_argument(
    '--batch-size',
    metavar='',
    dest='batch_size',
    type=int,
    default=300,
    help="Number of ids to sent per API request.")

parser.add_argument(
    '--batch-cooldown',
    metavar='',
    dest='batch_cooldown',
    type=int,
    default=5*60,
    help="Number of seconds to cooldown wait between batches.")

parser.add_argument(
    '--server-cooldown',
    metavar='',
    dest='server_cooldown',
    type=int,
    default=3*60*60,
    help="Number of seconds to cooldown wait"
         " when encountering a server error.")

parser.add_argument(
    '--max-id',
    metavar='',
    dest='max_id',
    type=int,
    default=None,
    help="Max 'thing' id to download up to."
)

parser.add_argument(
    '--no-shuffle',
    dest='shuffle',
    action='store_false',
    default=True,
    help="Disable shuffling of 'thing' ids while downloading."
)

parser.add_argument(
    '--random-seed',
    metavar='',
    dest='random_seed',
    type=int,
    default=None,
    help="Random seed for id shuffling.")

parser.add_argument(
    '--clear-progress',
    dest='clear_progress',
    action='store_true',
    default=False,
    help="Clear progress file if already present in save directory."
)

args = parser.parse_args()

retriever = Retriever(args.save_dir)

if args.clear_progress:
    retriever.remove_progress_file()

retriever.retrieve_all(
    batch_size=args.batch_size,
    batch_cooldown=args.batch_cooldown,
    server_cooldown=args.server_cooldown,
    max_id=args.max_id,
    shuffle=args.shuffle,
    random_seed=args.random_seed
)
