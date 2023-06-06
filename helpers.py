import numpy as np
import math
import scipy.interpolate as interpolate

from constants import Constants, Configuration


def generate_fibonacci_sphere(samples: int) -> np.ndarray:

    points = np.ndarray((0, 2))

    phi = math.pi * (3. - math.sqrt(5.))  # golden angle in radians

    for i in range(samples):

        y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y)  # radius at y

        golden = phi * i  # golden angle increment

        x = math.cos(golden) * radius
        z = math.sin(golden) * radius

        theta = math.acos(z)
        varphi = np.arctan2(y,x) + np.pi

        if 0.05*np.pi < theta < 0.95*np.pi:
            points = np.append(points, [[varphi, theta]], axis=0)

    return points

class Atmosphere:

    def __init__(self,
                 c: Constants = Constants(),
                 conf: Configuration = Configuration()):
        self.us_interpolated = None
        self.vs_interpolated = None
        self.temps_interpolated = None
        self.fib_points = conf.points
        self.c = c
        self.conf = conf

        self.lons_grid = np.linspace(0, 2 * np.pi, 2 * self.conf.res)
        self.lats_grid = np.linspace(0, np.pi, self.conf.res)

        self.lons_grid_gridded, self.lats_grid_gridded = np.meshgrid(self.lons_grid, self.lats_grid)

        self.lon_us = None
        self.lon_vs = None
        self.lon_temps = None

        self.lat_us = None
        self.lat_vs = None
        self.lat_temps = None

        self.atmos = None
        self.points = None

        self._generate_world()

    def _generate_world(self):
        """Helper function for initialization"""

        # generate fibonacci sphere
        points = generate_fibonacci_sphere(self.fib_points)
        self.points = points
        self.lats = points[:, 1]
        self.lons = points[:, 0]
        self.temps = 270 + 20 * np.sin(self.lats)
        self.f = 1E-5 * np.cos(self.lats)
        self.us = np.zeros(len(self.lats), dtype=np.float)
        self.vs = np.zeros(len(self.lats), dtype=np.float)
        # create the atmosphere

        #################
        self.update_grids()

        return None

    def field_d_lat(self, field):
        return field(self.lats, self.lons, dtheta=1, grid=False) / self.c.radius

    def field_d_lon(self, field):
        return field(self.lats, self.lons, dphi=1, grid=False) / (self.c.radius * np.sin(self.lats))

    def update_temps(self, dt, sun_lon):
        """Updates the atmosphere temperature"""
        self.temps += dt * (
                self.c.solar *
                (1 - self.c.albedo) *
                np.maximum(0, np.sin(self.lats)) *
                np.maximum(0, np.sin(self.lons - sun_lon)) -
                5.67E-8 *
                (self.temps ** 4)
        ) / self.c.heat_capacity
        return None

    def update_velocity(self, dt):
        self.us -= dt * (
                self.us * self.field_d_lon(self.us_interpolated) +
                self.vs * self.field_d_lat(self.us_interpolated) +
                self.f * self.vs + self.field_d_lon(self.temps_interpolated)
        )
        self.vs -= dt * (
                self.us * self.field_d_lon(self.vs_interpolated) +
                self.vs * self.field_d_lat(self.vs_interpolated) -
                self.f * self.us + self.field_d_lat(self.temps_interpolated)
        )
        return None

    def advect(self, dt):
        self.temps -= dt * (
                self.temps * self.field_d_lon(self.us_interpolated) +
                self.us * self.field_d_lon(self.temps_interpolated) +
                self.temps * self.field_d_lat(self.vs_interpolated) +
                self.vs * self.field_d_lat(self.temps_interpolated)
        )

    def get_us_interpolated(self, s=4):
        return interpolate.SmoothSphereBivariateSpline(self.lats, self.lons, self.us, s=s)

    def get_U(self):
        return self.get_us_interpolated()(self.lats_grid, self.lons_grid)

    def get_V(self):
        return self.get_vs_interpolated()(self.lats_grid, self.lons_grid)

    def get_TEMP(self):
        return self.get_temps_interpolated()(self.lats_grid, self.lons_grid)

    def get_temps_interpolated(self, s=4):
        return interpolate.SmoothSphereBivariateSpline(self.lats, self.lons, self.temps, s=s)

    def get_vs_interpolated(self, s=4):
        return interpolate.SmoothSphereBivariateSpline(self.lats, self.lons, self.vs, s=s)

    def update_grids(self):

        temps_interpolated = self.get_temps_interpolated()
        us_interpolated = self.get_us_interpolated()
        vs_interpolated = self.get_vs_interpolated()

        lats_grid, lons_grid = self.lats_grid, self.lons_grid

        lat_us = us_interpolated(lats_grid, lons_grid, dtheta=1) / self.c.radius
        lat_vs = vs_interpolated(lats_grid, lons_grid, dtheta=1) / self.c.radius
        lat_temps = temps_interpolated(lats_grid, lons_grid, dtheta=1) / self.c.radius

        lon_us = us_interpolated(lats_grid, lons_grid, dphi=1)# / (self.c.radius * np.sin(self.lats))
        lon_vs = vs_interpolated(lats_grid, lons_grid, dphi=1)# / (self.c.radius * np.sin(self.lats))
        lon_temps = temps_interpolated(lats_grid, lons_grid, dphi=1)# / (self.c.radius * np.sin(self.lats))

        self.temps_interpolated = temps_interpolated
        self.us_interpolated = us_interpolated
        self.vs_interpolated = vs_interpolated

        self.lon_us = lon_us
        self.lon_vs = lon_vs
        self.lon_temps = lon_temps

        self.lat_us = lat_us
        self.lat_vs = lat_vs
        self.lat_temps = lat_temps

    def update(self, sun_lon:float) -> None:

        self.update_grids()

        self.update_temps(self.conf.dt, sun_lon)
        self.update_velocity(self.conf.dt)
        self.advect(self.conf.dt)




