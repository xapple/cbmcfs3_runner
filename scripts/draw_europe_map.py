"""
A script to draw a map of all the countries that pass a certain step of the simulation.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/scripts/draw_europe_map.py
"""

# Built-in modules #
import os, inspect, StringIO

# Third party modules #
import pandas, folium

# First party modules #
from autopaths.dir_path   import DirectoryPath

# Internal modules #
from cbm_runner.all_countries import all_countries

# Current directory #
file_name = os.path.abspath((inspect.stack()[0])[1])
this_dir  = DirectoryPath(os.path.dirname(os.path.abspath(file_name)))

###############################################################################
map_data = pandas.DataFrame({
    'A3':    [c.country_iso3 for c in all_countries],
    'value': [int(c.standard_import_tool.passed) for c in all_countries]
})

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
    fill_color = 'YlOrRd'
)

###############################################################################
m.save(str(this_dir + 'europe.html'))
(this_dir + 'europe.png').write(m._to_png(), mode='wb')