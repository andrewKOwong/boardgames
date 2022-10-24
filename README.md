# boardgames (Work-In-Progress)

This is a work-in-progress repo. The intention is to get data on all boardgames
on boardgamegeek.com and analyze it.


## Project Summary

## Instructions
### Description of Files
- `core/bgg.py` contains library code for downloading board games from BGG
- `core/etl.py` contains library code for extracting downloaded XML files
- `data` contains extracted board game data as `*.parquet` files under the `parquet` subfolder. `data` can also be used as the directory for downloaded xml files
- `test` contains testing files using the `pytest` testing framework
- `script_retrieve_all_boardgames.py` is a script for downloading boardgames, using library code from `core/bgg.py`. Use `python script_retrieve_allgames.py -h` to see all parameters.
- `script_etl.py` is a script for extracting XML data, using library code from `core/etl.py`. Use `python script_etl.py -h` to see all parameters.


### Libraries Required
- `python` 3.10+
- `pandas`
- `numpy

### Downloading Boardgames from BGG

To download all board games, run in the project root folder:
 ```sh
python script_retrieve_all_boardgames.py --save_dir <path_to_folder>
 ```
This will download all boardgames in batches of 500, with 5 minutes of wait time between batches and 3 hours of wait time if there's a server error. These are very conservative wait times (may take 30 hours in total), you may want to shorten them using `--batch-cooldown` and `--server-cooldown` flags. Use `--help` to see all command line args.

As the maximum board game id in use by BGG will increase in the future, use `--max-id` to set a higher maximum id.

### ETL on Downloaded XML-formatted Data
To extract downloaded XML data, run in the project root folder:
```sh
python script_etl.py <path_to_folder_containing_xml_files> <path_to_output_folder> <prefix_for_extracted_files>
```
By default, this extracts the data to `parquet` files. Use `--help` to see flags for `csv` output, turning off compression, and omitting some data extraction.

### Running Tests
In the project root directory, run `pytest`. Alternatively, run `pytest -sv` to see logging output from `stdout` as it is happening, or `pytest -rA` for better formatted logging output after the tests have finished running.

## TODO Analysis
- jupyter
- blog post
