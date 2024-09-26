import pandas as pd
from qgis.PyQt.QtCore import QDate, QDateTime
from qgis.core import QgsVectorLayer

def layer_to_df(layer, fields=None):
    """
    Convert a QGIS vector layer to a pandas DataFrame

    All or selected fields of the attribute table
    are converted to columns in the DataFrame.
    Columns with date or datetime values are converted
    to pandas datetime.

    :param layer: vector layer
    :type layer: QgsVectorLayer 
    :param fields: List of field names to be included in the DataFrame, default is all fields
    :type fields: list of strings, optional
    :return: DataFrame
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