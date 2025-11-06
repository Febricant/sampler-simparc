# Import libraries
import os
import json

# Import local libraries
import config

# Class to define a building and its methods/attributes
class Building:
	"""
	The current class Building is used to define a building based on inputs defined in the
	OpenStudio-HPXML module developed by NREL. This class contains multiple methods, including:
	- __init__: Initialize the Building object with HPXML and non-HPXML arguments.
	- create_osw: Create an OpenStudio Workflow (OSW) file based on the building's arguments.
	- Other methods will be added later to extend the functionality of the Building class.

	"""
	def __init__(self, building_data: dict):
		"""
		Initialize the Building object with HPXML and non-HPXML arguments.

		Args:
			building_data (dict): A dictionary containing the HPXML and non-HPXML arguments for the building.
			
		"""
		# Check if hpxml_args is a dictionary
		if not isinstance(building_data, dict):
			raise TypeError("building_data must be a dictionary")

		self.hpxml_args = building_data['hpxml_args']
		self.non_hpxml_args = building_data['non_hpxml_args']

		pass

	def create_osw(self, project_dir, building_dir):
		"""
		Create an OpenStudio Workflow (OSW) file based on the building's HPXML arguments.

		Args:
			project_dir (str): The directory where the project is located.
			building_dir (str): The directory where the building's OSW file will be created.

		Returns:
			None
		"""
		# Initialize the content of a OSW (OpenStudio Workflow) file
		self.osw_content = {}

		# Define the path to the measures
		self.osw_content['measure_paths'] = [os.path.join(project_dir, config.MEASURES_PATH)]
		
		# Initialize the list of steps in the OSW content
		self.osw_content['steps'] = []

		# Step 1 - BuildResidentialHPXML
		step1 = {
			'measure_dir_name': 'BuildResidentialHPXML',
			'arguments': self.hpxml_args
		}
		self.osw_content['steps'].append(step1)

		# Step 2 - BuildResidentialScheduleFile
		step2 = {
			'measure_dir_name': 'BuildResidentialScheduleFile',
			'arguments': {
				"hpxml_path": building_dir+"/built.xml",
				"output_csv_path": building_dir+"/stochastic.csv",
				"hpxml_output_path": building_dir+"/built-stochastic-schedules.xml"
			}}
		self.osw_content['steps'].append(step2)

		# Step 3 - ModifyStochasticFilePython - Modify the stochastic file generated in Step 2
		# step3 = {
		# 	'measure_dir_name': 'ModifyStochasticFilePython',
		# 	'arguments': {
		# 		"csv_path": building_dir+"/stochastic.csv"
		# 	}}
		# self.osw_content['steps'].append(step3)

		# Step 4 - HPXMLtoOpenStudio
		step4 = {
			'measure_dir_name': 'HPXMLtoOpenStudio',
			'arguments': {
				"hpxml_path": building_dir+"/built-stochastic-schedules.xml",
				"output_dir": "..",
				"output_format": "csv",
				"add_component_loads": config.ADD_COMPONENT_LOADS,
				"skip_validation": config.SKIP_VALIDATION,
				"debug": config.DEBUG_MODE
			}}
		self.osw_content['steps'].append(step4)

		# Step 5 - ReportSimulationOutput
		step5 = {
			'measure_dir_name': 'ReportSimulationOutput',
			'arguments': {
				"output_format": "csv",
				"include_annual_total_consumptions": config.INCLUDE_ANNUAL_TOTAL_CONSUMPTIONS,
				"include_annual_fuel_consumptions": config.INCLUDE_ANNUAL_FUEL_CONSUMPTIONS,
				"include_annual_end_use_consumptions": config.INCLUDE_ANNUAL_END_USE_CONSUMPTIONS,
				"include_annual_system_use_consumptions": config.INCLUDE_ANNUAL_SYSTEM_USE_CONSUMPTIONS,
				"include_annual_emissions": config.INCLUDE_ANNUAL_EMISSIONS,
				"include_annual_emission_fuels": config.INCLUDE_ANNUAL_EMISSION_FUELS,
				"include_annual_emission_end_uses": config.INCLUDE_ANNUAL_EMISSION_END_USES,
				"include_annual_total_loads": config.INCLUDE_ANNUAL_TOTAL_LOADS,
				"include_annual_unmet_hours": config.INCLUDE_ANNUAL_UNMET_HOURS,
				"include_annual_peak_fuels": config.INCLUDE_ANNUAL_PEAK_FUELS,
				"include_annual_peak_loads": config.INCLUDE_ANNUAL_PEAK_LOADS,
				"include_annual_component_loads": config.INCLUDE_ANNUAL_COMPONENT_LOADS,
				"include_annual_hot_water_uses": config.INCLUDE_ANNUAL_HOT_WATER_USES,
				"include_annual_hvac_summary": config.INCLUDE_ANNUAL_HVAC_SUMMARY,
				"include_annual_resilience": config.INCLUDE_ANNUAL_RESILIENCE,
				"timeseries_frequency": config.TIMESERIES_FREQUENCY,
				"include_timeseries_total_consumptions": config.INCLUDE_TIMESERIES_TOTAL_CONSUMPTIONS,
				"include_timeseries_fuel_consumptions": config.INCLUDE_TIMESERIES_FUEL_CONSUMPTIONS,
				"include_timeseries_end_use_consumptions": config.INCLUDE_TIMESERIES_END_USE_CONSUMPTIONS,
				"include_timeseries_system_use_consumptions": config.INCLUDE_TIMESERIES_SYSTEM_USE_CONSUMPTIONS,
				"include_timeseries_emissions": config.INCLUDE_TIMESERIES_EMISSIONS,
				"include_timeseries_emission_fuels": config.INCLUDE_TIMESERIES_EMISSION_FUELS,
				"include_timeseries_emission_end_uses": config.INCLUDE_TIMESERIES_EMISSION_END_USES,
				"include_timeseries_hot_water_uses": config.INCLUDE_TIMESERIES_HOT_WATER_USES,
				"include_timeseries_total_loads": config.INCLUDE_TIMESERIES_TOTAL_LOADS,
				"include_timeseries_component_loads": config.INCLUDE_TIMESERIES_COMPONENT_LOADS,
				"include_timeseries_unmet_hours": config.INCLUDE_TIMESERIES_UNMET_HOURS,
				"include_timeseries_zone_temperatures": config.INCLUDE_TIMESERIES_ZONE_TEMPERATURES,
				"include_timeseries_zone_conditions": config.INCLUDE_TIMESERIES_ZONE_CONDITIONS,
				"include_timeseries_airflows": config.INCLUDE_TIMESERIES_AIRFLOWS,
				"include_timeseries_weather": config.INCLUDE_TIMESERIES_WEATHER,
				"include_timeseries_resilience": config.INCLUDE_TIMESERIES_RESILIENCE,
				"timeseries_timestamp_convention": config.TIMESERIES_TIMESTAMP_CONVENTION,
				"add_timeseries_dst_column": config.ADD_TIMESERIES_DST_COLUMN,
				"add_timeseries_utc_column": config.ADD_TIMESERIES_UTC_COLUMN,
				"user_output_variables": config.USER_OUTPUT_VARIABLES, 
				"user_output_meters": config.USER_OUTPUT_METERS 
			}}
		self.osw_content['steps'].append(step5)

		# Write the OSW content to a file
		with open(building_dir+'/in.osw', 'w') as f:
			json.dump(self.osw_content, f, indent=2)

		pass