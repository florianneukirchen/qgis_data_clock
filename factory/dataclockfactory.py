import calendar
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# NOTE Docs generated with pdoc3: pdoc factory -o doc

def dataclock(df, date_column, mode="YM", agg='count', agg_column=None, colorscale=None, title=None, colorbar=False):
    """Figure factory for data clock plots

    For visualisation of seasonal/cyclic time series data as a polar heatmap.
    The rings of the chart show the larger, cyclic time unit 
    (e.g. year), while each ring is divided into
    smaller units shown as wedges.

    The data is binned into these wedges and the color is determined
    by the count of data rows or by an aggregation function 
    (e.g. 'sum', 'mean', 'median') on a specified column.

    The following combinations of rings and wedges are implemented:
    Year-Month, Year-Week, Year-Day, Week-Day, Day-Hour.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe with at least one datetime column
    date_column : str
        Name of a datetime column
    mode : str
        Codes mapping time units to rings and wedges (default is "YM"): 
        "YM" (Year-Month), "YW" (Year-Week), "YD" (Year-Day), "WD" (Week-Day), "DH" (Day-Hour)
    agg : str or function, optional
        Optional aggregate function to be used in combination with parameter agg_column.
        Default is count (number of rows).
    agg_column : str, optional
        Name of a numerical column for aggregation with parameter agg
    colorscale : str, optional
        Name of a plotly color scale, e.g. 'Viridis', 'Magma', 'YlGn'.
        See [Build-In Sequential Color scales](https://plotly.com/python/builtin-colorscales/#builtin-sequential-color-scales)
    title : str, optional
        Title of the plot
    colorbar : bool, optional
        Show a color bar. Default is False.

    Returns 
    -------
    plotly.graph_objects.Figure
        Plotly figure object

    Raises
    ------
    ValueError
        If date_column is not of type datetime or mode is invalid
    """

    df = df.copy()

    if not agg_column:
        agg_column =  date_column

    try:
        df['year'] = df[date_column].dt.year
    except AttributeError:
        raise ValueError("Date column must be of type datetime")

    hovertemplate = agg.title() + ': %{marker.color}<extra></extra>'
    customdata = None
    categoryarray = None

    if mode == "YM":
        df['ring'] = df['year']
        df['wedge'] = df[date_column].dt.strftime('%B') # Name of month
        hovertemplate = '%{r}<br>%{theta}<br>' + hovertemplate
        categoryarray = list(calendar.month_name)[1:] # For proper sorting of categories
        wedgerange = categoryarray # All categories in the wedges, for filling data gaps
    elif mode == "YW":
        df['ring'] = df['year']
        df['wedge'] = df[date_column].dt.isocalendar().week
        # Add the last few days to week 52 
        df.loc[df['wedge'] == 53, 'wedge'] = 52
        wedgerange = range(1, 53)
        categoryarray = [str(x) for x in range(1, 53)]
        hovertemplate = '%{r}<br>Week %{theta}<br>' + hovertemplate
    elif mode == "YD":
        df['ring'] = df['year']
        df['wedge'] = df[date_column].dt.dayofyear
        # Leap year: add last two days
        # TODO: Is there a better solution? 
        df.loc[df['wedge'] == 366, 'wedge'] = 365
        categoryarray = [str(x) for x in range(1, 366)]
        wedgerange = range(1, 366)
        hovertemplate = '%{r}<br>Day %{theta}<br>' + hovertemplate
    elif mode == "WD":
        # Use a number made from year and week as identifier for the ring 
        df['ring'] = (df[date_column].dt.isocalendar().week + df[date_column].dt.year * 100).astype(str)
        df['wedge'] = df[date_column].dt.strftime('%A')
        df['week'] = df[date_column].dt.isocalendar().week
        hovertemplate = '%{customdata|%Y-%m-%d}<br>%{theta}, Week %{customdata|%W}<br>' + hovertemplate
        categoryarray = list(calendar.day_name)
        wedgerange = categoryarray
    elif mode == "DH": 
        df['ring'] = df[date_column].dt.dayofyear + df[date_column].dt.year * 1000
        df['wedge'] = df[date_column].dt.hour
        hovertemplate = '%{customdata|%Y-%m-%d}<br>%{theta}:00 h<br>' + hovertemplate
        wedgerange = range(24)
    else:
        raise ValueError("Invalid mode")
    
    df = df.groupby(['ring', 'wedge']).agg({agg_column: agg}).reset_index()

    # Make sure all combinations are present (even if the value will be nan)
    # otherwise wedges will shown in the wrong ring
    full_index =  pd.MultiIndex.from_product([df['ring'].unique(), wedgerange], names=['ring', 'wedge'])  
    df = df.set_index(['ring', 'wedge']).reindex(full_index).reset_index()

    # Set customdata: reconstructing the date from ring and wedge makes shure
    # that hover info is also shown when data is nan
    if mode == "DH":
        customdata = pd.to_datetime(df['ring'], format='%Y%j')
    elif mode == "WD":
        customdata = pd.to_datetime(df['ring'].astype(str) + '-' + df['wedge'], format='%Y%W-%A') 

    # Passing theta and r as string makes them categorical;  
    # numerical values would be interpreted as angles and radii
    fig = go.Figure(go.Barpolar(
        r=df['ring'].astype(str),
        theta=df['wedge'].astype(str),
        marker_color=df[agg_column],
        marker_colorscale=colorscale,
        hovertemplate=hovertemplate,
        customdata=customdata,
        ))

    fig.update_layout(
        title=title,
        polar_bargap=0,
        polar_radialaxis_visible=False,
        polar_radialaxis_type='linear',
        polar_angularaxis_direction='clockwise',
        )
    
    if colorbar:
        fig.update_traces(
            marker_colorbar_thickness=20,
        )
    if categoryarray:
        fig.update_layout(
            polar_angularaxis_categoryarray=categoryarray,
            polar_angularaxis_categoryorder='array',
            )

    # No ticks for YD mode, as it is too crowded
    if mode == 'YD':
        fig.update_layout(
            polar_angularaxis_visible=False,
        )

    return fig