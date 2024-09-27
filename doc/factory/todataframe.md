Module factory.todataframe
==========================

Functions
---------

`layer_to_df(layer, fields=None)`
:   Vector layer attribute table to pandas DataFrame
    
    Returns a dataframe with all or with selected fields 
    of the attribute table of a QGIS vector layer turned
    into columns.
    
    Columns with date or datetime values are converted
    to pandas datetime.
    
    Parameters
    ----------
    layer : QgsVectorLayer 
        Vector layer, e.g. layer = iface.activeLayer()
        Should have at least one date or datetime field.
    fields : list of strings, optional
        List of field names to be included in the DataFrame, default is all fields
    
    Returns
    ------- 
    pandas.DataFrame
        DataFrame with the attribute table of the layer