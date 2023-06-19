import argparse
import logging
import gedcom_parser
import geocoder
import map_generator
import os


# Configure logging
logging.basicConfig(filename='mapping_project.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(gedcom_file_path):
    print(f"GEDCOM file path: {gedcom_file_path}")  
    # Read the API key from the file
    with open('api_key.txt', 'r') as f:
        api_key = f.read().strip()

    # Parse the GEDCOM file
    try:
        logging.info(f"Parsing GEDCOM file: {gedcom_file_path}")
        individuals = gedcom_parser.parse_gedcom_file(gedcom_file_path)
        print(f"Individuals after parsing: {individuals}")

    except Exception as e:
        logging.error(f"Error parsing GEDCOM file {gedcom_file_path}: {e}")
        raise

    # Geocode the locations
    try:
        logging.info("Geocoding locations")
        geocoded_individuals = geocoder.geocode_locations(individuals, api_key)
        print(geocoded_individuals)  # add this line


    except Exception as e:
        logging.error("Error geocoding locations: {e}")
        raise

    # Generate the map
    try:
        logging.info("Generating map")
        map_generator.generate_map(geocoded_individuals, 'map.html')
    except Exception as e:
        logging.error("Error generating map: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a map from a GEDCOM file.')
    parser.add_argument('gedcom_file_path', help='The path to the GEDCOM file.')
    args = parser.parse_args()

    main(args.gedcom_file_path)
