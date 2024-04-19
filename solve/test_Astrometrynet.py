from astroquery.astrometry_net import AstrometryNet

ast = AstrometryNet()
ast.api_key = ''

wcs_header = ast.solve_from_image('E:/test_download/astropy/1.fits')


