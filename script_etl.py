import argparse
from core import etl

parser = argparse.ArgumentParser(
    description=(
        "Extract a folder of xml files containing boardgame data and "
        "save them as csv files. "
        "Saved files will have format: <save_csv_dir>/<save_file_prefix>"
        "_<data_type>.csv where <data_type> indicates whether the file "
        "contains general data, link data, or poll data."
    )
)

parser.add_argument(
    'read_xml_dir',
    type=str,
    help="Directory of xml files downloaded from BGG."
)

parser.add_argument(
    'save_csv_dir',
    type=str,
    help="Directory to save output csv files."
)

parser.add_argument(
    'save_prefix',
    type=str,
    help="Prefix for naming saved csv files."

)

parser.add_argument(
    '--omit-general-data',
    dest='omit_general_data',
    action='store_true',
    default=False,
    help="Flag to omit general data extraction."
)

parser.add_argument(
    '--omit-link-data',
    dest='omit_link_data',
    action='store_true',
    default=False,
    help="Flag to omit link data extraction."
)

parser.add_argument(
    '--omit-poll-data',
    dest='omit_poll_data',
    action='store_true',
    default=False,
    help='Flag to omit poll data extraction.'
)

args = parser.parse_args()

dict_of_dfs = etl.flatten_xml_folder_to_dataframe(
    args.read_xml_dir,
    get_general_data=(not args.omit_general_data),
    get_link_data=(not args.omit_link_data),
    get_poll_data=(not args.omit_poll_data)
)

etl.write_dataframes_to_csv(
    dict_of_dataframes=dict_of_dfs,
    save_dir_path=args.save_csv_dir,
    save_file_prefix=args.save_prefix
)
