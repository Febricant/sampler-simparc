# Import necessary libraries
import pandas as pd

# Import local libraries
import config

# Function to apply filters to the DataFrame based on the upgrade settings
def apply_filters(df: pd.DataFrame, filters: list):
    """
    Apply filters to the DataFrame based on the provided conditions.
    Args:
        df (DataFrame): The DataFrame to filter.
        filters (list): A list of filter conditions, where each condition is a tuple
                        (column_name, operator, value).

    Returns:
        DataFrame: The filtered DataFrame.
    
    """
    for col, op, val in filters:
        if op == "==":
            df = df[df[col] == val]
        elif op == "!=":
            df = df[df[col] != val]
        elif op == ">":
            df = df[df[col] > val]
        elif op == "<":
            df = df[df[col] < val]
        elif op == ">=":
            df = df[df[col] >= val]
        elif op == "<=":
            df = df[df[col] <= val]
        
    return df

# Function to modify wall insulation
def wall_insulation(df: pd.DataFrame, improvement_rate: float):
	"""
	Apply the new wall insulation value based on the improvement rate.

	Args:
		df (DataFrame): The DataFrame containing building data.
		improvement_rate (float): The percentage improvement rate (fraction).

	Returns:
		df (DataFrame): The DataFrame with updated wall insulation values.

	"""
	df['wall_assembly_r'] = df['wall_assembly_r'] * (1 + improvement_rate)
	
	return df

def window_properties(df: pd.DataFrame, improvement_rate_uvalue: float, improvement_rate_shgc: float):
	"""
	Apply the new window properties based on the improvement rates.

	Args:
		df (DataFrame): The DataFrame containing building data.
		improvement_rate_uvalue (float): The percentage improvement rate for U-value (fraction).
		improvement_rate_shgc (float): The percentage improvement rate for SHGC (fraction).

	Returns:
		df (DataFrame): The DataFrame with updated window properties.
		
	"""
	df['window_ufactor'] = df['window_ufactor'] * (1 - improvement_rate_uvalue)
	df['window_shgc'] = df['window_shgc'] * (1 + improvement_rate_shgc)

	return df

def air_leakage(df: pd.DataFrame, improvement_rate: float):
	"""
	Apply the new air leakage value based on the improvement rate.

	Args:
		df (DataFrame): The DataFrame containing building data.
		improvement_rate (float): The percentage improvement rate (0-100).

	Returns:
		df (DataFrame): The DataFrame with updated air leakage values.
		
	"""
	df['air_leakage_value'] = df['air_leakage_value'] * (1 - improvement_rate)

	return df

# Function to apply upgrades to the building data
def apply_upgrades(building_data):
	"""
	Apply upgrades to the building data based on the configuration constraints.
	
	Args:
		building_data (dataframe): The building data to which upgrades will be applied.
	
	Returns:
		building_data (dataframe): The updated building data with applied upgrades.
	"""
	# Check if upgrade settings are defined
	if config.UPGRADE_SETTINGS is None:
		return None
	
	# Iterate through each set of upgrades defined in the configuration
	i = 0
	building_data_init = building_data.copy()
	building_data_upgrades = pd.DataFrame()
	for set_of_measures in config.UPGRADE_SETTINGS.keys():
		i += 1
        # Apply filters to select the targeted buildings for the upgrades
		filters = config.UPGRADE_SETTINGS[set_of_measures]["Filters"]
		i_building_data = apply_filters(building_data_init, filters)
        # Apply the adoption rate to select buildings for upgrades
		adoption_rate = config.UPGRADE_SETTINGS[set_of_measures]["Adoption rate"]
		i_building_data = i_building_data.sample(frac=adoption_rate, replace=False, axis=0)
        # Define a new building_id in the dataframe
		i_building_data['building_id'] = i_building_data['building_id'].astype(str)+"_SetOfMeasures"+str(i)
		for measure in config.UPGRADE_SETTINGS[set_of_measures]["Upgrades"].keys():
			if measure == "Wall insulation":
				improvement_rate = config.UPGRADE_SETTINGS[set_of_measures]["Upgrades"][measure]["improvement_rate"]
				i_building_data = wall_insulation(i_building_data, improvement_rate)
			elif measure == "Window properties":
				improvement_rate_uvalue = config.UPGRADE_SETTINGS[set_of_measures]["Upgrades"][measure]["improvement_rate_uvalue"]
				improvement_rate_shgc = config.UPGRADE_SETTINGS[set_of_measures]["Upgrades"][measure]["improvement_rate_shgc"]
				i_building_data = window_properties(i_building_data, improvement_rate_uvalue, improvement_rate_shgc)
			elif measure == "Air leakage":
				improvement_rate = config.UPGRADE_SETTINGS[set_of_measures]["Upgrades"][measure]["improvement_rate"]
				i_building_data = air_leakage(i_building_data, improvement_rate)
		# Concatenate the modified building data with the original data
		building_data_upgrades = pd.concat([building_data_upgrades, i_building_data], ignore_index=True)
    
	return building_data_upgrades