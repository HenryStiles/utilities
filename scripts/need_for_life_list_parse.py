import re
import sys
import argparse
from datetime import datetime, timedelta, date

def parse_ebird_alert_text(alert_text):
    """
    Parses the eBird alert email text into structured records.
    """
    species_pattern = re.compile(
        r'^([A-Z].*?)\s*\(([^)]+)\)\s*\((\d+)\)'
    )
    all_lines = alert_text.splitlines()
    records = []
    current_record = None

    for line in all_lines:
        line = line.strip()
        match = species_pattern.match(line)
        if match:
            if current_record:
                records.append(current_record)
            species_name = match.group(1).strip()
            scientific_name = match.group(2).strip()
            count = match.group(3).strip()
            current_record = {
                'species': species_name,
                'scientific_name': scientific_name,
                'count': int(count),  # Convert count to integer
                'lines': []
            }
        else:
            if current_record:
                if line:
                    current_record['lines'].append(line)
    if current_record:
        records.append(current_record)

    return records

def filter_records_by_county(records, counties_of_interest):
    """
    Filters records based on the county appearing in the second line.
    """

    filtered = []
    for record in records:
        if len(record['lines']) < 2:
            continue  # Ensure we have at least 2 lines
        location_line = record['lines'][1]  # Second line is often the location
        for county in counties_of_interest:
            if f"{county}, Colorado" in location_line:
                filtered.append(record)
                break
    return filtered

def filter_records_by_species_count(records, min_count=10):
    """
    Filters records to only include species with sightings >= min_count.
    """
    return [record for record in records if record['count'] >= min_count]

def parse_reported_date(date_string):
    """
    Parses a date string in the format "- Reported Mar 12, 2025 11:55 by ..."
    and returns a datetime object.

    Args:
        date_string: The string containing the date and time.

    Returns:
        A datetime object representing the parsed date and time, or None if parsing fails.
    """
    match = re.search(r"- Reported (\w{3} \d{1,2}, \d{4} \d{2}:\d{2})", date_string)
    if match:
        date_time_str = match.group(1)
        try:
            # Parse the date and time string
            date_time_obj = datetime.strptime(date_time_str, "%b %d, %Y %H:%M")
            return date_time_obj
        except ValueError:
            print(f"Error: Could not parse date/time string: {date_time_str}")
            return None
    else:
        print(f"Error: Could not find date/time pattern in string: {date_string}")
        return None

def filter_records_by_after_days_ago(records, days_ago=50):
    """
    Filters records based on the reported date.
    """
    filtered_records = []
    for record in records:
        if not record['lines']:
            continue # skip if there are no lines
        first_line = record['lines'][0]
        reported_date = parse_reported_date(first_line)

        if reported_date:
             # Calculate the date that is 'days_ago' days ago from today
            cutoff_date = datetime.now() - timedelta(days=days_ago)

            # check the date is more recent than "days_ago"
            if reported_date >= cutoff_date:
                filtered_records.append(record)
    return filtered_records

def main():
    import sys
    import argparse
    # detect if there is any data in stdin
    raw_text = sys.stdin.read()

    parser = argparse.ArgumentParser(description="Parse eBird alert emails and filter by count threshold.")
    parser.add_argument("--threshold", type=int, default=5, help="Minimum count of species to include in the output.")
    parser.add_argument("--counties", nargs='*', default=["Larimer", "Boulder", "Arapahoe", "Weld", "Denver", "Jefferson", "Douglas", "Adams"], help="List of county names to filter by.")
    parser.add_argument("--days-ago", type=int, default=50, help="days back")
                        
    args = parser.parse_args()

    # Parse into records
    records = parse_ebird_alert_text(raw_text)
    print(f"Total records parsed: {len(records)}")

    # Filter for certain counties
    filtered_by_county = filter_records_by_county(records, args.counties)
    print(f"Filtered by counties: {len(filtered_by_county)} records.")

    filtered_by_count = filter_records_by_species_count(filtered_by_county, min_count=args.threshold)
    print(f"Filtered by species count (>=5 sightings): {len(filtered_by_count)} records.\n")

    filtered_by_date = filter_records_by_after_days_ago(filtered_by_count, days_ago=args.days_ago)
    print(f"Filtered by date: {len(filtered_by_date)} records.\n")

    # Sort records by species name
    sorted_records = sorted(filtered_by_date, key=lambda rec: rec['species'])

    # Print the filtered records
    for rec in sorted_records:
        print(f"{rec['species']} ({rec['scientific_name']}) x{rec['count']}")
        for line in rec['lines']:
            print("  " + line)
        print("-" * 60)

if __name__ == "__main__":
    main()