# Import necessary libraries
import os
import subprocess

# Import local libraries
import config
import osrunner
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

# Function to write a building's OSW without running it
def prepare_building(building_data: dict):
	"""
	Create the building's results directory and write its OpenStudio Workflow file.

	Split out from batch_building_simulation so the inputs OpenStudio will be given
	can be produced -- and asserted on -- without OpenStudio: this is what
	`main.py --dry-run` and the tests use. It needs neither Docker nor dask, so it
	runs anywhere in a couple of seconds.

	Args:
		building_data (dict): A dictionary containing the building data.
	Returns:
		str: The directory holding the building's in.osw.
	"""
	# Create a new folder named 'building_1' in results_dir
	building_dir = os.path.join(config.CURRENT_PATH, config.RESULTS_PATH,
								str(building_data['non_hpxml_args']['building_id']))
	if not os.path.exists(building_dir):
		os.makedirs(building_dir)

	# Correct the paths in hpxml_args. These are read by OpenStudio, so they are
	# expressed in its filesystem rather than ours (osrunner.to_container_path).
	building_data['hpxml_args']['hpxml_path'] = \
		osrunner.to_container_path(building_dir) + '/built.xml'
	building_data['hpxml_args']['weather_station_epw_filepath'] = \
		osrunner.to_container_path(os.path.join(config.CURRENT_PATH,
												config.WEATHER_FILES_PATH,
												config.WEATHER_EPW_FILENAME))

	# Define the simulation settings
	building_data['hpxml_args']['simulation_control_timestep'] = config.SIMULATION_TIMESTEP
	building_data['hpxml_args']['simulation_control_run_period'] = config.SIMULATION_RUN_PERIOD

	# Define a new building based on the CSV data
	building_i = Building(building_data)

	# Create the OpenStudio Workflow (OSW) file for the building
	building_i.create_osw(config.CURRENT_PATH, building_dir)

	return building_dir

# Function to run a prepared building through OpenStudio
def run_building(building_dir: str):
	"""
	Run the OpenStudio workflow already written into building_dir.

	Args:
		building_dir (str): The directory holding the building's in.osw.
	Returns:
		int: The OpenStudio process return code.
	"""
	osw_path = osrunner.to_container_path(os.path.join(building_dir, 'in.osw'))
	completed = subprocess.run(osrunner.openstudio_command(osw_path))
	return completed.returncode

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
	return run_building(prepare_building(building_data))
