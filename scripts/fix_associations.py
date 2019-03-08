from cbm_runner.all_countries import *
c = continent['ES']

print c.aidb_switcher.species_type.to_string()
print c.aidb_switcher.admin_boundary.to_string()
print c.input_data.classifiers

if hasattr(c.orig_to_csv.associations_parser, '__cache__'):
    c.orig_to_csv.associations_parser.__cache__.pop('df', None)
    c.orig_to_csv.associations_parser.__cache__.pop('all_mappings', None)
if hasattr(c.standard_import_tool, '__cache__'):
    c.standard_import_tool.__cache__.pop('context')
if hasattr(c.orig_to_csv.associations_parser, '__cache__'):
  c.orig_to_csv.associations_parser.__cache__.pop('df', None)

c.aidb_switcher()
c.orig_to_csv.associations_parser()
c.standard_import_tool()