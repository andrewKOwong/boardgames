# boardgames

## Retrieving the data

BoardGameGeek provides an [XML API](https://boardgamegeek.com/wiki/page/BGG_XML_API2). To avoid excessive load on the server and getting locked out, I sampled the ~360k "things" on BoardGameGeek in batches of 500 for 8 times (with replacement, with duplicates removed later), while filtering for `type=boardgame` as opposed to `boardgameexpansion` or `boardgameaccessory`. I included a 300 second wait time between samples.

This can be reproduced by running `python sample_boardgames.py`, although you could manually edit the sampling size, number of requests, wait time, and filepaths.

## Possible improvements

I sampled essentially with replacement, but one could rewrite the sampling function to generate a non-duplicated list of ids of the desired final size and then break that into chunks.

`sample_boardgames.py` would benefit from an arg parser.
