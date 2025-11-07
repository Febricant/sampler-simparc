# Import necessary libraries
import pandas as pd
import json
import os
import pyarrow as pa
import pyarrow.parquet as pq

# Import local libraries
import config

# Define the postprocessing function
def postprocess_results(i):
	"""
	This function is used to post-process the results of the simulation
	For now, it processes simulation status and error messages for each building.
	Inputs:
	- i: dictionary containing the building properties (from the input CSV)
	Outputs:
	- None (results are saved as parquet files in the results directory)

	"""
	# Define the results directory
	results_dir = os.path.join(config.CURRENT_PATH, config.RESULTS_PATH)
	# Define the path to the building directory
	building_dir = os.path.join(config.CURRENT_PATH, config.RESULTS_PATH, str(i['building_id']))
	# Define the path to the json file "out.osw"
	out_osw_path = os.path.join(building_dir, 'out.osw')
	# Read the out.osw file
	with open(out_osw_path, 'r') as f:
		out_osw = json.load(f)
	# Get the status of the simulation
	i['status'] = out_osw.get('completed_status', None)
	# Get the failed step if any
	i['last_step'] = out_osw['steps'][out_osw['current_step']-1].get('measure_dir_name', None)
	i['failure_message'] = out_osw['steps'][out_osw['current_step']-1]['result'].get('step_errors', None)
	if i['status'] == 'Success':
		# Collect all columns names
		columns_to_be_str = list(i.keys())
		# Add the annual results
		results_annual_path = os.path.join(building_dir, 'run', 'results_annual.csv')
		df_annual_results = pd.read_csv(results_annual_path,header=None)
		dict_annual_results = df_annual_results.set_index(0).T.to_dict('records')[0]
		i.update(dict_annual_results)
		# Convert the dictionary to a pandas DataFrame and save it as a parquet file
		dfMetadata = pd.DataFrame([i])
		dfMetadata[columns_to_be_str] = dfMetadata[columns_to_be_str].astype(str)
		tableMetadata = pa.Table.from_pandas(dfMetadata)
		pq.write_to_dataset(tableMetadata, 
							root_path=os.path.join(results_dir, 'metadata.parquet'), 
							partition_cols=['building_id'],
							existing_data_behavior='delete_matching') 
		# Add the timeseries results
		dfTimeseries = pd.read_csv(os.path.join(building_dir, 'run', 'results_timeseries.csv'),
								header=[0,1])
		dfTimeseries.columns = ['_'.join([str(i) for i in col if str(i) != 'nan']) \
								for col in dfTimeseries.columns.values]
		dfTimeseries['building_id'] = i['building_id']
		tableTimeseries = pa.Table.from_pandas(dfTimeseries)
		pq.write_to_dataset(tableTimeseries, 
							root_path=os.path.join(results_dir, 'timeseries.parquet'), 
							partition_cols=['building_id'],
							existing_data_behavior='delete_matching')
	else:
		# If the simulation failed, just save the dict i into a json file
		dfErrors = pd.DataFrame([i])
		tableErrors = pa.Table.from_pandas(dfErrors)
		pq.write_to_dataset(tableErrors, 
							root_path=os.path.join(results_dir, 'errors.parquet'), 
							partition_cols=['building_id'],
							existing_data_behavior='delete_matching')

	return