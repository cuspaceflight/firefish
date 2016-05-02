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
    zs = np.linspace(0, 20000, 200)
    ps, ts, ss = model_atmosphere(zs)
    rhos = (ps/1000) / (0.2869 * (ts + 273.1))
    vs_t = flutter_velocity_transonic(ps, ss, 20, 10, 10, 0.2)
    vs_s1 = flutter_velocity_supersonic(rhos, 26796, 7025, 0.0527, 0.06, 0.0518, 0.0058, 4.3)
    vs_s2 = flutter_velocity_supersonic(rhos, 26796, 7025, 0.0527, 0.06, 0.0518, 0.0058, 3)
    vs_s3 = flutter_velocity_supersonic(rhos, 26796, 7025, 0.0527, 0.06, 0.0518, 0.0058, 2)

    plt.figure()
    #plt.plot(zs * 1e-3, vs_t, 'r', label="transonic flutter velocity")
    plt.plot(zs*1e-3, vs_s1/343.2, 'g', label="Mach 4.3")
    plt.plot(zs*1e-3, vs_s2/343.2, 'r', label="Mach 3")
    plt.plot(zs*1e-3, vs_s3/343.2, 'b', label="Mach 2")

    plt.title('Flutter velocity vs altitude')
    plt.xlabel('Altitude [km]')
    plt.ylabel('Flutter Velocity [Mach]')
    plt.legend()
    plt.savefig(output, format='PDF')

if __name__ == '__main__':
    main()
