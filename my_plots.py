from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.io import show, output_notebook
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import CheckboxGroup
from bokeh.layouts import row, WidgetBox
from bokeh.palettes import Category20c
from bokeh.plotting import figure
import pandas as pd
import numpy as np

output_notebook()

def PiePlot(df1):

    # Function for handling plot interaction (data selection):
    def modify_doc(doc):

        # Function for creating a dataset from county selection
        def make_dataset(df, county_list):
            source = pd.DataFrame(columns=['start_angle', 'end_angle', 'color', 'legend'])

            percents = df.loc[county_list].values.sum(axis=0) / df.loc[county_list].values.sum()

            source['start_angle'] = np.hstack((0, np.cumsum(percents)[:-1])) * 2 * np.pi
            source['end_angle'] = np.cumsum(percents) * 2 * np.pi
            source['legend'] = df.columns
            source['color'] = Category20c[len(source)]
            source['percents'] = percents.round(4) * 100

            source = source[source['percents'] > 0]

            return ColumnDataSource(source)

        # Function for making a pie plot:
        def make_plot(src):
            # Make bokeh figure:
            p = figure(plot_height=600, plot_width=600, toolbar_location=None, tools="")

            # Add pie slices:
            p.wedge(x=0, y=1, radius=0.5, start_angle='start_angle', end_angle='end_angle',
                    line_color="white", fill_color='color', legend='legend', source=src)

            # Remove labels, axes and grid:
            p.axis.axis_label = None
            p.axis.visible = False
            p.grid.grid_line_color = None

            # Add hover information:
            hover = HoverTool(tooltips=[('Ethnicity', '@legend'), ('Percent', '@percents')])
            p.add_tools(hover)

            return p

        # Function for graph update (after data selection):
        def update(attr, old, new):
            # Get county selection from check box:
            counties_to_plot = [county_selection.labels[i] for i in county_selection.active]
            # If no counties are selected - plot for all counties:
            if len(counties_to_plot) == 0:
                counties_to_plot = county_selection.labels

            # Make a new dataset based on the selected counties
            new_src = make_dataset(df1, counties_to_plot)

            # Update the source used the quad glpyhs
            src.data.update(new_src.data)

        # Include county selection check box:
        county_selection = CheckboxGroup(labels=df1.index.values.tolist(), active=[])
        county_selection.on_change('active', update)

        # Wrap the check box inside a widget box:
        controls = WidgetBox(county_selection)

        # Select all counties as initial state:
        initial_counties = county_selection.labels

        # Create initial dataset:
        src = make_dataset(df1, initial_counties)

        # Make the graph:
        p = make_plot(src)
        layout = row(controls, p)
        doc.add_root(layout)

    # Set up an application handler:
    handler = FunctionHandler(modify_doc)
    app = Application(handler)
    show(app)


def BarPlot(df3):

    names = [str(x) for x in df3.columns]
    colors = Category20c[len(names)]
    counties = [str(x) for x in df3.index]

    p = figure(x_range=counties, plot_height=500, plot_width=900, toolbar_location=None, tools="")

    bottom = df3[names[0]].values * 0

    for i in range(len(names)):
        top = bottom + df3[names[i]].values

        source = pd.DataFrame(columns=['x', 'top', 'bottom', 'name', 'value'])

        source['x'] = counties
        source['top'] = top
        source['bottom'] = bottom
        source['color'] = [colors[i]] * len(counties)
        source['name'] = [names[i]] * len(counties)
        source['value'] = df3[names[i]].values

        p.vbar(x='x', top='top', bottom='bottom', width=0.8, color='color', name='name', source=source)

        bottom = top

    if len(counties) < 10:
        hover = HoverTool(tooltips=[('Service', '@name'), ('Availability', '@value{(0.0 a)} %')])
    else:
        hover = HoverTool(tooltips=[('County', '@x'), ('Service', '@name'), ('Availability', '@value{(0.0 a)} %')])

    p.add_tools(hover)
    p.y_range.start = 0
    p.x_range.range_padding = 0.025
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    #p.yaxis.visible = None

    if len(counties) > 10:
        p.xaxis.major_label_orientation = np.pi / 2

    show(p)
