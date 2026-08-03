# Import necessary libraries
import os

# Import local libraries
from hpxml_input_schema import extract_arguments_from_xml	# extract arguments from HPXML schema

# Define the path to the HPXML schema file
HPXML_SCHEMA_FILE = "measures/BuildResidentialHPXML/measure.xml"
ARGS_CONSTRAINTS = extract_arguments_from_xml(HPXML_SCHEMA_FILE)

# Define the paths
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = "results"
MEASURES_PATH = "measures"
WEATHER_FILES_PATH = "weather"
WEATHER_EPW_FILENAME = "CAN_AB_Calgary.Intl.AP.718770_CWEC2016.epw" # location fixed to Calgary

# How to invoke OpenStudio. See osrunner.py.
# "auto"   - use an installed binary if there is one, else Docker. This keeps the
#            devcontainer working (openstudio on PATH, no docker inside it) while
#            a bare host falls through to the image.
# "docker" - always shell out to DOCKER_IMAGE, which already carries OpenStudio
#            3.9.0. Runs from an ordinary Windows shell; no devcontainer needed.
# "native" - always call an installed binary directly (OPENSTUDIO_EXE, else PATH).
OPENSTUDIO_RUNNER = "auto"
DOCKER_IMAGE = "simparc-dev:latest"
CONTAINER_WORKSPACE = "/workspace" # where the project is bind-mounted in the container

# Define the path to the openstudio executable (used when OPENSTUDIO_RUNNER = "native")
# NOT NEEDED IF USING DEVCONTAINER
OPENSTUDIO_EXE = "openstudio-3.9.0/bin/openstudio"

# Define the settings for Dask
DASK_NUM_WORKERS = 5
DASK_NUM_WORKERS_POSTPROCESSING = 5

# Define the simulation settings
SIMULATION_TIMESTEP = 15 # minutes - must be integer and a divisor of 60 
SIMULATION_RUN_PERIOD = "Jan 1 - Dec 31" # Define the simulation run using the same format (First 3 letters of month and day number) e.g., "Jan 1 - Dec 31", "Jun 1 - Aug 31"

# Define the output settings
ADD_COMPONENT_LOADS = False # If true, adds the calculation of heating/cooling component loads (not enabled by default for faster performance).
SKIP_VALIDATION = False # If true, skips the validation of the HPXML file for faster performance.
DEBUG_MODE = True # If true, enables debug mode for more verbose output (OSM, E+ and additional log output files).
INCLUDE_ANNUAL_TOTAL_CONSUMPTIONS = True
INCLUDE_ANNUAL_FUEL_CONSUMPTIONS = True
INCLUDE_ANNUAL_END_USE_CONSUMPTIONS = True
INCLUDE_ANNUAL_SYSTEM_USE_CONSUMPTIONS = True
INCLUDE_ANNUAL_EMISSIONS = False
INCLUDE_ANNUAL_EMISSION_FUELS = False
INCLUDE_ANNUAL_EMISSION_END_USES = False
INCLUDE_ANNUAL_TOTAL_LOADS = True
INCLUDE_ANNUAL_UNMET_HOURS = True
INCLUDE_ANNUAL_PEAK_FUELS = True
INCLUDE_ANNUAL_PEAK_LOADS = True
INCLUDE_ANNUAL_COMPONENT_LOADS = True
INCLUDE_ANNUAL_HOT_WATER_USES = True
INCLUDE_ANNUAL_HVAC_SUMMARY = True
INCLUDE_ANNUAL_RESILIENCE = True
TIMESERIES_FREQUENCY = "timestep" # Options: "none", "timestep", "hourly", "daily", "monthly"
INCLUDE_TIMESERIES_TOTAL_CONSUMPTIONS = True
INCLUDE_TIMESERIES_FUEL_CONSUMPTIONS = True
INCLUDE_TIMESERIES_END_USE_CONSUMPTIONS = True
INCLUDE_TIMESERIES_SYSTEM_USE_CONSUMPTIONS = False
INCLUDE_TIMESERIES_EMISSIONS = False
INCLUDE_TIMESERIES_EMISSION_FUELS = False
INCLUDE_TIMESERIES_EMISSION_END_USES = False
INCLUDE_TIMESERIES_HOT_WATER_USES = False
INCLUDE_TIMESERIES_TOTAL_LOADS = False
INCLUDE_TIMESERIES_COMPONENT_LOADS = False
INCLUDE_TIMESERIES_UNMET_HOURS = False
INCLUDE_TIMESERIES_ZONE_TEMPERATURES = False
INCLUDE_TIMESERIES_ZONE_CONDITIONS = False
INCLUDE_TIMESERIES_AIRFLOWS = False
INCLUDE_TIMESERIES_WEATHER = True
INCLUDE_TIMESERIES_RESILIENCE = False
TIMESERIES_TIMESTAMP_CONVENTION = "start" # Options: "start", "end"
ADD_TIMESERIES_DST_COLUMN = False # If true, adds a column for Daylight Saving Time (DST) in the timeseries output.
ADD_TIMESERIES_UTC_COLUMN = True # If true, adds a column for UTC time in the timeseries output.
USER_OUTPUT_VARIABLES = "" # Comma-separated list of user-defined output variables to include
USER_OUTPUT_METERS = "" # Comma-separated list of user-defined output meters to include

# Define the upgrade settings
UPGRADE_SETTINGS = None
#Example UPGRADE_SETTINGS structure:
# UPGRADE_SETTINGS = {
# 	"Set of upgrades 1": {
# 		"Filters":[],  # List of filters to select the targeted buildings for the upgrades
# 		"Adoption rate": 0.5,  # Fraction of buildings that will adopt the upgrades among the targeted buildings
# 		"Upgrades": {
# 			"Wall insulation": {
# 				"improvement_rate": 0.2,  # Fractional improvement rate for wall insulation
# 			},
# 			"Window properties": {
# 				"improvement_rate_uvalue": 0.3,  # Fractional improvement rate for U-value
# 				"improvement_rate_shgc": 0.15,  # Fractional improvement rate for SHGC
# 			},
# 			"Air leakage": {
# 				"improvement_rate": 0.25,  # Fractional improvement rate for air leakage
# 			}
# 		}
# 	},
# 	"Set of upgrades 2": {
# 		"Filters":[("geometry_unit_type", "==", "single-family detached"),
# 			 ("geometry_unit_num_bedrooms", ">=", 3)],  # List of filters to select the targeted buildings for the upgrades
# 		"Adoption rate": 0.8,  # Percentage of buildings that will adopt the upgrades among the targeted buildings
# 		"Upgrades": {
# 			"Wall insulation": {
# 				"improvement_rate": 0.15,  # Fractional improvement rate for wall insulation
# 			},
# 			"Window properties": {
# 				"improvement_rate_uvalue": 0.2,  # Fractional improvement rate for U-value
# 				"improvement_rate_shgc": 0.1,  # Fractional improvement rate for SHGC
# 			},
# 			"Air leakage": {
# 				"improvement_rate": 0.2,  # Fractional improvement rate for air leakage
# 			}
# 		}
# 	}
# }