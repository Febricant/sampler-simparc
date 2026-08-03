# Import necessary libraries
import argparse
import contextlib
import os, sys
from pathlib import Path

import pandas as pd

# Import local libraries
import config	# configuration file for paths and constants
import osrunner	# decides how OpenStudio is invoked (docker or a native binary)
import validation	# refuses a CSV OpenStudio would reject
from preprocessing import preprocess_data_types, preprocess_data_to_dict	# function to preprocess the data
from upgrading import apply_upgrades	# function to apply upgrades to the building data
from parallelization import batch_building_simulation, prepare_building	# run simulations (using the Building class)
from postprocessing import postprocess_results	# function to post-process the results


@contextlib.contextmanager
def performance_report_or_nothing(filename):
	"""dask's performance_report, but never able to lose a finished run.

	The report is rendered by bokeh when the context exits, so a missing or
	broken bokeh raises *after* every simulation has completed -- discarding the
	batch and the post-processing that should have followed it. The report is a
	diagnostic; the run is the result.
	"""
	from dask.distributed import performance_report

	reporter = performance_report(filename=filename)
	try:
		reporter.__enter__()
	except Exception as exc:	# pragma: no cover - report set-up only
		print(f"   (no {filename}: {exc})")
		yield
		return

	try:
		yield
	except BaseException:
		# A real failure in the body must propagate untouched.
		with contextlib.suppress(Exception):
			reporter.__exit__(*sys.exc_info())
		raise
	else:
		try:
			reporter.__exit__(None, None, None)
		except Exception as exc:
			print(f"   (could not write {filename}: {exc}. "
				  f"pip install bokeh to enable it.)")


def parse_arguments(argv=None):
	parser = argparse.ArgumentParser(
		description="Run SimParc over a building sample CSV.")
	parser.add_argument("csv", help="building sample input .csv file path")
	parser.add_argument("--repair", action="store_true",
						help="fix problems the validation finds instead of refusing to run; "
							 "writes the corrected CSV next to the input")
	parser.add_argument("--dry-run", action="store_true",
						help="write every building's in.osw and stop, without running "
							 "OpenStudio. Needs neither Docker nor dask.")
	parser.add_argument("--limit", type=int, metavar="N",
						help="only process the first N buildings")
	parser.add_argument("--serial", action="store_true",
						help="run the simulations one at a time instead of through dask")
	return parser.parse_args(argv)


def load_input(path, repair):
	"""Read the CSV and refuse to go further if OpenStudio would reject it.

	Both failed runs of this sample reached OpenStudio with an apartment unit on
	a conditioned basement, a pairing BuildResidentialHPXML rejects. The check
	that catches it already existed; it just was not on the path anything took.
	"""
	data = pd.read_csv(path)

	if repair:
		data, changes = validation.repair(data)
		for change in changes:
			print("   repaired: %s" % change)

	safe = validation.report(path, data)
	succeeded, message = validation.preprocessing_succeeds(data)
	print("   %s" % message)
	if not succeeded:
		raise SystemExit("\nrefusing to simulate: preprocessing fails on this input.")
	if not safe:
		raise SystemExit(
			"\nrefusing to simulate: the findings above would fail inside OpenStudio.\n"
			"re-run with --repair to correct them, or regenerate the sample.")

	if repair:
		repaired_path = "%s-repaired.csv" % os.path.splitext(path)[0]
		data.to_csv(repaired_path, index=False)
		print("   wrote %s" % repaired_path)

	return data


if __name__ == "__main__":

	args = parse_arguments()

	# Check file exists and is a .csv
	path_object = Path(args.csv)
	if not path_object.is_file():
		raise FileNotFoundError("File not found.")
	elif path_object.suffix != ".csv":
		raise TypeError("invalid file")

	# Get the building properties from a CSV file, and stop here if they cannot be simulated
	data = load_input(args.csv, args.repair)

	if args.limit:
		data = data.head(args.limit)
		print(f"   limited to the first {len(data)} building(s)")

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

	# Write every in.osw without running anything, so the inputs OpenStudio would
	# be given can be inspected in seconds rather than after a batch of failures.
	if args.dry_run:
		for building_data in data_dict:
			prepare_building(building_data)
		print(f"Dry run: wrote {len(data_dict)} in.osw file(s) under {results_dir}. "
			  "No simulations were run.")
		sys.exit(0)

	# Fail now, with an explanation, rather than 80 times inside the workers
	print(f"OpenStudio runner: {osrunner.resolve()}")

	if args.serial:
		print(f"Running {len(data_dict)} baseline simulations serially...")
		for building_data in data_dict:
			batch_building_simulation(building_data)
		if data_upgrades_dict is not None:
			print(f"Running {len(data_upgrades_dict)} upgrade simulations serially...")
			for building_data in data_upgrades_dict:
				batch_building_simulation(building_data)
		print("Simulations completed.")
	else:
		# dask is imported here so --dry-run and the validation above work without it
		from dask.distributed import LocalCluster, Client, progress

		# Initialize Dask cluster and client
		cluster = LocalCluster(n_workers=config.DASK_NUM_WORKERS)
		client = Client(cluster)

		with performance_report_or_nothing("dask-report-baseline.html"):
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
			with performance_report_or_nothing("dask-report-upgrades.html"):
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

	if args.serial:
		print(f"Running post-processing for {len(data_all_dict)} simulation results...")
		for building_data in data_all_dict:
			postprocess_results(building_data)
		print("Postprocessing completed.")
	else:
		from dask.distributed import LocalCluster, Client, progress

		# Initialize Dask cluster and client for post-processing
		cluster = LocalCluster(n_workers=config.DASK_NUM_WORKERS_POSTPROCESSING)
		client = Client(cluster)

		with performance_report_or_nothing("dask-report-postprocessing.html"):
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
