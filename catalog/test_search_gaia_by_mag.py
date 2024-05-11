# from astropy.coordinates import SkyCoord
# from astroquery.gaia import Gaia
# import astropy.units as u
#
#
# Gaia.MAIN_GAIA_TABLE = "gaiadr2.gaia_source"  # Select Data Release 2
# Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"  # Reselect Data Release 3, default
#
#
# coord = SkyCoord(ra=280, dec=-60, unit=(u.degree, u.degree), frame='icrs')
# width = u.Quantity(0.1, u.deg)
# height = u.Quantity(0.1, u.deg)
# r = Gaia.query_object_async(coordinate=coord, width=width, height=height)
#
# r.pprint(max_lines=12, max_width=130)
#


from astroquery.gaia import Gaia

tables = Gaia.load_tables(only_names=True)
print(f'------------tables----------')
for table in tables:
    print(table.name)
meta = Gaia.load_table('gaiadr2.gaia_source')
print(f'-----------meta-----------')
print(meta)
print(f'----------cols------------')
for column in meta.columns:
    print(column.name)

# query1 = 'SELECT TOP 10 source_id, ra, dec, parallax FROM gaiadr2.gaia_source '
query1 = 'SELECT count(*) FROM gaiadr2.gaia_source where phot_g_mean_mag between 8 and 10'

job = Gaia.launch_job(query1)
# print(job)
results = job.get_results()
# type(results)
print(f'----------------------')
print(results)


