import argparse
from core import etl

parser = argparse.ArgumentParser(
    description=(
        "Extract a folder of xml files containing boardgame data and "
        "save them as parquet (default) or csv files. "
        "Saved files will have format: <output_dir>/<output_prefix>"
        "_<data_type>.<parquet|csv|csv.gz> where <data_type> indicates whether"
        "the file contains general data, link data, or poll data."
    )
)

parser.add_argument(
    'read_xml_dir',
    type=str,
    help="Directory of xml files downloaded from BGG."
)

parser.add_argument(
    'output_dir',
    type=str,
    help="Directory to save output parquet (default) or csv files."
)

parser.add_argument(
    'output_prefix',
    type=str,
    help="Prefix for naming output files."

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

parser.add_argument(
    '--output-csv',
    dest='output_csv',
    action='store_true',
    default=False,
    help='Output files as csv instead of parquet.'
)

parser.add_argument(
    '--omit-csv-compression',
    dest='omit_csv_compression',
    action='store_true',
    default=False,
    help="Omit gunzip compression of csv files."
)

args = parser.parse_args()

dict_of_dfs = etl.flatten_xml_folder_to_dataframe(
    args.read_xml_dir,
    get_general_data=(not args.omit_general_data),
    get_link_data=(not args.omit_link_data),
    get_poll_data=(not args.omit_poll_data)
)

if args.output_csv:
    etl.write_dataframes_to_csv(
        dict_of_dataframes=dict_of_dfs,
        save_dir_path=args.output_dir,
        save_file_prefix=args.output_prefix,
        compress_csv=(not args.omit_csv_compression)
    )
else:
    etl.write_dataframes_to_parquet(
        dict_of_dataframes=dict_of_dfs,
        save_dir_path=args.output_dir,
        save_file_prefix=args.output_prefix
    )
