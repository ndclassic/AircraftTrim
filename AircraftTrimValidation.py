'''
This script provides an example usage of the  the function
"trim" from the file "AircraftTraim.py" and validates the example values.
It uses the physical properties of an Airbus A300, provided by
Alles, Brockhaus, Luckner - "Flugregelung", Pages 906 - 909.
'''
import numpy as np
import AircraftTrim
'''
The Longitudinal Derivatives have to be provided 
in the following format: 
                  [[CD0, CDal, CDet],
                   [CL0,  CLal, CLet],
                   [Cm0,  Cmal, Cmet]]
'''
derLon = np.array([[0.023, 0.219, 0.0068],
                   [0.341, 6.22, 0.194],
                   [-0.0092, -1.081, -0.771]])

a300 = {"Mass": 130e3,
        "Mean Wing Chord": 6.6,
        "Reference Wing Area": 260,
        "Thrust Vector Mounting Angle": 2.17 * np.pi/180,  # Converting Degree to Radiant
        "Leverage Arm of the Thrust Vector": 2.65,
        "Maximum Total Thrust": 452000,
        "Longitudinal Derivatives": derLon
        }
vcr = 264  # Cruising Velocity
rh = 0.412706  # Air density at 10km in the standard atmosphere

solution = AircraftTrim.trim(a300, 264, rh, 0, verbose="all")
print("The AircraftTrim.trim(...) function outputs:\n")
print('{:>21s}{:>10.3e}'.format("AoA (rad) = ", solution[0]))
print('{:>21s}{:>10.3e}'.format("elevator (rad) = ", solution[1]))
print('{:>21s}{:>10.3e}'.format("Thrust (N) = ", solution[2]))
print('{:>21s}{:>10.3e}'.format("Efficiency (s/kg) = ", solution[3]))
'''
In the following, the solution is compared to the four expected values.
If each element of the solution does not meet it's  absolute 
or relative tolerance, an AssertionError is raised.
'''
expectation = np.array([0, 0, 0.2 * 452000, vcr / (0.2 * 452000)])

np.testing.assert_allclose(expectation[0], solution[0], atol=0.02, verbose=True)
np.testing.assert_allclose(expectation[1], solution[1], atol=0.02, verbose=True)
np.testing.assert_allclose(expectation[2], solution[2], rtol=0.25, verbose=True)
np.testing.assert_allclose(expectation[3], solution[3], rtol=0.25, verbose=True)
