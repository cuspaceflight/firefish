"""
An example script which generates a plot of flutter velocity versus altitude.

Run via: python plot_fin_flutter.py

The plot is written to: flutter-velocity-example.pdf

Theodorson (general case):
    Args:
        pressures (np.array): 1-d array of atmospheric pressures in Pascals
        speeds_of_sound (np.array): 1-d array of speeds of sound in m/s
        root_chord: fin root chord (cm)
        tip_chord: fin tip chord (cm)
        semi_span: fin semi-span (cm)
        thickness: fin thickness (cm)
        shear_modulus: fin material shear modulus (Pascals)

Supersonic correction:
    Args:
        semi_span: fin semi-span (m)
        air_densities: 1-d array of air density in kg/m^3  (np.array)
        torsional frequency: uncoupled torsional frequency (rad/s)
        bending_frequency: uncoupled bending frequency of the fin (rad/s)
        mass: mass of fin (kg)
        Mach_number: mach number of rocket
        distance_to_COG: distance of COG to axis of rotation (m)
        radius_of_gyration: distance at which all the mass of the fin
                            can be though to be concenreated, =sqrt(I/M)

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
    vs_t = flutter_velocity_transonic(ps, ss, 14.02, 7, 8.59, 0.5)
    vs_s1 = flutter_velocity_supersonic(rhos, 5026, 11671, 0.0923, 0.0859, 0.0284, 0.0040, 4.3)
    vs_s2 = flutter_velocity_supersonic(rhos, 5026, 11671, 0.0923, 0.0859, 0.0284, 0.0040, 3)
    vs_s3 = flutter_velocity_supersonic(rhos, 5026, 11671, 0.0923, 0.0859, 0.0284, 0.0040, 2)

    plt.figure()
    #plt.plot(zs * 1e-3, vs_t, 'r', label="transonic flutter velocity")
    plt.plot(zs*1e-3, vs_t/343.2, 'c', label="Theodorson")
    plt.plot(zs*1e-3, vs_s1/343.2, 'g', label="Mach 4.3")
    plt.plot(zs*1e-3, vs_s2/343.2, 'r', label="Mach 3")
    plt.plot(zs*1e-3, vs_s3/343.2, 'b', label="Mach 2")

    plt.title('Flutter velocity vs altitude, Core/Booster fin')
    plt.xlabel('Altitude [km]')
    plt.ylabel('Flutter Velocity [Mach]')
    plt.legend()
    plt.savefig(output, format='PDF')

if __name__ == '__main__':
    main()
