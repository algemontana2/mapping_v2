import datetime
import logging
import folium
from folium.plugins import MarkerCluster, Search
import branca

def calculate_age(birth_year, residence_date):
    current_year = datetime.datetime.now().year
    try:
        residence_year = int(residence_date[:4])
    except ValueError:
        logging.warning(f"Invalid date format: {residence_date}. Cannot calculate age.")
        return 'N/A'
    return (
        current_year - birth_year
        if birth_year <= residence_year <= current_year
        else 'N/A'
    )


def filter_individuals(individuals, start_date, end_date):
    filtered_individuals = []
    for individual in individuals:
        if filtered_residences := [
            residence
            for residence in individual.get('residences', [])
            if 'date' in residence
            and start_date <= residence['date'] <= end_date
        ]:
            filtered_individuals.append({'name': individual['name'], 'residences': filtered_residences})
    return filtered_individuals


def generate_map(individuals, output_file, start_date=None, end_date=None):
    logging.info("Starting map generation.")
    if start_date and end_date:
        logging.info(f"Filtering individuals from {start_date} to {end_date}")
        individuals = filter_individuals(individuals, start_date, end_date)

    total_residences = sum(len(individual.get('residences', [])) for individual in individuals)
    if total_residences < 10:
        logging.error("Less then 10 residences found in the provided individuals.")
        return

    average_latitude = sum(residence['latitude'] for individual in individuals for residence in individual.get('residences', [])) / total_residences
    average_longitude = sum(residence['longitude'] for individual in individuals for residence in individual.get('residences', [])) / total_residences

    logging.info(f"Average latitude: {average_latitude}, Average longitude: {average_longitude}")

    m = folium.Map(location=[average_latitude, average_longitude], zoom_start=2, tiles='cartodb positron')

    colors = {
        'BIRT': 'green',
        'DEAT': 'red',
        'DIV': 'black',
        'IMMI': 'darkblue',
        'EMIG': 'darkgreen',
        'RESI': 'pink',
        'resi': 'pink',
        'OCCU': 'lightblue',
        'PROB': 'lightred',
        'WILL': 'darkred',
        'GRAD': 'cadetblue',
        'RETI': 'blue',
        'NATU': 'lightgray',
        'CHRA': 'gray',
        'ORDN': 'darkblue',
        'CONF': 'lightgreen',
        'BAPM': 'darkpurple',
        'FCOM': 'pink',
        'BLES': 'purple',
        'ADOP': 'orange',
        'RELI': 'green',
        'BURI': 'red',
        'CREM': 'black',
        'BARM': 'lightblue',
        'BASM': 'beige',
        'CAST': 'darkgreen',
        'DSCR': 'darkpurple',
        'EDUC': 'lightred',
        'IDNO': 'darkred',
        'NATI': 'cadetblue',
        'NCHI': 'blue',
        'NMR': 'lightgray',
        'PROP': 'gray',
        'SSN': 'darkgreen',
        'TITL': 'darkpurple',
        'FACT': 'lightred',
        'AFN': 'darkred',
        'REFN': 'cadetblue',
        'RIN': 'blue',
        '_UID': 'lightgray',
        'CHAN': 'gray',
        'EVEN': 'darkgreen',
        'NOTE': 'darkpurple',
        'SOUR': 'lightred',
        'OBJE': 'darkred',
        'HUSB': 'cadetblue',
        'WIFE': 'blue',
        'CHIL': 'lightgray',
        'SPOU': 'gray',
        'FAMC': 'darkgreen',
        'FAMS': 'darkpurple',
        'SUBM': 'lightred',
        'ANUL': 'darkred',
        'CENS': 'cadetblue',
        'DIVF': 'blue',
        'ENGA': 'lightgray',
        'MARB': 'gray',
        'MARC': 'darkgreen',
        'MARR': 'darkpurple',
        'MARL': 'lightred',
        'MARS': 'darkred',
    }
    marker_cluster = MarkerCluster().add_to(m)
    
    for individual in individuals:
        for i, residence in enumerate(individual['residences']):
            if 'date' not in residence:
                continue
            birth_year = int(individual['birth']['date'][:4]) if 'birth' in individual and 'date' in individual['birth'] else None
            age = calculate_age(birth_year, residence['date']) if birth_year else 'N/A'
            html = f"""
            <h4>{individual['name']}</h4>
            <p><b>Event:</b> {residence['event']}</p>
            <p><b>Date:</b> {residence['date']}</p>
            <p><b>Place:</b> {residence['place']}</p>
            <p><b>Age:</b> {age}</p>
            """
            iframe = branca.element.IFrame(html=html, width=400, height=300)
            popup = folium.Popup(iframe, max_width=500)

            marker = folium.Marker(
                location=[residence['latitude'], residence['longitude']],
                popup=popup,
                icon=folium.Icon(color=colors[residence['event'].upper()], icon='cloud'),
            )

            # Add the marker to the map
            marker.add_to(marker_cluster)
            print(f"Residence being added to map: {residence}")

    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 100px; height: 90px; 
    border:5px solid grey; z-index:9999; font-size:14px;">
    <p><a style='color:green;'>●</a>&nbsp;Birth</p>
    <p><a style='color:red;'>●</a>&nbsp;Death</p>
    <p><a style='color:blue;'>●</a>&nbsp;Residence</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add a search bar
    search = Search(
        layer=marker_cluster,
        geom_type='Point',
        placeholder='Search for a place or date...',
        collapsed=False,
    ).add_to(m)

    # Save the map to an HTML file
    try:
        logging.info(f"Saving map to {output_file}")
        m.save(output_file)
        logging.info("Map saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save map: {e}")

    return m
