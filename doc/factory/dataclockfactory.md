Module factory.dataclockfactory
===============================

Functions
---------

`dataclock(df, date_column, mode='YM', agg='count', agg_column=None, colorscale=None, title=None, colorbar=False)`
:   Figure factory for data clock plots
    
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