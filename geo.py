import numpy as np
import matplotlib.path as mpath


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

    def mask_with_polygon(self, lons, lats, polygon_vertices):
        m = len(lons) - 1
        n = len(lats) - 1

        # Create the path for the polygon
        polygon_path = mpath.Path(polygon_vertices)

        # Create a mask array
        extended_mask = np.zeros((n, m), dtype=bool)
        extended_mask[:, :] = True

        # Define the sampling points within each pixel (center and midpoints of edges)
        sampling_points_detailed = [
            (0.1, 0.1), (0.1, 0.5), (0.1, 0.9),
            (0.5, 0.1), (0.5, 0.5), (0.5, 0.9),
            (0.9, 0.1), (0.9, 0.5), (0.9, 0.9)
        ]

        # Check each pixel
        for i in range(m):
            for j in range(n):
                corners = [
                    (lons[i], lats[j]),
                    (lons[i], lats[j+1]),
                    (lons[i+1], lats[j+1]),
                    (lons[i+1], lats[j]),
                ]
                corner_count = sum(polygon_path.contains_points(corners))

                # If at least 3 out of 4 corners are inside, the pixel is inside
                if corner_count >= 3:
                    extended_mask[j, i] = False
                else:
                    # Perform detailed sampling if corner check is inconclusive
                    count = 0
                    for dx, dy in sampling_points_detailed:
                        sample_lon = lons[i] + dx * \
                            (lons[i+1] - lons[i])
                        sample_lat = lats[j] + dy * \
                            (lats[j+1] - lats[j])
                        if polygon_path.contains_point((sample_lon, sample_lat)):
                            count += 1
                    # More than 50% means at least 5 out of 9 points
                    if count >= 5:
                        extended_mask[j, i] = False

        return extended_mask
