import folium
from geopy.geocoders import Nominatim


f=open("traceroute.txt","r")
lines=f.readlines()

cities=[]
order=[]
indx=1

for line in lines:
    # make a string of the line and strip the spaces
    line=line.strip()
    if(line!="Unknown"):
        cities.append(line)
        order.append(indx)
        indx+=1



# Create a map centered on North America
geolocator = Nominatim(user_agent="my_application")
location = geolocator.geocode("North America")
map = folium.Map(location=[location.latitude, location.longitude], zoom_start=4)

# Loop through the countries and add markers with their order
for i in range(len(cities)):
    city = cities[i]
    order_num = order[i]
    location = geolocator.geocode(city)
    folium.Marker([location.latitude, location.longitude],
                  popup=f"{city}: {order_num}",
                  icon=folium.Icon(color='red')).add_to(map)

# Create arrows between the markers to indicate order
for i in range(len(cities) - 1):
    start_country = cities[i]
    end_country = cities[i + 1]
    start_location = geolocator.geocode(start_country)
    end_location = geolocator.geocode(end_country)
    folium.PolyLine(locations=[(start_location.latitude, start_location.longitude),
                               (end_location.latitude, end_location.longitude)],
                    color='blue',
                    weight=2).add_to(map)

# Save the map as an HTML file
map.save("my_map.html")