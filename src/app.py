import pandas as pd
import plotly.express as px
import numpy as np


def run(data, save_path, scope):
    """
    data: List of data to be plotted.
    save_path: Path for html export
    scope: "world" or "europe" scope depending on the dataset
    Plotting all the data with routes of TSP.
    """
    df = pd.DataFrame(data, columns=['lat', 'lon', 'generation', 'place', 'distance', 'fitness', 'color'])

    fig = px.line_geo(df, lat="lat", lon="lon", animation_frame="generation", title="TSP using GA", markers=True,
                      hover_data=["place", "distance"], color='color', locationmode='country names')
    fig.update_layout(showlegend=False)
    fig.update_geos(
        visible=True, resolution=50, scope=scope,
        showcountries=True, countrycolor="Black",
        showsubunits=True, subunitcolor='Brown')

    fitness = df.fitness.unique()
    if len(fitness) < len(fig.frames):
        clone = fitness[-1]
        fitness = np.concatenate((fitness, [clone for _ in range(len(fig.frames) - len(fitness))]))

    for i, frame in enumerate(fig.frames):
        frame.layout.title = "Shortest distance: " + str(round(fitness[i])) + "km (fitness)"

    fig.show()
    fig.write_html(save_path)
