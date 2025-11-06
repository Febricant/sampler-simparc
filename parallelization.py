# Import necessary libraries
import os
import subprocess

# Import local libraries
import config
from building import Building

# Function to postprocess the results of each building simulation
def postprocess_building_simulation(building_dir: str):
	"""
	This function will be used to postprocess the results of each building simulation
	It will take the directory of the building simulation as input and process the results
	to extract useful information such as errors, warnings, and performance metrics.
	Args:
		building_dir (str): The directory where the building simulation results are stored.
	Returns:
		None
	"""
	# Implement postprocessing logic here
	pass

# Define the function to be parallelized
def batch_building_simulation(building_data: dict):
	"""
	This function will be used to run the building simulation in parallel
	It will take a dictionary of building data as input and run the simulation
	using the OpenStudio Workflow (OSW) file created for that building.
	The function will return the results of the simulation.

	Args:
		building_data (dict): A dictionary containing the building data.
	"""
	# Create a new folder named 'building_1' in results_dir
	building_dir = os.path.join(config.CURRENT_PATH, config.RESULTS_PATH, 
								str(building_data['non_hpxml_args']['building_id']))
	if not os.path.exists(building_dir):
		os.makedirs(building_dir)
	
	# Correct the paths in hpxml_args
	building_data['hpxml_args']['hpxml_path'] = building_dir + '/built.xml'
	building_data['hpxml_args']['weather_station_epw_filepath'] = os.path.join(config.CURRENT_PATH, 
																 config.WEATHER_FILES_PATH, 
																 building_data['hpxml_args']['weather_station_epw_filepath'])	

	# Define the simulation settings
	building_data['hpxml_args']['simulation_control_timestep'] = config.SIMULATION_TIMESTEP
	building_data['hpxml_args']['simulation_control_run_period'] = config.SIMULATION_RUN_PERIOD

	# Define a new building based on the CSV data
	building_i = Building(building_data)

	# Create the OpenStudio Workflow (OSW) file for the building	
	building_i.create_osw(config.CURRENT_PATH, building_dir)

	# Run the OpenStudio workflow using the command line
	subprocess.run(["openstudio", "run", "-w", building_dir+"/in.osw"]) # with devcontainer
	#subprocess.run([config.OPENSTUDIO_EXE, "run", "-w", building_dir+"/in.osw"]) # with OpenStudio SDK mentioned in config.py

	return