from astropy.coordinates import SkyCoord

item_coord_i = SkyCoord(ra=101.1656125, dec=16.818694444444443, unit='deg')
item_cart_i = item_coord_i.cartesian
print(item_cart_i)


item_coord_center = SkyCoord(ra=100.55225833333333, dec=17.469655555555555, unit='deg')
item_cart_center = item_coord_center.cartesian
print(f'center {item_cart_center}')

item_coord_rt = SkyCoord(ra=102.33743820833334, dec=16.389531583333333, unit='deg')
item_cart_rt = item_coord_rt.cartesian
print(f'r top {item_cart_rt}')


item_coord_lt = SkyCoord(ra=98.84193645833334, dec=16.286219666666668, unit='deg')
item_cart_lt = item_coord_lt.cartesian
print(f'l top {item_cart_lt}')


item_coord_rb = SkyCoord(ra=102.28489220833333, dec=18.63467547222222, unit='deg')
item_cart_rb = item_coord_rb.cartesian
print(f'r bott {item_cart_rb}')

item_coord_lb = SkyCoord(ra=98.74567554166667, dec=18.522890694444442, unit='deg')
item_cart_lb = item_coord_lb.cartesian
print(f'l bott {item_cart_lb}')

minX = min(item_cart_rt.x, item_cart_lt.x, item_cart_rb.x, item_cart_lb.x)
maxX = max(item_cart_rt.x, item_cart_lt.x, item_cart_rb.x, item_cart_lb.x)
minY = min(item_cart_rt.y, item_cart_lt.y, item_cart_rb.y, item_cart_lb.y)
maxY = max(item_cart_rt.y, item_cart_lt.y, item_cart_rb.y, item_cart_lb.y)
minZ = min(item_cart_rt.z, item_cart_lt.z, item_cart_rb.z, item_cart_lb.z)
maxZ = max(item_cart_rt.z, item_cart_lt.z, item_cart_rb.z, item_cart_lb.z)


print(f'{minX}  {maxX} {minY}  {maxY} {minZ}  {maxZ} ')

# minX                    maxX              minY                 maxY              minZ                 maxZ
# -0.204999059438705	-0.144292160868645	0.925861299037933	0.948392748832703	0.280624389648437	0.319561839103699

# -0.2049864481121801  -0.14417217597840776 0.925877352480648  0.9484657762455934 0.2804358559337861  0.3195328413918048

