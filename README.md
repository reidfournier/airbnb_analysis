# Airbnb Market Analysis: Columbus vs New York

## Author
[Your Name]

## Project Overview
This project analyzes Airbnb listing data to compare the Columbus, Ohio and New York City markets. The goal is to [briefly describe what decisions your analysis could support].

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
- **Columbus, Ohio:** [X] listings (as of Sept 26, 2025)
- **New York City:** [X] listings (as of Dec 4, 2025)
- **Primary data source:** [Inside Airbnb](http://insideairbnb.com/get-the-data)

## Project Status
- [x] Initial data exploration
- [x] Research questions defined
- [x] Data sources mapped
- [ ] Data downloaded and cleaned
- [ ] Analysis complete
- [ ] Visualizations created
