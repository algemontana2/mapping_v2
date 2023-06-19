import logging
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
from dateutil.parser import parse
import pandas as pd

# Configure logging
logging.basicConfig(filename='mapping_project.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_date(date_string):
    print(f"Date before conversion: {date_string}")
    date_string = date_string.strip().lower()
    approximate = False

    # Check for 'about' dates
    if date_string.startswith('about') or date_string.startswith('abt'):
        approximate = True
        date_string = date_string.replace('about', '').replace('abt', '').strip()

    try:
        # Try to parse the date with dateutil
        date = parse(date_string, fuzzy=True, default=pd.Timestamp('2000-01-01'))
    except ValueError:
        # If dateutil fails, handle the date manually
        date = handle_date_manually(date_string)
    except Exception as e:
        logging.error(f"Invalid form for date: {date_string}, error: {e}")
        raise e

    # Format the date as 'MM/DD/YYYY'
    if isinstance(date, list):
        formatted_date = [d.strftime('%m/%d/%Y') for d in date]
    else:
        formatted_date = date.strftime('%m/%d/%Y')
    
    print(f"Date after conversion: {formatted_date}, Approximate: {approximate}")

    return formatted_date, approximate



def handle_date_manually(date_string):
    print(f"Date before manual handling: {date_string}")
    if '-' in date_string:  # Handle year ranges
        year1, year2 = map(int, date_string.split('-'))
        dates = [pd.Timestamp(year=year, month=1, day=1) for year in range(year1, year2+1)]
        return dates
    elif '/' in date_string:  # Handle date ranges
        date_string1, date_string2 = date_string.split('/')
        date1 = handle_date_manually(date_string1.strip())
        date2 = handle_date_manually(date_string2.strip())
        average_date = date1 + (date2 - date1) / 2
        return average_date
    elif date_string.isdigit() and len(date_string) == 4:  # Handle dates with only year specified
        date = pd.Timestamp(year=int(date_string), month=1, day=1)
    elif len(date_string.split(' ')) == 2 and date_string.split(' ')[1].isdigit():  # Handle dates with month and year specified
        month, year = date_string.split(' ')
        date = pd.Timestamp(year=int(year), month=parse(month).month, day=1)
    elif len(date_string.split(' ')) == 3 and date_string.split(' ')[2].isdigit():  # Handle dates with day, month, and year specified
        day, month, year = date_string.split(' ')
        date = pd.Timestamp(year=int(year), month=parse(month).month, day=int(day))
    else:
        raise ValueError(f'Cannot parse date: {date_string}')
    print(f"Date after manual handling: {date}")

    return date


def extract_event(element, event_tag):
    event_element = next((child for child in element.get_child_elements() if child.get_tag() == event_tag), None)
    if not event_element:
        return None, None

    place = next((child.get_value() for child in event_element.get_child_elements() if child.get_tag() == 'PLAC'), None)
    date = next((child.get_value() for child in event_element.get_child_elements() if child.get_tag() == 'DATE'), None)

    return place, date

def parse_gedcom_file(file_path):
    gedcom_parser = Parser()
    gedcom_parser.parse_file(file_path)
    root_element = gedcom_parser.get_root_element()

    individuals = []
    death_approximate = None

    for element in root_element.get_child_elements():
        if isinstance(element, IndividualElement):
            name = element.get_name()
            gender = element.get_gender()

            birth_place, birth_date = extract_event(element, 'BIRT')
            death_place, death_date = extract_event(element, 'DEAT')

            if birth_date is not None:
                birth_date, birth_approximate = convert_date(birth_date)
            if death_date is not None:
                death_date, death_approximate = convert_date(death_date)

            residences = []
            for event_tag in ['RESI', 'BIRT', 'DEAT']:
                for child_element in (child for child in element.get_child_elements() if child.get_tag() == event_tag):
                    residence_base = {'event': event_tag.lower()}
                    dates = None
                    for sub_element in child_element.get_child_elements():
                        if sub_element.get_tag() == 'PLAC':
                            residence_base['place'] = sub_element.get_value()
                        elif sub_element.get_tag() == 'DATE':
                            dates = convert_date(sub_element.get_value())  # dates might be a list now
                        elif sub_element.get_tag() == 'FAMC' and event_tag == 'RESI':  # FAMC is only relevant for residences
                            residence_base['family'] = sub_element.get_value()
                    if dates is not None:
                        if isinstance(dates, list):
                            for d in dates:
                                residence = residence_base.copy()
                                residence['date'] = d
                                residences.append(residence)
                        else:
                            residence = residence_base
                            residence['date'] = dates
                            residences.append(residence)


            individuals.append({
                'name': name,
                'gender': gender,
                'birth_place': birth_place,
                'birth_date': birth_date,
                'birth_approximate': birth_approximate,
                'death_place': death_place,
                'death_date': death_date,
                'death_approximate': death_approximate,
                'residences': residences,
            })

    return individuals
