# Import necessary libraries
import pandas as pd
import os,sys
from pathlib import Path
from dask.distributed import LocalCluster, Client, progress, performance_report # dask for parallel processing

# Import local libraries
import config	# configuration file for paths and constants	
from preprocessing import preprocess_data_types, preprocess_data_to_dict	# function to preprocess the data
from upgrading import apply_upgrades	# function to apply upgrades to the building data
from parallelization import batch_building_simulation	# function to run simulations in parallel (using the Building class)
from postprocessing import postprocess_results	# function to post-process the results

if __name__ == "__main__":

	# Check if enough arguments are provided
	if len(sys.argv) < 2:
		raise TypeError("Missing building sample input .csv file path.")
	elif len(sys.argv) > 2:
		raise TypeError("Error: Too many arguments.")
	else:
		pass

	# Get input file path
	csv_input_path = sys.argv[1]

	# Check if file exists and is a .csv
	path_object = Path(csv_input_path)
	if path_object.is_file() and path_object.suffix == ".csv":
		pass
	elif path_object.is_file() and path_object.suffix != ".csv":
		raise TypeError("invalid file")
	else:
		raise FileNotFoundError("File not found.")

	# Get the building properties from a CSV file
	data = pd.read_csv(csv_input_path)

	# Preprocess the data to ensure it meets the constraints
	data, list_columns_hpxml = preprocess_data_types(data, config.ARGS_CONSTRAINTS)

	# Apply upgrades
	data_upgrades = apply_upgrades(data)  # Apply upgrades to the building data

	# Preprocess the data to get a dictionary
	data_dict = preprocess_data_to_dict(data, config.ARGS_CONSTRAINTS, list_columns_hpxml)
	data_upgrades_dict = preprocess_data_to_dict(data_upgrades, config.ARGS_CONSTRAINTS, list_columns_hpxml)

	# Create a new folder named 'results' in current_dir
	results_dir = os.path.join(config.CURRENT_PATH, config.RESULTS_PATH)
	if not os.path.exists(results_dir):
		os.makedirs(results_dir)
	
	# Initialize Dask cluster and client
	cluster = LocalCluster(n_workers=config.DASK_NUM_WORKERS)
	client = Client(cluster)

	with performance_report(filename="dask-report-baseline.html"):
		# Print the number of simulations to run
		print(f"Running {len(data_dict)} baseline simulations with {config.DASK_NUM_WORKERS} workers...")
		# Parallel simulations with Dask
		futures = client.map(batch_building_simulation, data_dict)
		# Show progress bar
		progress(futures)
		# Execute the futures and gather the results
		client.gather(futures)
		# Print completion message
		print("Baseline simulations completed.")
	
	if data_upgrades_dict is not None:
		with performance_report(filename="dask-report-upgrades.html"):
			# Print the number of simulations to run
			print(f"Running {len(data_upgrades_dict)} upgrade simulations with {config.DASK_NUM_WORKERS} workers...")
			# Parallel simulations with Dask for upgraded buildings
			futures_upgrades = client.map(batch_building_simulation, data_upgrades_dict)
			# Show progress bar
			progress(futures_upgrades)
			# Execute the futures and gather the results
			client.gather(futures_upgrades)
			# Print completion message
			print("Upgrade simulations completed.")

	# Close the Dask client and cluster
	client.close()
	cluster.close()

	# Prepare data for results post-processing
	data_all = pd.concat([data, data_upgrades], ignore_index=True)
	data_all_dict = data_all.to_dict(orient='records')

	# Initialize Dask cluster and client for post-processing
	cluster = LocalCluster(n_workers=config.DASK_NUM_WORKERS_POSTPROCESSING)
	client = Client(cluster)

	with performance_report(filename="dask-report-postprocessing.html"):
		# Print the number of building results to post-process
		print(f"Running post-processing for {len(data_all_dict)} simulation results with {config.DASK_NUM_WORKERS_POSTPROCESSING} workers...")
		# Parallel post-processing with Dask
		futures = client.map(postprocess_results, data_all_dict)
		# Show progress bar
		progress(futures)
		# Execute the futures and gather the post-processed results
		client.gather(futures)
		# Print completion message
		print("Postprocessing completed.")

	# Close the Dask client and cluster
	client.close()
	cluster.close()