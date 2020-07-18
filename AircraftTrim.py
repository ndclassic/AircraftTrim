'''
This File contains a function called "trim", which calculates the required
angle of attack, elevator deflection and total thrust of an aircraft
to achieve unaccelerated straight flight (level/ascending/descending).

It utilizes the multi-dimensional version of Newton's Method described in
Courtney Remani - "Numerical Methods for Solving Systems of Nonlinear Equations"
from Page 7 onwards.
https://www.lakeheadu.ca/sites/default/files/uploads/77/docs/RemaniFinal.pdf
'''

import numpy as np
from numpy import sin, cos, pi

def trim(aircraft, VA, rh, ga, g=9.80665, X0=np.array([0, 0, 1000]), tol=1e-8, it=16, verbose='last'):
    '''
    All arguments must be given in SI-units.
    Args:
        aircraft: dictionary containing aircraft-specific data, see line 37 to 52
        VA: true air speed (velocity in the aerodynamic-frame) in m/s
        rh: air density (greek letter rho) in kg/m^3
        ga: flight path angle (greek letter gamma) in RADIANTS

    Optional Args:
        g: gravitational constant (may vary slightly with lattitude and altitude) in m/s^2
        X0: initial guess for the solver.
        tol: tolerance of the error in between the last two iterations
        it: maximum number of iterations
        verbose: can be "all" or "last", any other input will prevent an console-output

    Returns Numpy Array with 4 elements:
        al: Angle of Attack (greek letter alpha) in RADIANTS
        et: Elevator Deflection (greek letter eta) in RADIANTS
        F: Total Thrust in NEWTON
        ef: Efficiency Indicator (in s/kg): ef = VA / F
    '''
    m = aircraft["Mass"]  # in kg
    c = aircraft["Mean Wing Chord"]  # in m
    S = aircraft["Reference Wing Area"]  # in m^2
    mo = aircraft["Thrust Vector Mounting Angle"]  # in RADIANTS
    zf = aircraft["Leverage Arm of the Thrust Vector"]  # in m  
    Fmax = aircraft["Maximum Total Thrust"]  # in N
    derLon = aircraft["Longitudinal Derivatives"]
    CL0 =  derLon[1, 0]
    CLal = derLon[1, 1]
    CLet = derLon[1, 2]
    CD0 =  derLon[0, 0]
    CDal = derLon[0, 1]
    CDet = derLon[0, 2]
    Cm0 =  derLon[2, 0]
    Cmal = derLon[2, 1]
    Cmet = derLon[2, 2]
    '''
    The following if-block only concerns the console output.
    Show the provided input parameters, if verbose is set to "all"
    '''
    if verbose == 'all':
        print('\n')
        print('{:-^31s}'.format('INPUT PARAMETERS'))
        print('{:24s}{:>6.3f}{:26s}{:>6.3f}{:26s}{:>6.3f}'.format('True Airspeed (m/s): ', VA,
              '\nAir Density (kg/m3): ', rh, '\nFlight Path Angle (deg):', ga * 180 / pi))
        print('{:^78s}'.format(''))
    '''
    Set up a non-defined 2D-Solution Vector.
    The three columns contain the values for al, et and F,
    every iteration step get's it's dedicated row.
    '''
    X = np.ndarray(shape=(it + 1, 3))
    X[0, :] = X0  # First row becomes the initial guess
    FU = np.ndarray(shape=(3,))  # Function vector
    err = np.ndarray(shape=(it + 1,))  # Error vector
    err[0] = None
    E = rh / 2 * VA ** 2 * S  # Aerodynamic Unit Force

    for i in range(it):  # Loop to the maximum allowed number of iterations

        al = X[i, 0]
        et = X[i, 1]
        F = X[i, 2]
        '''
        These are the three equations describing an equlibrium in the Aerodynmaic Frame,
        see file "Vectors.pdf" for a graphical representation of the vectors. 
        FU[0] states that the sum of forces in the vertical axis is equal to zero, 
        FU[1] states that the sum of forces in the horizontal axis is equal to zero, 
        FU[2] states the sum of moments about the lateral axis is equal to zero.
        '''
        FU[0] = + m * g * cos(ga) - E * (CL0 + CLal * al + CLet * et) - F * sin(al + mo)
        FU[1] = - m * g * sin(ga) - E * (CD0 + CDal * al + CDet * et) + F * cos(al + mo)
        FU[2] = E * c * (Cm0 + Cmal * al + Cmet * et) + F * cos(mo) * zf

        J = np.ndarray(shape=(3, 3))  # Jacobian Matrix

        '''
        These are the elements of the Jacobian Matrix. They contain the partial derivatives
        of al, et and F for all three equations. 
        The row corresponds to the equation FU[0], FU[1] or FU[2]   
        and the column to the derivative variable dal, det or dF
        '''
        J[0, 0] = - E * CLal - F * cos(al+mo)
        J[0, 1] = - E * CLet
        J[0, 2] = - sin(al + mo)
        J[1, 0] = - E * CDal - F * sin(al+mo)
        J[1, 1] = - E * CDet
        J[1, 2] = cos(al + mo)
        J[2, 0] = E * c * Cmal
        J[2, 1] = E * c * Cmet
        J[2, 2] = cos(mo) * zf


        Y = np.linalg.solve(J, -FU)

        X[i + 1, :] = X[i, :] + Y
        err[i + 1] = np.linalg.norm(Y) / np.linalg.norm(X[i + 1, :])

        if err[i + 1] < tol:
            it = i + 1
            break
        if i == it - 1:
            print('\nWarning! The Iteration loop has reached', it, 'steps!\n')

    if X[it, 2] == 0:  # Prevent #DIV/0! case where F = 0 (Aircraft is gliding without thrust)
        ef = 0
    else:
        ef = VA / X[it, 2]  # Calculate Efficiency

    '''
    The following code only concerns the console output.
    '''
    if verbose == 'all':
        print('{:-^60s}'.format('TRIM ALOGRITHM'))
        n = ['AoA (deg)', 'elevator (deg)', 'Thrust (%)']
        print('{:7}{:8}{:^17}{:^17}{:^12}'.format('Step', 'Error(%)', n[0], n[1], n[2]))
        for i in range(0, it + 1):
            print('{:<7d}{:<8.2e}{:^3s}{:>10.6f}{:^3s}{:>10.6f}{:^8s}{:>10.6f}'
                  .format(i, err[i], '', 180 / np.pi * X[i, 0], '', 180 / np.pi * X[i, 1], '',
                          100 * X[i, 2] / Fmax))
        print('{:->60s}'.format(''))
        # FINAL VALUES print(180/np.pi*X[it,0],'',180/np.pi*X[it,1],'',100*X[it,2]/Fmax)
        print('{:17}{:<10.3e}'.format('Efficiency VA/F: ', ef), '\n')
    elif verbose == 'last':
        print('{:-^70s}'.format('TRIM ALOGRITHM'))
        n = ['AoA (deg)', 'elevator (deg)', 'Thrust (%)']
        print('{:8}{:11}{:12}{:13}{:16}{:12}'.format('Steps', 'Error(%)', 'VA/F', n[0], n[1], n[2]))
        print('{:<8d}{:<11.2e}{:<12.3e}{:<13.6f}{:<16.6f}{:<12.6f}'
              .format(it+1, err[it], ef, 180 / np.pi * X[it, 0],
                      180 / np.pi * X[it, 1], 100 * X[it, 2] / Fmax))
        print('{:->70s}'.format(''))

    return np.array([X[it, 0], X[it, 1], X[it, 2], ef])  # returns al, et, F and ef





