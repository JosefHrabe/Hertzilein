'''
======================
Triangular 3D surfaces
======================

Plot a 3D surface with a triangular mesh.
'''
import random

import matplotlib.pyplot as plt
import netBase as nb

# x,y,z=[],[],[]
#
# for d in range(10):
#     for i in range( 1000 ):
#         dayoffset=24*60*60
#         day   = nb.getDateObject( nb.getStamp( offset=dayoffset ))
#         stamp = nb.getDateObject( nb.getStamp( offset=dayoffset + i))
#
#         x.append( day )
#         y.append( stamp )
#         z.append( random.uniform(49.9,50.1))
#
#
# fig = plt.figure()
# ax = fig.gca(projection='3d')
#
# ax.plot_trisurf(x, y, z, linewidth=0.2, antialiased=True)
#
# plt.show()

# import patoolib
# patoolib.extract_archive("D:/sso/Mozart Klavierkonzert.rar", outdir="D:/sso/Mozart Klavierkonzert")
from pyunpack import Archive
Archive('D:/sso/Mozart Klavierkonzert.rar').extractall('D:/sso/Mozart')
