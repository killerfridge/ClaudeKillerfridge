import numpy as np
from constants import Constants, Configuration
from helpers import Atmosphere
from typing import Union

def time_to_str(time:int, conf:Union[int, Configuration]=Configuration()):
    """function for converting the time to human readable string"""
    if isinstance(conf, int):
        conf = Configuration(day=conf)
    return f"{time/conf.day:02} Days"

def get_atmos_attrs(atmos:Atmosphere, n: int, store: list[dict], time:int):
    """
    Updates the data store with the necessary data for plotting
    :param atmos: Atmosphere object
    :param n: epoch
    :param store: store object - a list of dictionaries
    :param time: planet time
    :return:
    """

    # get all the key datapoints from the atmosphere
    atmosp_temp = atmos.get_TEMP()
    U = atmos.get_U()
    V = atmos.get_V()
    lons_grid_gridded, lats_grid_gridded = atmos.lons_grid_gridded, atmos.lats_grid_gridded

    # add a new item to the data store
    store.append(
        dict(
            n=n,
            lat_grid=lats_grid_gridded,
            lon_grid=lons_grid_gridded,
            temps=atmosp_temp,
            U=U,
            V=V,
            time=time_to_str(time, atmos.conf)
        )
    )
    return None


def run_simulation(epochs:int=360,
                   c:Constants=Constants(),
                   conf:Configuration=Configuration()) -> list[dict]:
    """
    Runs the simulation for the requested number of epochs
    :param epochs: number of timesteps to run the simulation
    :param c: Constants - universal constants, as well as planet level constants
    :param conf: configuration variables
    :return store: list of dictionaries containing data about each timestep
    """

    # generate atmosphere
    atmosphere = Atmosphere(c, conf)

    # initialize sun longitude
    sun_lon = 0
    # initialize the time
    time = 0

    # initialize the store
    store = []

    for n in range(epochs):

        # update the atmosphere based on the sun location
        atmosphere.update(sun_lon)
        # store the variables
        get_atmos_attrs(atmosphere, n, store, time)
        # update the sun location
        sun_lon += conf.dt * 2 * np.pi / conf.day
        # update the local time
        time += conf.dt

    return store
