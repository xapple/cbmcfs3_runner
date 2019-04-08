"""
A script to draw a map of all the countries that pass a certain step of the simulation.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbmcfs3_runner/scripts/draw_europe_map.py

Color brewer makes provides a range of color palettes:

    http://colorbrewer2.org/#type=sequential&scheme=BuGn&n=3

"""

# Built-in modules #
import os, inspect, StringIO

# Third party modules #
import pandas, folium, brewer2mpl

# First party modules #
from autopaths.dir_path import DirectoryPath

# Internal modules #
from cbmcfs3_runner.all_countries import continent

# Current directory #
file_name = os.path.abspath((inspect.stack()[0])[1])
this_dir  = DirectoryPath(os.path.dirname(os.path.abspath(file_name)))

# Colors #
palette = brewer2mpl.get_map('YlGn', 'sequential', 3)

###############################################################################
map_data = pandas.DataFrame({
    'A3':    [c.country_iso3 for c in continent],
    'value': [c.map_value for c in continent]
})

print map_data

###############################################################################
m = folium.Map(
    location = [50, 15],
    zoom_start = 4
)

###############################################################################
m.choropleth(
    geo_data   = 'https://github.com/simonepri/geo-maps/releases/download/v0.6.0/countries-land-10km.geo.json',
    data       = map_data,
    columns    = ['A3', 'value'],
    key_on     = 'feature.properties.A3',
    fill_color = 'YlGn' # palette.hex_color # 'PuBuGn'
)

###############################################################################
m.save(str(this_dir + 'europe.html'))
(this_dir + 'europe.png').write(m._to_png(), mode='wb')
