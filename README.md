# Columbus and New York

[Reid Fournier](https://github.com/reidfournier). Miami University.

Inside Airbnb. [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).

- Columbus: 2,959 listings. September 22, 2026.
- New York: 29,918 listings. September 14, 2026.

325 Columbus listings and 10,512 New York listings have no price. The price figures use the rest. Each city then drops the cheapest and dearest 0.5%. Columbus keeps 2,606 listings. New York keeps 19,211.

The bathroom count is read from the bathroom text. The bathrooms column is empty in both files. The host-total column is empty in both files. Hosts are counted with `calculated_host_listings_count`, the host's listings in that city. A neighborhood enters a rank only when it has 30 or more priced listings.

## Price

The typical night is the median.

Columbus median: $163. Mean: $205.49.

New York median: $182.46. Mean: $283.29.

The earlier page used the September 26, 2025 Columbus file and the June 14, 2026 New York file. Those means were $137.12 and $252.62.

Neighborhoods with 30 or more priced listings:

- Columbus: Far Northwest $246.50 (30 listings), Clintonville $190.83 (96), Near North/University $179.25 (764).
- New York: Tribeca $603.70 (69), Financial District $569.50 (318), SoHo $567 (142).

## Calendars

Open nights are not booked nights.

The median listing is open 283 nights in Columbus and 227 nights in New York.

Among neighborhoods with 30 or more priced listings, Franklinton leads Columbus at 327.5 open nights. The median price there is $162. Wakefield leads New York at 358 open nights. The median price there is $97.23. The next neighborhoods sit close behind. A high bar on that chart is an empty calendar.

## Hosts

The count is the same kind in both cities.

Columbus has 1,023 hosts. 61.1% have one listing in the city. Hosts with more than one listing hold 78.9% of the rows.

New York has 16,148 hosts. 80.2% have one listing in the city. Hosts with more than one listing hold 56.7% of the rows.

## Rooms

Columbus is 81.8% entire homes and 17.3% private rooms.

New York is 54.8% entire homes, 43.0% private rooms, and 1.5% hotel rooms.

On the priced listings, a Columbus entire home has a median night of $181.50. A New York entire home has a median night of $216.98. A New York hotel room has a median night of $623, across 407 listings. Columbus has 24 hotel rooms in the priced set. Their median is $161.08.

Guest capacity tracks price. The correlation is 0.641 in Columbus and 0.422 in New York. Bedrooms and the bathroom count come next. Review count does not.

## Run

`analysis.py` downloads the two files into `data/` and writes the five charts. The listing files are not in this repo.

The files are the September 22, 2026 Columbus extract and the September 14, 2026 New York extract from [Inside Airbnb](https://insideairbnb.com/get-the-data/).
