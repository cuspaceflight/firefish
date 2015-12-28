"""
Calculation of fin flutter vs. altitude.

The transonic flutter velocity code comes from "Peak of flight" newsletter
issue 291, which is itself a modified version of the equation in
NACA paper 4197.

The supersonic flutter criterion is from a thesis by J. Simmons at the
Air Force Institute of Technology, Ohio. (AFIT/GSS/ENY/09-J02), the torsional and
bending frequencies have to be calculated for different geometries using
finite element analysis in Solidworks.

This module provides a simple API for computing fin-flutter velocity as a
function of altitude. These can then be plotted. For example:

.. plot::
    :include-source:

    import matplotlib.pyplot as plt
    import numpy as np
    from firefish import finflutter

    zs = np.linspace(0, 50000, 200)
    ps, _, ss = finflutter.model_atmosphere(zs)
    vs = finflutter.flutter_velocity_transonic(ps, ss, root_chord=20, +
        tip_chord=10, semi_span=10, thickness=0.2)

    plt.plot(zs * 1e-3, vs)
    plt.grid()
    plt.title('Flutter velocity versus altitude')
    plt.xlabel('Altitude [km]')
    plt.ylabel('Flutter velocity [ms${}^{-1}$]')
    plt.show()

"""
# Make sure a/b does what we expect even if both are integers(!)
from __future__ import division

import numpy as np

def model_atmosphere(altitudes):
    """Model atmospheric pressure, temperature and speed of sound.

    Args:
        altitudes (np.array): 1-d array of geopotential altitudes in metres

    Returns:
        A triple giving corresponding 1-d arrays of estimated pressure,
        temperature and speed of sound. Units are Pascals, Celsius and m/s
        respectively.

    >>> import numpy as np
    >>> zs = np.linspace(0, 30000, 100)
    >>> ps, ts, ss = model_atmosphere(zs)
    >>> assert ps.shape == zs.shape
    >>> assert ts.shape == zs.shape
    >>> assert ss.shape == zs.shape

    """
    # Ensure input is a 1d floating point array.
    altitudes = np.atleast_1d(altitudes).astype(np.float)

    # Create output
    ps = np.zeros_like(altitudes)
    ts = np.zeros_like(altitudes)
    ss = np.zeros_like(altitudes)

    # Flag different atmospheric regs. Use 1 for Troposphere, 2 for Lower
    # Stratosphere and 3 for Upper Stratosphere.
    regs = np.zeros_like(altitudes, dtype=np.int)
    regs[altitudes <= 11000] = 1
    regs[np.logical_and(altitudes > 11000, altitudes < 25000)] = 2
    regs[altitudes > 25000] = 3

    # Troposphere
    ts[regs == 1] = 15.04 - 0.00649*altitudes[regs == 1]
    ps[regs == 1] = 1000 * 101.29*((ts[regs == 1] + 273.1)/288.08)**5.256

    # Lower Stratosphere
    ts[regs == 2] = -56.46
    ps[regs == 2] = 1000 * 22.65 * np.exp(1.73 - 0.000157*altitudes[regs == 2])

    # Upper Stratosphere
    ts[regs == 3] = -131.21 + 0.00299*altitudes[regs == 3]
    ps[regs == 3] = 1000 * 2.488 * ((ts[regs == 3] + 273.1) / 216.6)**-11.388

    # "from Hyperphysics"
    ss = 331.3 * np.sqrt(1 + (ts / 273.15))

    return ps, ts, ss


def flutter_velocity_transonic(pressures, speeds_of_sound,
                               root_chord, tip_chord, semi_span, thickness,
                               shear_modulus=2.62e9):
    """Calculate transonic flutter velocities for a given fin design.
    The equation is valid if the rocket is travelling at < M2.5 at the
    given altitude.

    Fin dimensions are given via the root_chord, tip_chord, semi_span and
    thickness arguments. All dimensions are in centimetres.

    Use shear_modulus to specify the shear modulus of the fin material in
    Pascals.

    >>> import numpy as np
    >>> zs = np.linspace(0, 30000, 100)
    >>> ps, _, ss = model_atmosphere(zs)
    >>> vels = flutter_velocity_transonic(ps, ss, 20, 10, 10, 0.2)
    >>> assert vels.shape == ps.shape

    Args:
        pressures (np.array): 1-d array of atmospheric pressures in Pascals
        speeds_of_sound (np.array): 1-d array of speeds of sound in m/s
        root_chord: fin root chord (cm)
        tip_chord: fin tip chord (cm)
        semi_span: fin semi-span (cm)
        thickness: fin thickness (cm)
        shear_modulus: fin material shear modulus (Pascals)

    Returns:
        A 1-d array containing corresponding flutter velocities in m/s.

    """
    # Ensure input is 1d array of floating point values
    pressures = np.atleast_1d(pressures).astype(np.float)

    # Compute derived dimensions from fin specification.
    S = 0.5 * (root_chord + tip_chord) * semi_span # Area
    Ra = (semi_span * semi_span) / S # Aspect ratio
    k = tip_chord / root_chord # Taper ratio

    Vf = np.zeros_like(pressures)
    A = 1.337 * Ra**3 * pressures * (k+1)
    B = 2 * (Ra + 2) * (thickness / root_chord)**3
    Vf = speeds_of_sound * np.sqrt(shear_modulus * B / A)

    return Vf

def flutter_velocity_supersonic(air_densities, torsional_frequency, bending_frequency,
                                mass, semi_span, radius_of_gyration, distance_to_COG, Mach_number):

    """Calculate transonic flutter velocities for a given fin design.
    The equation is valid for freestream flow in the supersonic regime
    (>~M2.5)

    Fin analysis have to be done for Solidworks in order to find the
    frequencies for bending and torsional modes, as well as the radius_of_gyration
    and distance_to_COG. Torsional and bending frequency are in rad/s, the semi-span,
    radius of gyration, and distance to COG will be given in metres.

    >>> import numpy as np
    >>> zs = np.linspace(0, 30000, 100)
    >>> ps, ts, ss = model_atmosphere(zs)
    >>> rhos = (ps/1000) / (0.2869 * (ts + 273.1))
    >>> vels = flutter_velocity_supersonic(rhos, 380, 104, 1, 0.1, 0.2, 0.1, 3)
    >>> assert vels.shape == ps.shape

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

    Returns:
        A 1-d array containing corresponding flutter velocities in m/s.
    """
    Vf = np.zeros_like(air_densities)
    air_densities = np.atleast_1d(air_densities).astype(np.float)
    #mass ratio
    mr = mass / (air_densities * semi_span**2)
    A = (mr * radius_of_gyration**2 * np.sqrt(Mach_number**2 - 1)) / (distance_to_COG * semi_span)
    #frequency ratio squared
    fr2 = (bending_frequency / torsional_frequency)**2
    B = (1-fr2)**2 + 4*(distance_to_COG/radius_of_gyration)**2 * fr2
    C = 2*(1+fr2)
    Vf = semi_span * torsional_frequency * np.sqrt(A*B/C)

    return Vf
