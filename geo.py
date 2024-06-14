import numpy as np


class Geo:
    def __init__(self, domain):
        self.domain = domain

    def rot2geo(self, xin, yin):

        pollon = self.domain.pol_lon
        pollat = self.domain.pol_lat

        xgeo = [i for i in xin]
        ygeo = [i for i in yin]

        pi_r = np.pi/180.

        for i in range(len(xin)):
            ygeo[i] = 1./pi_r * np.arcsin(
                np.sin(pi_r*yin[i])*np.sin(pi_r*pollat) +
                np.cos(pi_r*yin[i])*np.cos(pi_r*xin[i]) *
                np.cos(pi_r*pollat))

            xgeo[i] = 1./pi_r * np.arctan(
                (np.cos(pi_r*yin[i])*np.sin(pi_r*xin[i])) /
                (np.sin(pi_r*pollat)*np.cos(pi_r*yin[i]) *
                 np.cos(pi_r*xin[i])-np.sin(pi_r*yin[i]) *
                 np.cos(pi_r*pollat))) + pollon + 180.

            if xgeo[i] > 180.:
                xgeo[i] -= 360.

        return (xgeo, ygeo)

    def geo2rot(self, xin, yin):

        singlepoint = None

        pollon = self.domain.pol_lon
        pollat = self.domain.pol_lat

        if type(xin) is float or type(xin) is int:
            singlepoint = True
            xin = [xin]
            yin = [yin]

        xrot = [None] * len(xin)
        yrot = [None] * len(yin)

        pi_r = np.pi/180.

        for i in range(len(xin)):

            yrot[i] = 1./pi_r * np.arcsin(
                np.sin(pi_r*yin[i])*np.sin(pi_r*pollat) +
                np.cos(pi_r*yin[i])*np.cos(pi_r*pollat) *
                np.cos(pi_r*(xin[i]-pollon)))

            xrot[i] = 1./pi_r * np.arctan(
                (np.cos(pi_r*yin[i])*np.sin(pi_r*(xin[i]-pollon))) /
                (np.cos(pi_r*yin[i])*np.sin(pi_r*pollat) *
                 np.cos(pi_r*(xin[i]-pollon)) -
                 np.sin(pi_r*yin[i])*np.cos(pi_r*pollat)))

        if singlepoint:
            return xrot[0], yrot[0]
        else:
            return xrot, yrot

    def get_corners(self, rlon, rlat):

        dx = self.domain.dx
        # print('geo', dx)

        corner_x = [rlon - dx/2,
                    rlon + dx/2,
                    rlon + dx/2,
                    rlon - dx/2]
        corner_y = [rlat - dx/2,
                    rlat - dx/2,
                    rlat + dx/2,
                    rlat + dx/2]

        corner_x, corner_y = self.rot2geo(corner_x, corner_y)

        return corner_x, corner_y
