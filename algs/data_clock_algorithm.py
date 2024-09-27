# -*- coding: utf-8 -*-

"""
/***************************************************************************
 DataClock
                                 A QGIS plugin
 Polar plot of seasonal data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-09-26
        copyright            : (C) 2024 by Florian Neukirchen
        email                : mail@riannek.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Florian Neukirchen'
__date__ = '2024-09-26'
__copyright__ = '(C) 2024 by Florian Neukirchen'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterDefinition
                       )

import plotly.express as px
import locale

from qgis_data_clock.algs.i18n import tr
from qgis_data_clock.factory import layer_to_df, dataclock


class DataClockAlgorithm(QgsProcessingAlgorithm):
    """
    Data Clock, plot seasonal time series data as a polar heat map

    For visualisation of seasonal/cyclic time series data.
    The rings of the chart show the larger, cyclic time unit 
    (e.g. year), while each ring is divided into
    smaller units shown as wedges.

    The data is binned into these wedges and the color is determined
    by the count of data rows or by an aggregation function 
    (e.g. 'sum', 'mean', 'median') on a specified column.

    The following combinations of rings and wedges are implemented:
    Year-Month, Year-Week, Year-Day, Week-Day, Day-Hour.

    The result is a html file with an interactive plotly chart.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    DATEFIELD = 'DATEFIELD'
    MODE = 'MODE'
    AGG = 'AGG'
    AGGFIELD = 'AGGFIELD'
    COLORSCALE = 'COLORSCALE'
    INVERTCOLORSCALE = 'INVERTCOLORSCALE'
    TITLE = 'TITLE'
    COLORBAR = 'COLORBAR'
    LOCALE = 'LOCALE'


    def getModeLabels(self):
        return [tr('Year-Month'), tr('Year-Week'), tr('Year-Day'), tr('Week-Day'), tr('Day-Hour')]
    
    modes = ['YM', 'YW', 'YD', 'WD', 'DH']

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Add parameters

        self.aggfunctions = ['count', 'sum', 'mean', 'median', 'min', 'max', 'std', 'first', 'last']
        self.colorscales = px.colors.named_colorscales()
        self.colorscales.sort()


        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        self.addParameter(QgsProcessingParameterEnum(
            self.MODE,
            tr('Mode'),
            self.getModeLabels(),
            defaultValue=0)) 


        self.addParameter(
            QgsProcessingParameterField(
                self.DATEFIELD,
                self.tr('Date field'),
                type=QgsProcessingParameterField.DateTime,
                parentLayerParameterName=self.INPUT
            )
        )

        self.addParameter(QgsProcessingParameterEnum(
            self.AGG,
            tr('Aggregation function'),
            self.aggfunctions,
            defaultValue=0,
            optional=True))
        
        self.addParameter(
            QgsProcessingParameterField(
                self.AGGFIELD,
                self.tr('Aggregation field'),
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT,
                optional=True
            )
        )

        self.addParameter(QgsProcessingParameterEnum(
            self.COLORSCALE,
            tr('Color Scale'),
            self.colorscales,
            defaultValue=self.colorscales.index('plasma'),
            optional=True)) 

        self.addParameter(QgsProcessingParameterBoolean(
            self.INVERTCOLORSCALE,
            tr('Invert Color Scale'),
            defaultValue=False,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            self.COLORBAR,
            tr('Show a color bar'),
            defaultValue=False,
            optional=True))

        self.addParameter(QgsProcessingParameterString(
            self.TITLE,
            tr('Title'),
            optional=True))         
    
        locale_param = QgsProcessingParameterString(
            self.LOCALE,
            tr('Locale'),
            optional=True)

        locale_param.setFlags(locale_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        
        self.addParameter(locale_param)
            
        self.addParameter(QgsProcessingParameterFileDestination(
                self.OUTPUT,
                tr('Data Clock'),
                tr('HTML files (*.html)'),
            ))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.INPUT, context)
        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)  

        datefield = self.parameterAsString(parameters, self.DATEFIELD, context)
        mode = self.modes[self.parameterAsEnum(parameters, self.MODE, context)]
        agg = self.aggfunctions[self.parameterAsEnum(parameters, self.AGG, context)]
        aggfield = self.parameterAsString(parameters, self.AGGFIELD, context)
        localestr = self.parameterAsString(parameters, self.LOCALE, context)
        localestr = localestr.strip()

        colorscale = self.colorscales[self.parameterAsEnum(parameters, self.COLORSCALE, context)]
        invertcolorscale = self.parameterAsBool(parameters, self.INVERTCOLORSCALE, context)
        colorbar = self.parameterAsBool(parameters, self.COLORBAR, context)

        if invertcolorscale:
            colorscale = colorscale + '_r'

        title = self.parameterAsString(parameters, self.TITLE, context)
        if title.strip() == '':
            title = None

        # Get the data from the layer
        neededfields = [datefield]
        if aggfield:
            neededfields.append(aggfield)

        df = layer_to_df(source, neededfields)

        # Optionally change locale
        if localestr != "":
            try:
                locale.setlocale(locale.LC_ALL, localestr + '.utf8')
                feedback.pushInfo(tr("locale set to {}").format(localestr))
            except locale.Error:
                feedback.reportError(tr("Locale not found: {}").format(localestr))
                feedback.pushInfo(tr("Continue with default locale"))

        fig = dataclock(df, datefield, mode=mode, agg=agg, agg_column=aggfield, title=title, colorscale=colorscale, colorbar=colorbar)
        
        # Reset locale to default
        locale.setlocale(locale.LC_ALL, '')

        fig.write_html(output)


        # or output names.
        return {self.OUTPUT: output}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Data Clock'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    # def groupId(self):
    #     """
    #     Returns the unique ID of the group this algorithm belongs to. This
    #     string should be fixed for the algorithm, and must not be localised.
    #     The group id should be unique within each provider. Group id should
    #     contain lowercase alphanumeric characters only and no spaces or other
    #     formatting characters.
    #     """
    #     return 'Plots'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return DataClockAlgorithm()
