import pandas as pd
from qgis.PyQt.QtCore import QDate, QDateTime
from qgis.core import QgsVectorLayer

def layer_to_df(layer, fields=None):
    """Vector layer attribute table to pandas DataFrame

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
    """
    if not fields:
        fields = [field.name() for field in layer.fields()]
    data = []
    for feature in layer.getFeatures():
        data.append([feature[field] for field in fields])

    df = pd.DataFrame(data, columns=fields)

    # Convert fields with QDate and QDateTime to datetime
    for col in df.columns:
        if isinstance(df[col].loc[0], QDate) or isinstance(df[col].loc[0], QDateTime):
            df[col] = df[col].apply(lambda x: QDateTime(x).toPyDateTime())
    
    return df