
# Mapping V2

This is a Python project that involves geocoding and generating maps, possibly with data from GEDCOM files, which are used for genealogy data. The project utilizes the Flask web framework.

## Description

The project contains the following main Python scripts:

1. **main.py**: This is the main entry point for the project. It reads a GEDCOM file, parses the file, geocodes the locations from the file, and generates a map.

2. **map_generator.py**: This script defines a function called `generate_map` which takes a list of individuals and an output file as arguments. It generates a map with markers for different events in the individuals' lives.

3. **gedcom_parser.py**: This script defines a function called `parse_gedcom_file` which takes a file path as an argument. It reads a GEDCOM file, parses it, and returns a list of individuals with their events.

4. **geocoder.py**: This script defines a function called `geocode_locations` which takes a list of individuals and an API key as arguments. It geocodes the locations from the individuals using the Google Maps Geocoding API.

## Installation

To install the necessary dependencies, use pip:

```
pip install -r requirements.txt
```

## Usage

To run the project, execute the main.py script:

```
python main.py [gedcom_file_path]
```

Please replace `[gedcom_file_path]` with the path to your GEDCOM file.

## License

[Add license information here]
