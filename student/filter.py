# ---------------------------------------------------------------------
# Project "Track 3D-Objects Over Time"
# Copyright (C) 2020, Dr. Antje Muntzinger / Dr. Andreas Haja.
#
# Purpose of this file : Kalman filter class
#
# You should have received a copy of the Udacity license together with this program.
#
# https://www.udacity.com/course/self-driving-car-engineer-nanodegree--nd013
# ----------------------------------------------------------------------
#

# imports
import numpy as np

# add project directory to python path to enable relative imports
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import misc.params as params


class Filter:
    '''Kalman filter class'''

    def __init__(self):
        self.dim_state = params.dim_state
        self.dt = params.dt
        self.q = params.q

    def F(self):
        n = self.dim_state
        dt = self.dt

        F = np.identity(n).reshape(n, n)
        F[0, n - 3] = dt
        F[1, n - 2] = dt
        F[2, n - 1] = dt

        return np.matrix(F)

    def Q(self):
        n = self.dim_state
        q = self.q
        dt = self.dt

        q1 = ((dt ** 3) / 3) * q
        q2 = ((dt ** 2) / 2) * q
        q3 = q * dt

        return np.matrix([[q1, 0, 0, q2, 0, 0],
                          [0, q1, 0, 0, q2, 0],
                          [0, 0, q1, 0, 0, q2],
                          [q2, 0, 0, q3, 0, 0],
                          [0, q2, 0, 0, q3, 0],
                          [0, 0, q2, 0, 0, q3]])

    def predict(self, track):
        F = self.F()
        Q = self.Q()

        x = track.x
        P = track.P

        x = F * x  # predict state
        P = F * P * F.transpose() + Q  # predict covariance

        track.set_x(x)
        track.set_P(P)

    def update(self, track, meas):
        P = track.P
        x = track.x
        I = np.identity(self.dim_state)

        H = meas.sensor.get_H(x)  # measurement matrix
        gamma = self.gamma(track, meas)  # residual
        S = self.S(track, meas, H)  # covariance of residual
        K = P * H.transpose() * np.linalg.inv(S)  # Kalman gain
        x = x + K * gamma  # state update
        P = (I - K * H) * P  # covariance update

        track.set_x(x)
        track.set_P(P)

        track.update_attributes(meas)

    def gamma(self, track, meas):
        x = track.x
        z = meas.z

        gamma = z - meas.sensor.get_hx(x)  # residual

        return gamma

    def S(self, track, meas, H):
        P = track.P
        R = meas.R
        S = H * P * H.transpose() + R

        return S
