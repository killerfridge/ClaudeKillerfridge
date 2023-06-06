from simulation import run_simulation
from constants import Constants, Configuration
from plotting import plot_atmosphere
from datetime import datetime

if __name__ == '__main__':

    start = datetime.now()
    store = run_simulation(500, Constants(), Configuration())

    fig = plot_atmosphere(store)

    fig.write_html("Test Plot.html", config={"displayModeBar": False})

    end = datetime.now()

    print(end - start)
