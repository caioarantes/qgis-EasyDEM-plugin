# -*- coding: utf-8 -*-
"""
/***************************************************************************
 easydemDialog
                                 A QGIS plugin
 Get Digital Elevation Model (DEM) data from Google Earth Engine and plot as raster layer it contour lines, make elevation maps.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-11-13
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Caio Arantes
        email                : caiosimplicioarantes@gmail.com
        ICON SOURCE: <a href="https://www.flaticon.com/free-icons/topography" title="topography icons">Topography icons created by Freepik - Flaticon</a>
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

import os

from qgis.PyQt import uic

# PyQt5 modules
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog

# QGIS modules
from qgis.core import QgsProject, QgsMapLayer
import geopandas as gpd
import os
import platform  # Add this line

from qgis.PyQt import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication  # Add QMessageBox and QApplication

# QGIS modules
from qgis.core import QgsProject, QgsMapLayer

import os
import sys 
import subprocess
import platform
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
import geopandas as gpd
import requests
from qgis.core import QgsRasterLayer, QgsProject, QgsRasterShader, QgsColorRampShader, QgsSingleBandPseudoColorRenderer, QgsStyle
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsRasterLayer, QgsProject, QgsMapLayer, QgsVectorLayer,QgsSingleBandPseudoColorRenderer, QgsColorRampShader,QgsStyle, QgsColorRamp
from PyQt5.QtWidgets import QGridLayout, QWidget, QDesktopWidget
from qgis.core import QgsRasterLayer, QgsProject, QgsLayerTreeLayer
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsCoordinateTransform
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox
from PyQt5.QtWidgets import QApplication, QDateEdit
from PyQt5.QtCore import QDate
from dateutil.relativedelta import relativedelta
from qgis.core import QgsProject
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from qgis.utils import iface
import pandas as pd
import plotly.express as px
import io
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QPushButton
import array
import numpy as np
from scipy.signal import savgol_filter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from qgis import processing
from qgis.PyQt.QtCore import QVariant
from qgis.analysis import QgsNativeAlgorithms


import sys
import importlib

def install_earthengine_api():
    try:
        # Import pip directly and use its internal API
        import pip
        # Install the package
        pip_args = ['install', 'earthengine-api==1.3.1']
        pip.main(pip_args)
        print("Earth Engine API installed successfully.")
    except AttributeError:
        # If pip.main is not available, use the newer pip API
        from pip._internal.cli.main import main as pip_main
        pip_main(['install', 'earthengine-api==1.3.1'])
        print("Earth Engine API installed successfully.")
    except Exception as e:
        print(f"An error occurred during installation: {e}")

# Check if the Earth Engine API is already installed
try:
    # import ee
    importlib.import_module('ee')
    print("Earth Engine API is already installed.")
    import ee
except ImportError:
    print("Earth Engine API not found. Installing...")
    install_earthengine_api()
    # Reload the module after installation
    try:
        importlib.import_module('ee')
        print("Earth Engine API imported successfully.")
        import ee
    except ImportError:
        print("Earth Engine API could not be imported after installation.")
        # self.pop_aviso('Error importing Earth Engine API after installation. Please install manually.')

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'easy_dialog_base.ui'))

class easydemDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(easydemDialog, self).__init__(parent)
        self.setupUi(self)

        self.dem_datasets = { "NASADEM": {
                "ID": "NASA/NASADEM_HGT/001",
                "Resolution": [30],
                "Coverage": "Global",
                "Description": "A refined reprocessing of SRTM data, incorporating auxiliary datasets for improved accuracy and void reduction.",
                "Info": "<b>NASADEM</b> <br>"
                        "<b>ID:</b> NASA/NASADEM_HGT/001 <br>"
                        "<b>Resolution:</b> 30 meters <br>"
                        "<b>Coverage:</b> Global <br>"
                        "NASADEM integrates auxiliary data from ASTER GDEM, ICESat GLAS, and PRISM datasets. Significant improvements include enhanced phase unwrapping and void reduction using ICESat GLAS data as control. "
                        "These refinements make it ideal for detailed topographic studies and high-resolution terrain analysis. "
                        "(<a href='https://earthdata.nasa.gov/esds/competitive-programs/measures/nasadem'>Source</a>)"
            },
            "ASTER Global Digital Elevation Model (GDEM)": {
                "ID": "NASA/ASTER_GED/AG100_003",
                "Resolution": [100],
                "Coverage": "Global",
                "Description": "The Advanced Spaceborne Thermal Emission and Reflection Radiometer Global Emissivity Database (ASTER-GED) is a comprehensive product developed by NASA's JPL and Caltech. It includes elevation data, mean emissivity, LST, NDVI, and standard deviations for ASTER Thermal Infrared bands.",
                "Info": "<b>ASTER GDEM</b> <br>"
                        "<b>ID:</b> NASA/ASTER_GED/AG100_003 <br>"
                        "<b>Resolution:</b> 100 meters <br>"
                        "<b>Coverage:</b> Global <br>"
                        "Derived from clear-sky pixels using the ASTER Temperature Emissivity Separation (TES) algorithm with WVS atmospheric correction. "
                        "(<a href='https://developers.google.com/earth-engine/datasets/catalog/NASA_ASTER_GED_AG100_003/'>Source</a>)"
            },
            "Copernicus Global Digital Elevation Model (GLO-30)": {
                "ID": "COPERNICUS/DEM/GLO30",
                "Resolution": [30],
                "Coverage": "Global",
                "Description": "A Digital Surface Model (DSM) that includes Earth's surface features such as buildings, infrastructure, and vegetation, derived from the WorldDEM product.",
                "Info": "<b>Copernicus GLO-30</b> <br>"
                        "<b>ID:</b> COPERNICUS/DEM/GLO30 <br>"
                        "<b>Resolution:</b> 30 meters <br>"
                        "<b>Coverage:</b> Global <br>"
                        "Derived from the WorldDEM product, based on radar data from the TanDEM-X mission, a partnership between DLR and Airbus Defence and Space. "
                        "Earth Engine assets are ingested from DGED files. "
                        "(<a href='https://spacedata.copernicus.eu/collections/elevation'>Source</a>)"
            },
            "JAXA ALOS Global Digital Surface Model (AW3D30)": {
                "ID": "JAXA/ALOS/AW3D30/V3_2",
                "Resolution": [30],
                "Coverage": "Global",
                "Description": "A global digital surface model (DSM) dataset at ~30-meter resolution, derived from the high-resolution (5-meter) World 3D Topographic Data.",
                "Info": "<b>JAXA ALOS DSM (AW3D30)</b> <br>"
                        "<b>ID:</b> JAXA/ALOS/AW3D30/V3_2 <br>"
                        "<b>Resolution:</b> 30 meters <br>"
                        "<b>Coverage:</b> Global <br>"
                        "Version 3.2 (January 2021) includes updates to high-latitude formats, auxiliary data, and processing methods. "
                        "It uses stereo optical image matching for elevation calculation, with improvements in detecting anomalous values and incorporating updated auxiliary datasets such as coastline and AW3D version 3 data for Japan. "
                        "Clouds, snow, and ice are masked during processing, but some errors may persist near their edges. "
                        "Due to variable resolutions, this dataset is an image collection, requiring reprojection for slope computations. "
                        "(<a href='https://www.eorc.jaxa.jp/ALOS/en/aw3d30/index.htm'>Source</a>)"
            },
            "GMTED2010 (Global Multi-resolution Terrain Elevation Data 2010)": {
                "ID": "USGS/GMTED2010_FULL",
                "Resolution": [250, 500, 1000],
                "Coverage": "Global",
                "Description": "A global elevation dataset derived from multiple sources, replacing the GTOPO30 Elevation Model, with coverage at multiple resolutions.",
                "Info": "<b>GMTED2010</b> <br>"
                        "<b>ID:</b> USGS/GMTED2010_FULL <br>"
                        "<b>Resolutions:</b> 250, 500, and 1000 meters <br>"
                        "<b>Coverage:</b> Global <br>"
                        "Developed using NGA's SRTM DTED® (1-arc-second void-filled data) as the primary source. Additional data sources include non-SRTM DTED®, Canadian CDED, SPOT 5 Reference3D, US NED, Australia's GEODATA, and DEMs for Antarctica and Greenland. "
                        "This dataset offers improved global elevation data and replaces the GTOPO30 Elevation Model. "
                        "(<a href='https://topotools.cr.usgs.gov/gmted_viewer/viewer.htm'>Source</a>)"
            }

        }


        self.folder_set = False
        self.aio_set = True
        self.autentication = False

        # Call update_dem_datasets after initialization to avoid accessing dem_datasets before it's defined.
        self.update_dem_datasets()
        self.load_vector_layers()
        self.dem_dataset_combobox.currentIndexChanged.connect(self.update_dem_info)
        self.load_vector_layers_button.clicked.connect(self.load_vector_layers)
        self.vector_layer_combobox.currentIndexChanged.connect(self.get_selected_layer_path)
        # self.autenticacao.clicked.connect(self.auth)
        self.autenticacao_teste.clicked.connect(self.auth_test)
        self.desautenticacao.clicked.connect(self.auth_clear)
        self.elevacao.clicked.connect(self.elevacao_clicked)
        self.mQgsFileWidget.fileChanged.connect(self.on_file_changed)
        self.pushButtonNext.clicked.connect(self.next_button_clicked)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        print(f"Tab changed to index: {index}")
        if index == 2 and (self.pushButtonNext.isEnabled() == False):
            self.tabWidget.setCurrentIndex(1)
            return
        
        if index == 1 and (self.autentication == False):
            self.tabWidget.setCurrentIndex(0)


    def next_button_clicked(self):
        self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex() + 1)

    def on_file_changed(self, file_path):
        """Slot called when the selected file changes."""
        print(f"File selected: {file_path}")
        self.output_folder = file_path
        self.folder_set = True
        self.check_next_button()

    def check_next_button(self):
        """Enables the Next button if all required inputs are set."""
        if self.folder_set and self.aio_set:
            self.pushButtonNext.setEnabled(True)
        else:
            self.pushButtonNext.setEnabled(False)

    def update_dem_datasets(self):
        print(list(self.dem_datasets.keys()))
        self.dem_dataset_combobox.addItems(list(self.dem_datasets.keys()))
        self.update_dem_info()

    def get_unique_filename(self, base_file_name):
        """
        Generates a unique filename by checking if the file already exists
        and adding a numerical suffix to it if needed.

        Parameters:
        base_file_name (str): The base filename to use.

        Returns:
        str: The unique filename.
        """
        output_file = self.output_folder+f'/{base_file_name}.tif'
        counter = 1

        while os.path.exists(output_file):
            output_file = self.output_folder +f'/{base_file_name}_{counter}.tif'
            counter += 1

        print(f"Unique filename: {output_file}")
        return output_file

    def load_vector_layers(self) -> None:
        layers = QgsProject.instance().mapLayers().values()
        self.vector_layer_combobox.clear()
        self.vector_layer_ids = {}
        
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer_name = layer.name()
                print(f"Adding layer: {layer_name}")  # Debug: Show added layer names
                self.vector_layer_combobox.addItem(layer_name)
                self.vector_layer_ids[layer_name] = layer.id()
        
        # Debug: Show the layer dictionary after loading
        print(f"Loaded vector layers: {self.vector_layer_ids}")
        self.get_selected_layer_path()

    def get_selected_layer_path(self) -> str:
        layer_name = self.vector_layer_combobox.currentText()
        print(f"Selected layer name: {layer_name}")  # Debug: Show selected layer name
        
        layer_id = self.vector_layer_ids.get(layer_name)
        if not layer_id:
            print(f"Layer ID for '{layer_name}' not found in vector_layer_ids.")
            return None
        
        layer = QgsProject.instance().mapLayer(layer_id)
        if layer:
            print(f"Layer found: {layer.name()}, ID: {layer_id}")  # Debug: Confirm layer is found
            print(f"Layer data provider: {layer.dataProvider().dataSourceUri()}")
            
            if '.shp' in layer.dataProvider().dataSourceUri():
                self.selected_aio_layer_path = layer.dataProvider().dataSourceUri()
                self.load_vector_function()
                #enable next
                return None
            else:
                print(f"Layer '{layer_name}' is not a shapefile.")
                return None

        else:
            print(f"Layer '{layer_name}' with ID '{layer_id}' not found in the project.")
            return None


    def update_dem_info(self):
        dem_name = self.dem_dataset_combobox.currentText()
        dem_info = self.dem_datasets[dem_name]["Info"]
        self.dem_info_textbox.setHtml(dem_info)
        self.dem_resolution_combobox.clear()
        self.dem_resolution_combobox.addItems([str(res) for res in self.dem_datasets[dem_name]["Resolution"]])

    # def auth(self):
    #     print('Autenticando...')
    #     ee.Authenticate()

        
    def auth_test(self):
    # Attempt to initialize Earth Engine
        try:
            ee.Authenticate()
            ee.Initialize()
            self.pop_aviso("Authentication successful!")
            self.autentication = True
            # self.pushButtonNext.setEnabled(True)
            self.tabWidget.setCurrentIndex(1)
            print("Authentication successful!")

        except ee.EEException as e:
            if "Earth Engine client library not initialized" in str(e):
                self.pop_aviso("Authentication failed. Please authenticate.")
                print("Authentication failed. Please authenticate.")
                ee.Authenticate()
                ee.Initialize()  # Retry after authentication
            else:
                print(f"An error occurred: {e}")

    def auth_clear(self):
        print('Desautenticando...')
        """Clears the Earth Engine authentication by deleting the credentials file."""
        
        system = platform.system()
        
        # Set the path for Earth Engine credentials based on the operating system
        if system == 'Windows':
            credentials_path = os.path.join(os.environ['USERPROFILE'], '.config', 'earthengine', 'credentials')
        elif system == 'Linux':
            credentials_path = os.path.join(os.environ['HOME'], '.config', 'earthengine', 'credentials')
        elif system == 'Darwin':  # MacOS
            credentials_path = os.path.join(os.environ['HOME'], 'Library', 'Application Support', 'earthengine', 'credentials')
        else:
            raise Exception(f"Unsupported operating system: {system}")

        # Check if the credentials file exists and delete it
        if os.path.exists(credentials_path):
            os.remove(credentials_path)
            self.pop_aviso('Tolken cleared successfully.')
            print("Earth Engine authentication cleared successfully.")
        else:
            self.pop_aviso("No Earth Engine credentials found to clear.")
            print("No Earth Engine credentials found to clear.")

    def pop_aviso(self, aviso):
        QApplication.restoreOverrideCursor()
        msg = QMessageBox(parent=self)
        msg.setWindowTitle("Alerta!")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(aviso)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # Add Ok and Cancel buttons

        ret = msg.exec_()  # Get the result of the dialog

        if ret == QMessageBox.Ok:
            
            # Handle Ok button click
            print("Ok button clicked")
            # Add your code here for what to do when Ok is clicked
            return True
        elif ret == QMessageBox.Cancel:
            
            # Handle Cancel button click
            print("Cancel button clicked")
            # Add your code here for what to do when Cancel is clicked
            return False
    
    def load_vector_function(self):
        shapefile_path = self.selected_aio_layer_path
        gdf = gpd.read_file(shapefile_path)

        # Check if there is at least one geometry in the GeoDataFrame
        if not gdf.empty:
            # If the GeoDataFrame contains multiple geometries, dissolve them into one
            if len(gdf) > 1:
                self.aoi = gdf.dissolve()
            else:
                self.aoi = gdf

            # Extract the first geometry from the dissolved GeoDataFrame
            geometry = self.aoi.geometry.iloc[0]

            # Check if the geometry is a Polygon or MultiPolygon
            if geometry.geom_type in ['Polygon', 'MultiPolygon']:
                # Convert the geometry to GeoJSON format
                geojson = geometry.__geo_interface__

                # Remove the third dimension from the coordinates
                if geojson['type'] == 'Polygon':
                    geojson['coordinates'] = [list(map(lambda coord: coord[:2], ring)) for ring in geojson['coordinates']]
                elif geojson['type'] == 'MultiPolygon':
                    geojson['coordinates'] = [[list(map(lambda coord: coord[:2], ring)) for ring in polygon] for polygon in geojson['coordinates']]

                # Create an Earth Engine geometry object from the GeoJSON coordinates
                ee_geometry = ee.Geometry(geojson)

                # Convert the Earth Engine geometry to a Feature
                feature = ee.Feature(ee_geometry)

                # Create a FeatureCollection with the feature
                self.aoi = ee.FeatureCollection([feature])

                print("AOI defined successfully.")
                self.aio_set = True
                self.check_next_button()
            else:
                print("The geometry is not a valid type (Polygon or MultiPolygon).")
        else:
            print("The shapefile does not contain any geometries.")


    def elevacao_clicked(self):
        aoi = self.aoi  # Assuming 'self.aoi' holds the Earth Engine FeatureCollection

        DEM_source_key = self.dem_dataset_combobox.currentText()
        DEM_source_id = self.dem_datasets[DEM_source_key]["ID"]
        DEM_resolution = int(self.dem_resolution_combobox.currentText())
        print(f"Selected DEM source: {DEM_source_key} ({DEM_source_id})", DEM_resolution)

        # Replace invalid characters in DEM source ID for filenames
        safe_dem_source_id = DEM_source_id.replace("/", "_").replace("\\", "_")

        # Fetch DEM image based on selected source
        if DEM_source_id == 'COPERNICUS/DEM/GLO30':
            dem = ee.ImageCollection(DEM_source_id).select('DEM').mosaic().clip(aoi)
        elif DEM_source_id == 'JAXA/ALOS/AW3D30/V3_2':
            dem = ee.ImageCollection(DEM_source_id).select('DSM').mosaic().clip(aoi)
        elif DEM_source_id == 'NASA/NASADEM_HGT/001':
            dem = ee.Image(DEM_source_id).select('elevation').clip(aoi)
        elif DEM_source_id == 'USGS/GMTED2010_FULL':
            dem = ee.Image(DEM_source_id).select('min').clip(aoi)
        elif DEM_source_id == 'ASTER/ASTGTM':
            dem = ee.Image(DEM_source_id).select('elevation').clip(aoi)
        else:
            dem = ee.Image(DEM_source_id).clip(aoi).select('elevation')

        try:
            url = dem.getDownloadUrl({
                'scale': DEM_resolution,
                'region': aoi.geometry().bounds().getInfo(),
                'format': 'GeoTIFF'
            })

            # Include DEM source ID in file name, replacing invalid characters
            base_file_name = f'elevation_profile_{safe_dem_source_id}'
            output_file = self.get_unique_filename(base_file_name)

            response = requests.get(url)
            if response.status_code == 200:
                with open(output_file, 'wb') as file:
                    file.write(response.content)
                print(f"DEM image downloaded as {output_file}")
            else:
                print(f"Failed to download DEM image: {response.status_code}")
                return

        except Exception as e:
            print(f"Error during download: {e}")
            return

        # Load the vector layer for clipping
        vector_layer = QgsVectorLayer(self.selected_aio_layer_path, "Vector Layer", "ogr")

        if not vector_layer.isValid():
            print(f"Error: Vector layer '{self.selected_aio_layer_path}' is invalid.")
            return

        # Generate a unique name for the clipped output, including DEM source ID
        output_path = self.get_unique_filename(f'clipped_elevation_{safe_dem_source_id}')

        # Clip the raster using the vector layer
        try:
            processing.run("gdal:cliprasterbymasklayer", {
                'INPUT': output_file,
                'MASK': vector_layer,
                'NODATA': -9999,  # Ensure this is the right value for your dataset
                'CROP_TO_CUTLINE': True,
                'OUTPUT': output_path
            })
            print(f"Clipped raster saved to: {output_path}")

            # Load and add the clipped raster to the map canvas
            clipped_raster_layer = QgsRasterLayer(output_path, self.vector_layer_combobox.currentText() + f' - {safe_dem_source_id}')
            if clipped_raster_layer.isValid():
                QgsProject.instance().addMapLayer(clipped_raster_layer)
                print("Clipped raster added to canvas.")
            else:
                print("Failed to load clipped raster.")

        except Exception as e:
            print(f"Error during clipping: {str(e)}")
