# Airbnb Market Analysis: Columbus vs New York

## Author
[Reid Fournier]

## Project Overview
This project analyzes Airbnb listing data to compare the Columbus, Ohio and New York City markets. The goal is to help a prospective host or investor decide which market offers stronger return potential, informing decisions on pricing strategy, listing type, and neighborhood selection based on real demand, competition, and host concentration patterns in each city.

## Research Questions

1. How do average nightly prices differ between Columbus and New York City across neighborhoods?
2. Which neighborhoods in each city offer the highest availability relative to price?
3. How concentrated is host ownership in each city (single-listing hosts vs multi-listing hosts)?
4. What listing characteristics are most associated with higher prices in each market?
5. How does room type distribution differ between Columbus and New York City?

## Data Source Mapping

| # | Question | Data Needed | Source | Data Type |
|:-:|:---------|:------------|:-------|:----------|
| 1 | Price differences by neighborhood | price, neighbourhood | listings.csv | Structured |
| 2 | Availability vs price | availability_365, price, neighbourhood | calendar.csv, listings.csv | Structured |
| 3 | Host ownership concentration | host_id, host_total_listings_count | listings.csv | Structured |
| 4 | Drivers of higher prices | price, room_type, accommodates, bedrooms, reviews | listings.csv | Structured |
| 5 | Room type distribution | room_type | listings.csv | Structured |

## Data Overview
- **Columbus, Ohio:** 2,877 listings (as of Sept 26, 2025)
- **New York City:** 30,259 listings (as of Jun 14, 2026 -- the originally planned Dec 4, 2025 NYC snapshot had price and host-listing-count data fully redacted, a known effect of NYC's Local Law 18 reporting rules; this is the nearest snapshot with usable pricing data)
- **Primary data source:** [Inside Airbnb](http://insideairbnb.com/get-the-data)
- **Full analysis:** [airbnb_analysis.ipynb](airbnb_analysis.ipynb) (also runnable as [analysis.py](analysis.py))

## Key Findings

**1. Price by neighborhood** -- NYC's overall average nightly price (~$253) is nearly double Columbus's (~$137). Priciest NYC areas run well above Columbus's priciest (Hayden Run, ~$243).

**2. Availability vs price** -- In both cities, the best availability-per-dollar neighborhoods are outer, less-central ones (Greenlawn/Frank Road in Columbus; Co-op City and Olinville in NYC).

**3. Host concentration** -- Columbus: only 36% of hosts run a single listing, and multi-listing hosts control 86.5% of all Columbus listings. NYC: hosts with more than one listing in the dataset account for 62.7% of listings.

**4. Price drivers** -- `accommodates` (guest capacity) is the strongest price driver in both cities, followed by bedrooms and bathrooms. Review scores/counts barely correlate with price. NYC hotel-room listings (~$549/night) are the priciest room type in either city.

**5. Room type mix** -- Columbus is dominated by entire-home/apt listings (83.7%). NYC is far more mixed -- 53.7% entire home/apt, 43.3% private room, plus a small hotel-room segment (2.2%).

## Project Status
- [x] Initial data exploration
- [x] Research questions defined
- [x] Data sources mapped
- [x] Data downloaded and cleaned
- [x] Analysis complete
- [x] Visualizations created
