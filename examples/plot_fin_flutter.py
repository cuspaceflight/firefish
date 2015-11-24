"""
An example script which generates a plot of flutter velocity versus altitude.

Run via: python plot_fin_flutter.py

The plot is written to: flutter-velocity-example.pdf

"""
# Configure matplotlib to generate PDF output rather than popping a window up
import matplotlib
matplotlib.use('PDF')

import numpy as np
from matplotlib import pyplot as plt
from cusfsim.finflutter import model_atmosphere, flutter_velocity

def main(output='flutter-velocity-example.pdf'):
    """
    >>> import io
    >>> fobj = io.BytesIO()
    >>> main(fobj)
    >>> assert len(fobj.getvalue()) > 0
    >>> assert fobj.getvalue()[:4] == b'%PDF'

    """
    zs = np.linspace(0, 50000, 200)
    ps, _, ss = model_atmosphere(zs)
    vs = flutter_velocity(ps, ss, 20, 10, 10, 0.2)

    plt.figure()
    plt.plot(zs * 1e-3, vs)
    plt.title('Flutter velocity vs altitude')
    plt.xlabel('Altitude [km]')
    plt.ylabel('Flutter velocity [m/s]')
    plt.savefig(output, format='PDF')

if __name__ == '__main__':
    main()
