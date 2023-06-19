import googlemaps
import time

def geocode_locations(individuals, api_key):
    gmaps = googlemaps.Client(key=api_key)  # replace with your actual API key
    geocoded_locations = {}

    for individual in individuals:
        print(f"Processing individual: {individual['name']}")  # Print the name of the individual

        if 'residences' in individual:
            geocoded_residences = []
            for residence in individual['residences']:
                try:
                    if 'place' not in residence:
                        continue
                    place = residence['place']
                    print(f"  Geocoding residence: {place}") # Print the place to be geocoded
                    if place in geocoded_locations:
                        latitude, longitude = geocoded_locations[place]
                        print(f"  Found in cache: {latitude}, {longitude}")
                    else:
                        geocode_result = gmaps.geocode(place)
                        if geocode_result and len(geocode_result) > 0:
                            latitude = geocode_result[0]["geometry"]["location"]["lat"]
                            longitude = geocode_result[0]["geometry"]["location"]["lng"]
                            geocoded_locations[place] = (latitude, longitude)
                            print(f"Geocoded location: {place} -> ({latitude}, {longitude})")
                        else:
                            print(f"  No results for {place}")  # Print a message if no results were found
                            continue

                    geocoded_residence = residence.copy()
                    geocoded_residence['latitude'] = latitude
                    geocoded_residence['longitude'] = longitude
                    geocoded_residences.append(geocoded_residence)
                except Exception as e:
                    print(f"Error geocoding {residence.get('place', 'unknown place')}: {e}")
                time.sleep(0)  # To prevent exceeding the rate limit

            individual['residences'] = geocoded_residences
        else:
            print("No 'residences' key found in individual dictionary.")

    return individuals
