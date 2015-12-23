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
from firefish.finflutter import model_atmosphere, flutter_velocity_transonic, flutter_velocity_supersonic

def main(output='flutter-velocity-example.pdf'):
    """
    >>> import io
    >>> fobj = io.BytesIO()
    >>> main(fobj)
    >>> assert len(fobj.getvalue()) > 0
    >>> assert fobj.getvalue()[:4] == b'%PDF'

    """
    zs = np.linspace(0, 50000, 200)
    ps, ts, ss = model_atmosphere(zs)
    rhos = ps / (0.2869 * (ts + 273.1))
    vs_t = flutter_velocity_transonic(ps, ss, 20, 10, 10, 0.2)
    vs_s = flutter_velocity_supersonic(rhos, 380, 104, 1, 0.3, 0.0313, 0.0855, 3)

    plt.figure()
    plt.plot(zs * 1e-3, vs_t)
    plt.title('Flutter velocity vs altitude')
    plt.xlabel('Altitude [km]')
    plt.ylabel('Flutter velocity [m/s]')
    plt.savefig(output, format='PDF')

if __name__ == '__main__':
    main()
