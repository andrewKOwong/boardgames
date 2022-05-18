import bgg_data as b
from time import sleep

# Sample size
K = 500
# How many times to sample
N_REQUESTS = 8
# Time (s) between sampling request
# to avoid excessive load.
WAIT_TIME = 300
# File naming
OUT_PATH_PREFIX = "./data/sample_"
OUT_SUFFIX = ".xml"

# Repeat sample N_REQUEST times
for i in range(1, N_REQUESTS+1):
    # Get sample size k
    r = b.sample_random_ids(k=K)
    # If the query has a filter for board games
    # the number of items will be less than the
    # sample size. Expect ~30% of ids are board games.
    # Display this count.
    print(f"Request {i} contains {b.count_items(r)} items.")
    # Save each sample to individual files.
    b.write_response(r,
                     f"{OUT_PATH_PREFIX}"
                     f"{str(K)}_{i}"
                     f"{OUT_SUFFIX}"
                     )
    # Sleep to avoid hammering the server.
    sleep(WAIT_TIME)
