import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from helpers import Atmosphere
from matplotlib.patches import Rectangle


def plotting(atmos: Atmosphere):

    # TODO: Understand how this function operates

    atmosp_temp = atmos.get_TEMP()
    U = atmos.get_U()
    V = atmos.get_V()
    lons_grid_gridded, lats_grid_gridded = atmos.lons_grid_gridded, atmos.lats_grid_gridded

    quiver_resample = 4
    plt.pcolormesh(lons_grid_gridded, lats_grid_gridded, atmosp_temp)
    plt.gca().add_patch(Rectangle((0, 0), 2 * np.pi, np.pi, linewidth=1, edgecolor='w', facecolor='none'))
    plt.quiver(lons_grid_gridded[::quiver_resample, ::quiver_resample],
               lats_grid_gridded[::quiver_resample, ::quiver_resample], U[::quiver_resample, ::quiver_resample],
               V[::quiver_resample, ::quiver_resample])
    plt.scatter(atmos.lons, atmos.lats, s=0.5, color='black')

    plt.xlim((0, 2 * np.pi))
    plt.ylim((0, np.pi))
    plt.title(str(len(atmos.points)) + ' points')

    plt.pause(0.01)

    print('T: ', round(atmosp_temp.max() - 273.15, 1), ' - ', round(atmosp_temp.min() - 273.15, 1), ' C')
    print('U: ', round(U.max(), 2), ' - ', round(U.min(), 2), ' V: ', round(V.max(), 2), ' - ', round(V.min(), 2))


def plot_atmosphere(store: list[dict]):
    fig = go.Figure(frames=[
        go.Frame(data=go.Heatmap(
            z=n['temps'],
            x=n['lat_grid'][:, 0],
            y=n['lon_grid'][0, :],
            hoverongaps=False,
        ), name=n['time']) for n in store])

    fig.add_trace(go.Heatmap(
        z=store[0]['temps'],
        x=store[0]['lat_grid'][:, 0],
        y=store[0]['lon_grid'][0, :],
        hoverongaps=False
    ))

    def frame_args(duration):
        return {
            "frame": {"duration": duration},
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},
        }

    sliders = [
        {
            "pad": {"b": 10, "t": 60},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                {
                    "args": [[f.name], frame_args(0)],
                    "label": str(f.name),
                    "method": "animate",
                }
                for k, f in enumerate(fig.frames)
            ],
        }
    ]

    # Layout
    fig.update_layout(
        width=1200,
        height=600,
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, frame_args(50)],
                        "label": "&#9654;",  # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;",  # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
        ],
        sliders=sliders
    )

    return fig
