class HPXMLArguments:
    arguments = {
        "hpxml_path" : {
            "Name": "hpxml_path",
            "Display Name": "HPXML File Path",
            "Description": "Absolute/relative path of the HPXML file.",
            "Type": "String",
            "Required": "true"
        },
        "existing_hpxml_path" : {
            "Name": "existing_hpxml_path",
            "Display Name": "Existing HPXML File Path",
            "Description": "Absolute/relative path of the existing HPXML file. If not provided, a new HPXML file with one Building element is created. If provided, a new Building element will be appended to this HPXML file (e.g., to create a multifamily HPXML file describing multiple dwelling units).",
            "Type": "String",
            "Required": "false"
        },
        "whole_sfa_or_mf_building_sim" : {
            "Name": "whole_sfa_or_mf_building_sim",
            "Display Name": "Whole SFA/MF Building Simulation?",
            "Description": "If the HPXML file represents a single family-attached/multifamily building with multiple dwelling units defined, specifies whether to run the HPXML file as a single whole building model.",
            "Type": "Boolean",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "software_info_program_used" : {
            "Name": "software_info_program_used",
            "Display Name": "Software Info: Program Used",
            "Description": "The name of the software program used.",
            "Type": "String",
            "Required": "false"
        },
        "software_info_program_version" : {
            "Name": "software_info_program_version",
            "Display Name": "Software Info: Program Version",
            "Description": "The version of the software program used.",
            "Type": "String",
            "Required": "false"
        },
        "schedules_filepaths" : {
            "Name": "schedules_filepaths",
            "Display Name": "Schedules: CSV File Paths",
            "Description": "Absolute/relative paths of csv files containing user-specified detailed schedules. If multiple files, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "schedules_unavailable_period_types" : {
            "Name": "schedules_unavailable_period_types",
            "Display Name": "Schedules: Unavailable Period Types",
            "Description": "Specifies the unavailable period types. Possible types are column names defined in unavailable_periods.csv: Vacancy, Power Outage, No Space Heating, No Space Cooling. If multiple periods, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "schedules_unavailable_period_dates" : {
            "Name": "schedules_unavailable_period_dates",
            "Display Name": "Schedules: Unavailable Period Dates",
            "Description": "Specifies the unavailable period date ranges. Enter a date range like \"Dec 15 - Jan 15\". Optionally, can enter hour of the day like \"Dec 15 2 - Jan 15 20\" (start hour can be 0 through 23 and end hour can be 1 through 24). If multiple periods, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "schedules_unavailable_period_window_natvent_availabilities" : {
            "Name": "schedules_unavailable_period_window_natvent_availabilities",
            "Display Name": "Schedules: Unavailable Period Window Natural Ventilation Availabilities",
            "Description": "The availability of the natural ventilation schedule during unavailable periods. Valid choices are: regular schedule, always available, always unavailable. If multiple periods, use a comma-separated list. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-unavailable-periods'>HPXML Unavailable Periods</a>) is used.",
            "Type": "String",
            "Required": "false"
        },
        "simulation_control_timestep" : {
            "Name": "simulation_control_timestep",
            "Display Name": "Simulation Control: Timestep",
            "Description": "Value must be a divisor of 60. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-simulation-control'>HPXML Simulation Control</a>) is used.",
            "Type": "Integer",
            "Units": "min",
            "Required": "false"
        },
        "simulation_control_run_period" : {
            "Name": "simulation_control_run_period",
            "Display Name": "Simulation Control: Run Period",
            "Description": "Enter a date range like 'Jan 1 - Dec 31'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-simulation-control'>HPXML Simulation Control</a>) is used.",
            "Type": "String",
            "Required": "false"
        },
        "simulation_control_run_period_calendar_year" : {
            "Name": "simulation_control_run_period_calendar_year",
            "Display Name": "Simulation Control: Run Period Calendar Year",
            "Description": "This numeric field should contain the calendar year that determines the start day of week. If you are running simulations using AMY weather files, the value entered for calendar year will not be used; it will be overridden by the actual year found in the AMY weather file. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-simulation-control'>HPXML Simulation Control</a>) is used.",
            "Type": "Integer",
            "Units": "year",
            "Required": "false"
        },
        "simulation_control_daylight_saving_enabled" : {
            "Name": "simulation_control_daylight_saving_enabled",
            "Display Name": "Simulation Control: Daylight Saving Enabled",
            "Description": "Whether to use daylight saving. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-building-site'>HPXML Building Site</a>) is used.",
            "Type": "Boolean",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "simulation_control_daylight_saving_period" : {
            "Name": "simulation_control_daylight_saving_period",
            "Display Name": "Simulation Control: Daylight Saving Period",
            "Description": "Enter a date range like 'Mar 15 - Dec 15'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-building-site'>HPXML Building Site</a>) is used.",
            "Type": "String",
            "Required": "false"
        },
        "simulation_control_temperature_capacitance_multiplier" : {
            "Name": "simulation_control_temperature_capacitance_multiplier",
            "Display Name": "Simulation Control: Temperature Capacitance Multiplier",
            "Description": "Affects the transient calculation of indoor air temperatures. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-simulation-control'>HPXML Simulation Control</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "simulation_control_defrost_model_type" : {
            "Name": "simulation_control_defrost_model_type",
            "Display Name": "Simulation Control: Defrost Model Type",
            "Description": "Research feature to select the type of defrost model. Use standard for default E+ defrost setting. Use advanced for an improved model that better accounts for load and energy use during defrost; using advanced may impact simulation runtime. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-simulation-control'>HPXML Simulation Control</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "standard",
                "advanced"
            ],
            "Required": "false"
        },
        "simulation_control_ground_to_air_heat_pump_model_type" : {
            "Name": "simulation_control_ground_to_air_heat_pump_model_type",
            "Display Name": "Simulation Control: Ground-to-Air Heat Pump Model Type",
            "Description": "Research feature to select the type of ground-to-air heat pump model. Use standard for standard ground-to-air heat pump modeling. Use experimental for an improved model that better accounts for coil staging. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-simulation-control'>HPXML Simulation Control</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "standard",
                "experimental"
            ],
            "Required": "false"
        },
        "simulation_control_onoff_thermostat_deadband" : {
            "Name": "simulation_control_onoff_thermostat_deadband",
            "Display Name": "Simulation Control: HVAC On-Off Thermostat Deadband",
            "Description": "Research feature to model on-off thermostat deadband and start-up degradation for single or two speed AC/ASHP systems, and realistic time-based staging for two speed AC/ASHP systems. Currently only supported with 1 min timestep.",
            "Type": "Double",
            "Units": "deg-F",
            "Required": "false"
        },
        "simulation_control_heat_pump_backup_heating_capacity_increment" : {
            "Name": "simulation_control_heat_pump_backup_heating_capacity_increment",
            "Display Name": "Simulation Control: Heat Pump Backup Heating Capacity Increment",
            "Description": "Research feature to model capacity increment of multi-stage heat pump backup systems with time-based staging. Only applies to air-source heat pumps where Backup Type is 'integrated' and Backup Fuel Type is 'electricity'. Currently only supported with 1 min timestep.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "site_type" : {
            "Name": "site_type",
            "Display Name": "Site: Type",
            "Description": "The type of site. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "suburban",
                "urban",
                "rural"
            ],
            "Required": "false"
        },
        "site_shielding_of_home" : {
            "Name": "site_shielding_of_home",
            "Display Name": "Site: Shielding of Home",
            "Description": "Presence of nearby buildings, trees, obstructions for infiltration model. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "exposed",
                "normal",
                "well-shielded"
            ],
            "Required": "false"
        },
        "site_soil_and_moisture_type" : {
            "Name": "site_soil_and_moisture_type",
            "Display Name": "Site: Soil and Moisture Type",
            "Description": "Type of soil and moisture. This is used to inform ground conductivity and diffusivity. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "clay, dry",
                "clay, mixed",
                "clay, wet",
                "gravel, dry",
                "gravel, mixed",
                "gravel, wet",
                "loam, dry",
                "loam, mixed",
                "loam, wet",
                "sand, dry",
                "sand, mixed",
                "sand, wet",
                "silt, dry",
                "silt, mixed",
                "silt, wet",
                "unknown, dry",
                "unknown, mixed",
                "unknown, wet"
            ],
            "Required": "false"
        },
        "site_ground_conductivity" : {
            "Name": "site_ground_conductivity",
            "Display Name": "Site: Ground Conductivity",
            "Description": "Conductivity of the ground soil. If provided, overrides the previous site and moisture type input.",
            "Type": "Double",
            "Units": "Btu/hr-ft-F",
            "Required": "false"
        },
        "site_ground_diffusivity" : {
            "Name": "site_ground_diffusivity",
            "Display Name": "Site: Ground Diffusivity",
            "Description": "Diffusivity of the ground soil. If provided, overrides the previous site and moisture type input.",
            "Type": "Double",
            "Units": "ft^2/hr",
            "Required": "false"
        },
        "site_iecc_zone" : {
            "Name": "site_iecc_zone",
            "Display Name": "Site: IECC Zone",
            "Description": "IECC zone of the home address.",
            "Type": "Choice",
            "Choices": [
                "1A",
                "1B",
                "1C",
                "2A",
                "2B",
                "2C",
                "3A",
                "3B",
                "3C",
                "4A",
                "4B",
                "4C",
                "5A",
                "5B",
                "5C",
                "6A",
                "6B",
                "6C",
                "7",
                "8"
            ],
            "Required": "false"
        },
        "site_city" : {
            "Name": "site_city",
            "Display Name": "Site: City",
            "Description": "City/municipality of the home address.",
            "Type": "String",
            "Required": "false"
        },
        "site_state_code" : {
            "Name": "site_state_code",
            "Display Name": "Site: State Code",
            "Description": "State code of the home address. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "AK",
                "AL",
                "AR",
                "AZ",
                "CA",
                "CO",
                "CT",
                "DC",
                "DE",
                "FL",
                "GA",
                "HI",
                "IA",
                "ID",
                "IL",
                "IN",
                "KS",
                "KY",
                "LA",
                "MA",
                "MD",
                "ME",
                "MI",
                "MN",
                "MO",
                "MS",
                "MT",
                "NC",
                "ND",
                "NE",
                "NH",
                "NJ",
                "NM",
                "NV",
                "NY",
                "OH",
                "OK",
                "OR",
                "PA",
                "RI",
                "SC",
                "SD",
                "TN",
                "TX",
                "UT",
                "VA",
                "VT",
                "WA",
                "WI",
                "WV",
                "WY"
            ],
            "Required": "false"
        },
        "site_zip_code" : {
            "Name": "site_zip_code",
            "Display Name": "Site: Zip Code",
            "Description": "Zip code of the home address. Either this or the Weather Station: EnergyPlus Weather (EPW) Filepath input below must be provided.",
            "Type": "String",
            "Required": "false"
        },
        "site_time_zone_utc_offset" : {
            "Name": "site_time_zone_utc_offset",
            "Display Name": "Site: Time Zone UTC Offset",
            "Description": "Time zone UTC offset of the home address. Must be between -12 and 14. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Double",
            "Units": "hr",
            "Required": "false"
        },
        "site_elevation" : {
            "Name": "site_elevation",
            "Display Name": "Site: Elevation",
            "Description": "Elevation of the home address. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "site_latitude" : {
            "Name": "site_latitude",
            "Display Name": "Site: Latitude",
            "Description": "Latitude of the home address. Must be between -90 and 90. Use negative values for southern hemisphere. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Double",
            "Units": "deg",
            "Required": "false"
        },
        "site_longitude" : {
            "Name": "site_longitude",
            "Display Name": "Site: Longitude",
            "Description": "Longitude of the home address. Must be between -180 and 180. Use negative values for the western hemisphere. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Double",
            "Units": "deg",
            "Required": "false"
        },
        "weather_station_epw_filepath" : {
            "Name": "weather_station_epw_filepath",
            "Display Name": "Weather Station: EnergyPlus Weather (EPW) Filepath",
            "Description": "Path of the EPW file. Either this or the Site: Zip Code input above must be provided.",
            "Type": "String",
            "Required": "false"
        },
        "year_built" : {
            "Name": "year_built",
            "Display Name": "Building Construction: Year Built",
            "Description": "The year the building was built.",
            "Type": "Integer",
            "Required": "false"
        },
        "unit_multiplier" : {
            "Name": "unit_multiplier",
            "Display Name": "Building Construction: Unit Multiplier",
            "Description": "The number of similar dwelling units. EnergyPlus simulation results will be multiplied this value. If not provided, defaults to 1.",
            "Type": "Integer",
            "Required": "false"
        },
        "geometry_unit_type" : {
            "Name": "geometry_unit_type",
            "Display Name": "Geometry: Unit Type",
            "Description": "The type of dwelling unit. Use single-family attached for a dwelling unit with 1 or more stories, attached units to one or both sides, and no units above/below. Use apartment unit for a dwelling unit with 1 story, attached units to one, two, or three sides, and units above and/or below.",
            "Type": "Choice",
            "Default Value": "single-family detached",
            "Choices": [
                "single-family detached",
                "single-family attached",
                "apartment unit",
                "manufactured home"
            ],
            "Required": "true"
        },
        "geometry_unit_left_wall_is_adiabatic" : {
            "Name": "geometry_unit_left_wall_is_adiabatic",
            "Display Name": "Geometry: Unit Left Wall Is Adiabatic",
            "Description": "Presence of an adiabatic left wall.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "geometry_unit_right_wall_is_adiabatic" : {
            "Name": "geometry_unit_right_wall_is_adiabatic",
            "Display Name": "Geometry: Unit Right Wall Is Adiabatic",
            "Description": "Presence of an adiabatic right wall.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "geometry_unit_front_wall_is_adiabatic" : {
            "Name": "geometry_unit_front_wall_is_adiabatic",
            "Display Name": "Geometry: Unit Front Wall Is Adiabatic",
            "Description": "Presence of an adiabatic front wall, for example, the unit is adjacent to a conditioned corridor.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "geometry_unit_back_wall_is_adiabatic" : {
            "Name": "geometry_unit_back_wall_is_adiabatic",
            "Display Name": "Geometry: Unit Back Wall Is Adiabatic",
            "Description": "Presence of an adiabatic back wall.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "geometry_unit_num_floors_above_grade" : {
            "Name": "geometry_unit_num_floors_above_grade",
            "Display Name": "Geometry: Unit Number of Floors Above Grade",
            "Description": "The number of floors above grade in the unit. Attic type ConditionedAttic is included. Assumed to be 1 for apartment units.",
            "Type": "Integer",
            "Units": "#",
            "Default Value": "2",
            "Required": "true"
        },
        "geometry_unit_cfa" : {
            "Name": "geometry_unit_cfa",
            "Display Name": "Geometry: Unit Conditioned Floor Area",
            "Description": "The total floor area of the unit's conditioned space (including any conditioned basement floor area).",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "2000",
            "Required": "true"
        },
        "geometry_unit_aspect_ratio" : {
            "Name": "geometry_unit_aspect_ratio",
            "Display Name": "Geometry: Unit Aspect Ratio",
            "Description": "The ratio of front/back wall length to left/right wall length for the unit, excluding any protruding garage wall area.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "2",
            "Required": "true"
        },
        "geometry_unit_orientation" : {
            "Name": "geometry_unit_orientation",
            "Display Name": "Geometry: Unit Orientation",
            "Description": "The unit's orientation is measured clockwise from north (e.g., North=0, East=90, South=180, West=270).",
            "Type": "Double",
            "Units": "degrees",
            "Default Value": "180",
            "Required": "true"
        },
        "geometry_unit_num_bedrooms" : {
            "Name": "geometry_unit_num_bedrooms",
            "Display Name": "Geometry: Unit Number of Bedrooms",
            "Description": "The number of bedrooms in the unit.",
            "Type": "Integer",
            "Units": "#",
            "Default Value": "3",
            "Required": "true"
        },
        "geometry_unit_num_bathrooms" : {
            "Name": "geometry_unit_num_bathrooms",
            "Display Name": "Geometry: Unit Number of Bathrooms",
            "Description": "The number of bathrooms in the unit. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-building-construction'>HPXML Building Construction</a>) is used.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "geometry_unit_num_occupants" : {
            "Name": "geometry_unit_num_occupants",
            "Display Name": "Geometry: Unit Number of Occupants",
            "Description": "The number of occupants in the unit. If not provided, an *asset* calculation is performed assuming standard occupancy, in which various end use defaults (e.g., plug loads, appliances, and hot water usage) are calculated based on Number of Bedrooms and Conditioned Floor Area per ANSI/RESNET/ICC 301. If provided, an *operational* calculation is instead performed in which the end use defaults to reflect real-world data (where possible).",
            "Type": "Double",
            "Units": "#",
            "Required": "false"
        },
        "geometry_building_num_units" : {
            "Name": "geometry_building_num_units",
            "Display Name": "Geometry: Building Number of Units",
            "Description": "The number of units in the building. Required for single-family attached and apartment units.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "geometry_average_ceiling_height" : {
            "Name": "geometry_average_ceiling_height",
            "Display Name": "Geometry: Average Ceiling Height",
            "Description": "Average distance from the floor to the ceiling.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "8",
            "Required": "true"
        },
        "geometry_unit_height_above_grade" : {
            "Name": "geometry_unit_height_above_grade",
            "Display Name": "Geometry: Unit Height Above Grade",
            "Description": "Describes the above-grade height of apartment units on upper floors or homes above ambient or belly-and-wing foundations. It is defined as the height of the lowest conditioned floor above grade and is used to calculate the wind speed for the infiltration model. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-building-construction'>HPXML Building Construction</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "geometry_garage_width" : {
            "Name": "geometry_garage_width",
            "Display Name": "Geometry: Garage Width",
            "Description": "The width of the garage. Enter zero for no garage. Only applies to single-family detached units.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "geometry_garage_depth" : {
            "Name": "geometry_garage_depth",
            "Display Name": "Geometry: Garage Depth",
            "Description": "The depth of the garage. Only applies to single-family detached units.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "20",
            "Required": "true"
        },
        "geometry_garage_protrusion" : {
            "Name": "geometry_garage_protrusion",
            "Display Name": "Geometry: Garage Protrusion",
            "Description": "The fraction of the garage that is protruding from the conditioned space. Only applies to single-family detached units.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0",
            "Required": "true"
        },
        "geometry_garage_position" : {
            "Name": "geometry_garage_position",
            "Display Name": "Geometry: Garage Position",
            "Description": "The position of the garage. Only applies to single-family detached units.",
            "Type": "Choice",
            "Default Value": "Right",
            "Choices": [
                "Right",
                "Left"
            ],
            "Required": "true"
        },
        "geometry_foundation_type" : {
            "Name": "geometry_foundation_type",
            "Display Name": "Geometry: Foundation Type",
            "Description": "The foundation type of the building. Foundation types ConditionedBasement and ConditionedCrawlspace are not allowed for apartment units.",
            "Type": "Choice",
            "Default Value": "SlabOnGrade",
            "Choices": [
                "SlabOnGrade",
                "VentedCrawlspace",
                "UnventedCrawlspace",
                "ConditionedCrawlspace",
                "UnconditionedBasement",
                "ConditionedBasement",
                "Ambient",
                "AboveApartment",
                "BellyAndWingWithSkirt",
                "BellyAndWingNoSkirt"
            ],
            "Required": "true"
        },
        "geometry_foundation_height" : {
            "Name": "geometry_foundation_height",
            "Display Name": "Geometry: Foundation Height",
            "Description": "The height of the foundation (e.g., 3ft for crawlspace, 8ft for basement). Only applies to basements/crawlspaces.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "geometry_foundation_height_above_grade" : {
            "Name": "geometry_foundation_height_above_grade",
            "Display Name": "Geometry: Foundation Height Above Grade",
            "Description": "The depth above grade of the foundation wall. Only applies to basements/crawlspaces.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "geometry_rim_joist_height" : {
            "Name": "geometry_rim_joist_height",
            "Display Name": "Geometry: Rim Joist Height",
            "Description": "The height of the rim joists. Only applies to basements/crawlspaces.",
            "Type": "Double",
            "Units": "in",
            "Required": "false"
        },
        "geometry_attic_type" : {
            "Name": "geometry_attic_type",
            "Display Name": "Geometry: Attic Type",
            "Description": "The attic type of the building. Attic type ConditionedAttic is not allowed for apartment units.",
            "Type": "Choice",
            "Default Value": "VentedAttic",
            "Choices": [
                "FlatRoof",
                "VentedAttic",
                "UnventedAttic",
                "ConditionedAttic",
                "BelowApartment"
            ],
            "Required": "true"
        },
        "geometry_roof_type" : {
            "Name": "geometry_roof_type",
            "Display Name": "Geometry: Roof Type",
            "Description": "The roof type of the building. Ignored if the building has a flat roof.",
            "Type": "Choice",
            "Default Value": "gable",
            "Choices": [
                "gable",
                "hip"
            ],
            "Required": "true"
        },
        "geometry_roof_pitch" : {
            "Name": "geometry_roof_pitch",
            "Display Name": "Geometry: Roof Pitch",
            "Description": "The roof pitch of the attic. Ignored if the building has a flat roof.",
            "Type": "Choice",
            "Default Value": "6:12",
            "Choices": [
                "1:12",
                "2:12",
                "3:12",
                "4:12",
                "5:12",
                "6:12",
                "7:12",
                "8:12",
                "9:12",
                "10:12",
                "11:12",
                "12:12"
            ],
            "Required": "true"
        },
        "geometry_eaves_depth" : {
            "Name": "geometry_eaves_depth",
            "Display Name": "Geometry: Eaves Depth",
            "Description": "The eaves depth of the roof.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "2",
            "Required": "true"
        },
        "neighbor_front_distance" : {
            "Name": "neighbor_front_distance",
            "Display Name": "Neighbor: Front Distance",
            "Description": "The distance between the unit and the neighboring building to the front (not including eaves). A value of zero indicates no neighbors. Used for shading.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "neighbor_back_distance" : {
            "Name": "neighbor_back_distance",
            "Display Name": "Neighbor: Back Distance",
            "Description": "The distance between the unit and the neighboring building to the back (not including eaves). A value of zero indicates no neighbors. Used for shading.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "neighbor_left_distance" : {
            "Name": "neighbor_left_distance",
            "Display Name": "Neighbor: Left Distance",
            "Description": "The distance between the unit and the neighboring building to the left (not including eaves). A value of zero indicates no neighbors. Used for shading.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "10",
            "Required": "true"
        },
        "neighbor_right_distance" : {
            "Name": "neighbor_right_distance",
            "Display Name": "Neighbor: Right Distance",
            "Description": "The distance between the unit and the neighboring building to the right (not including eaves). A value of zero indicates no neighbors. Used for shading.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "10",
            "Required": "true"
        },
        "neighbor_front_height" : {
            "Name": "neighbor_front_height",
            "Display Name": "Neighbor: Front Height",
            "Description": "The height of the neighboring building to the front. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-neighbor-buildings'>HPXML Neighbor Building</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "neighbor_back_height" : {
            "Name": "neighbor_back_height",
            "Display Name": "Neighbor: Back Height",
            "Description": "The height of the neighboring building to the back. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-neighbor-buildings'>HPXML Neighbor Building</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "neighbor_left_height" : {
            "Name": "neighbor_left_height",
            "Display Name": "Neighbor: Left Height",
            "Description": "The height of the neighboring building to the left. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-neighbor-buildings'>HPXML Neighbor Building</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "neighbor_right_height" : {
            "Name": "neighbor_right_height",
            "Display Name": "Neighbor: Right Height",
            "Description": "The height of the neighboring building to the right. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-neighbor-buildings'>HPXML Neighbor Building</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "floor_over_foundation_assembly_r" : {
            "Name": "floor_over_foundation_assembly_r",
            "Display Name": "Floor: Over Foundation Assembly R-value",
            "Description": "Assembly R-value for the floor over the foundation. Ignored if the building has a slab-on-grade foundation.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "28.1",
            "Required": "true"
        },
        "floor_over_garage_assembly_r" : {
            "Name": "floor_over_garage_assembly_r",
            "Display Name": "Floor: Over Garage Assembly R-value",
            "Description": "Assembly R-value for the floor over the garage. Ignored unless the building has a garage under conditioned space.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "28.1",
            "Required": "true"
        },
        "floor_type" : {
            "Name": "floor_type",
            "Display Name": "Floor: Type",
            "Description": "The type of floors.",
            "Type": "Choice",
            "Default Value": "WoodFrame",
            "Choices": [
                "WoodFrame",
                "StructuralInsulatedPanel",
                "SolidConcrete",
                "SteelFrame"
            ],
            "Required": "true"
        },
        "foundation_wall_type" : {
            "Name": "foundation_wall_type",
            "Display Name": "Foundation Wall: Type",
            "Description": "The material type of the foundation wall. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-foundation-walls'>HPXML Foundation Walls</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "solid concrete",
                "concrete block",
                "concrete block foam core",
                "concrete block perlite core",
                "concrete block vermiculite core",
                "concrete block solid core",
                "double brick",
                "wood"
            ],
            "Required": "false"
        },
        "foundation_wall_thickness" : {
            "Name": "foundation_wall_thickness",
            "Display Name": "Foundation Wall: Thickness",
            "Description": "The thickness of the foundation wall. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-foundation-walls'>HPXML Foundation Walls</a>) is used.",
            "Type": "Double",
            "Units": "in",
            "Required": "false"
        },
        "foundation_wall_insulation_r" : {
            "Name": "foundation_wall_insulation_r",
            "Display Name": "Foundation Wall: Insulation Nominal R-value",
            "Description": "Nominal R-value for the foundation wall insulation. Only applies to basements/crawlspaces.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "foundation_wall_insulation_location" : {
            "Name": "foundation_wall_insulation_location",
            "Display Name": "Foundation Wall: Insulation Location",
            "Description": "Whether the insulation is on the interior or exterior of the foundation wall. Only applies to basements/crawlspaces.",
            "Type": "Choice",
            "Units": "ft",
            "Default Value": "exterior",
            "Choices": [
                "interior",
                "exterior"
            ],
            "Required": "false"
        },
        "foundation_wall_insulation_distance_to_top" : {
            "Name": "foundation_wall_insulation_distance_to_top",
            "Display Name": "Foundation Wall: Insulation Distance To Top",
            "Description": "The distance from the top of the foundation wall to the top of the foundation wall insulation. Only applies to basements/crawlspaces. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-foundation-walls'>HPXML Foundation Walls</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "foundation_wall_insulation_distance_to_bottom" : {
            "Name": "foundation_wall_insulation_distance_to_bottom",
            "Display Name": "Foundation Wall: Insulation Distance To Bottom",
            "Description": "The distance from the top of the foundation wall to the bottom of the foundation wall insulation. Only applies to basements/crawlspaces. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-foundation-walls'>HPXML Foundation Walls</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "foundation_wall_assembly_r" : {
            "Name": "foundation_wall_assembly_r",
            "Display Name": "Foundation Wall: Assembly R-value",
            "Description": "Assembly R-value for the foundation walls. Only applies to basements/crawlspaces. If provided, overrides the previous foundation wall insulation inputs. If not provided, it is ignored.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "rim_joist_assembly_r" : {
            "Name": "rim_joist_assembly_r",
            "Display Name": "Rim Joist: Assembly R-value",
            "Description": "Assembly R-value for the rim joists. Only applies to basements/crawlspaces. Required if a rim joist height is provided.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "slab_perimeter_insulation_r" : {
            "Name": "slab_perimeter_insulation_r",
            "Display Name": "Slab: Perimeter Insulation Nominal R-value",
            "Description": "Nominal R-value of the vertical slab perimeter insulation. Applies to slab-on-grade foundations and basement/crawlspace floors.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "slab_perimeter_insulation_depth" : {
            "Name": "slab_perimeter_insulation_depth",
            "Display Name": "Slab: Perimeter Insulation Depth",
            "Description": "Depth from grade to bottom of vertical slab perimeter insulation. Applies to slab-on-grade foundations and basement/crawlspace floors.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "slab_exterior_horizontal_insulation_r" : {
            "Name": "slab_exterior_horizontal_insulation_r",
            "Display Name": "Slab: Exterior Horizontal Insulation Nominal R-value",
            "Description": "Nominal R-value of the slab exterior horizontal insulation. Applies to slab-on-grade foundations and basement/crawlspace floors.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "slab_exterior_horizontal_insulation_width" : {
            "Name": "slab_exterior_horizontal_insulation_width",
            "Display Name": "Slab: Exterior Horizontal Insulation Width",
            "Description": "Width of the slab exterior horizontal insulation measured from the exterior surface of the vertical slab perimeter insulation. Applies to slab-on-grade foundations and basement/crawlspace floors.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "slab_exterior_horizontal_insulation_depth_below_grade" : {
            "Name": "slab_exterior_horizontal_insulation_depth_below_grade",
            "Display Name": "Slab: Exterior Horizontal Insulation Depth Below Grade",
            "Description": "Depth of the slab exterior horizontal insulation measured from the top surface of the slab exterior horizontal insulation. Applies to slab-on-grade foundations and basement/crawlspace floors.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "slab_under_insulation_r" : {
            "Name": "slab_under_insulation_r",
            "Display Name": "Slab: Under Slab Insulation Nominal R-value",
            "Description": "Nominal R-value of the horizontal under slab insulation. Applies to slab-on-grade foundations and basement/crawlspace floors.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "slab_under_insulation_width" : {
            "Name": "slab_under_insulation_width",
            "Display Name": "Slab: Under Slab Insulation Width",
            "Description": "Width from slab edge inward of horizontal under-slab insulation. Enter 999 to specify that the under slab insulation spans the entire slab. Applies to slab-on-grade foundations and basement/crawlspace floors.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "slab_thickness" : {
            "Name": "slab_thickness",
            "Display Name": "Slab: Thickness",
            "Description": "The thickness of the slab. Zero can be entered if there is a dirt floor instead of a slab. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-slabs'>HPXML Slabs</a>) is used.",
            "Type": "Double",
            "Units": "in",
            "Required": "false"
        },
        "slab_carpet_fraction" : {
            "Name": "slab_carpet_fraction",
            "Display Name": "Slab: Carpet Fraction",
            "Description": "Fraction of the slab floor area that is carpeted. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-slabs'>HPXML Slabs</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "slab_carpet_r" : {
            "Name": "slab_carpet_r",
            "Display Name": "Slab: Carpet R-value",
            "Description": "R-value of the slab carpet. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-slabs'>HPXML Slabs</a>) is used.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "ceiling_assembly_r" : {
            "Name": "ceiling_assembly_r",
            "Display Name": "Ceiling: Assembly R-value",
            "Description": "Assembly R-value for the ceiling (attic floor).",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "31.6",
            "Required": "true"
        },
        "roof_material_type" : {
            "Name": "roof_material_type",
            "Display Name": "Roof: Material Type",
            "Description": "The material type of the roof. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-roofs'>HPXML Roofs</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "asphalt or fiberglass shingles",
                "concrete",
                "cool roof",
                "slate or tile shingles",
                "expanded polystyrene sheathing",
                "metal surfacing",
                "plastic/rubber/synthetic sheeting",
                "shingles",
                "wood shingles or shakes"
            ],
            "Required": "false"
        },
        "roof_color" : {
            "Name": "roof_color",
            "Display Name": "Roof: Color",
            "Description": "The color of the roof. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-roofs'>HPXML Roofs</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "dark",
                "light",
                "medium",
                "medium dark",
                "reflective"
            ],
            "Required": "false"
        },
        "roof_assembly_r" : {
            "Name": "roof_assembly_r",
            "Display Name": "Roof: Assembly R-value",
            "Description": "Assembly R-value of the roof.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "2.3",
            "Required": "true"
        },
        "radiant_barrier_attic_location" : {
            "Name": "radiant_barrier_attic_location",
            "Display Name": "Attic: Radiant Barrier Location",
            "Description": "The location of the radiant barrier in the attic.",
            "Type": "Choice",
            "Choices": [
                "none",
                "Attic roof only",
                "Attic roof and gable walls",
                "Attic floor"
            ],
            "Required": "false"
        },
        "radiant_barrier_grade" : {
            "Name": "radiant_barrier_grade",
            "Display Name": "Attic: Radiant Barrier Grade",
            "Description": "The grade of the radiant barrier in the attic. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-roofs'>HPXML Roofs</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "1",
                "2",
                "3"
            ],
            "Required": "false"
        },
        "wall_type" : {
            "Name": "wall_type",
            "Display Name": "Wall: Type",
            "Description": "The type of walls.",
            "Type": "Choice",
            "Default Value": "WoodStud",
            "Choices": [
                "WoodStud",
                "ConcreteMasonryUnit",
                "DoubleWoodStud",
                "InsulatedConcreteForms",
                "LogWall",
                "StructuralInsulatedPanel",
                "SolidConcrete",
                "SteelFrame",
                "Stone",
                "StrawBale",
                "StructuralBrick"
            ],
            "Required": "true"
        },
        "wall_siding_type" : {
            "Name": "wall_siding_type",
            "Display Name": "Wall: Siding Type",
            "Description": "The siding type of the walls. Also applies to rim joists. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-walls'>HPXML Walls</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "aluminum siding",
                "asbestos siding",
                "brick veneer",
                "composite shingle siding",
                "fiber cement siding",
                "masonite siding",
                "none",
                "stucco",
                "synthetic stucco",
                "vinyl siding",
                "wood siding"
            ],
            "Required": "false"
        },
        "wall_color" : {
            "Name": "wall_color",
            "Display Name": "Wall: Color",
            "Description": "The color of the walls. Also applies to rim joists. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-walls'>HPXML Walls</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "dark",
                "light",
                "medium",
                "medium dark",
                "reflective"
            ],
            "Required": "false"
        },
        "wall_assembly_r" : {
            "Name": "wall_assembly_r",
            "Display Name": "Wall: Assembly R-value",
            "Description": "Assembly R-value of the walls.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "11.9",
            "Required": "true"
        },
        "window_front_wwr" : {
            "Name": "window_front_wwr",
            "Display Name": "Windows: Front Window-to-Wall Ratio",
            "Description": "The ratio of window area to wall area for the unit's front facade. Enter 0 if specifying Front Window Area instead. If the front wall is adiabatic, the value will be ignored.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.18",
            "Required": "true"
        },
        "window_back_wwr" : {
            "Name": "window_back_wwr",
            "Display Name": "Windows: Back Window-to-Wall Ratio",
            "Description": "The ratio of window area to wall area for the unit's back facade. Enter 0 if specifying Back Window Area instead. If the back wall is adiabatic, the value will be ignored.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.18",
            "Required": "true"
        },
        "window_left_wwr" : {
            "Name": "window_left_wwr",
            "Display Name": "Windows: Left Window-to-Wall Ratio",
            "Description": "The ratio of window area to wall area for the unit's left facade (when viewed from the front). Enter 0 if specifying Left Window Area instead. If the left wall is adiabatic, the value will be ignored.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.18",
            "Required": "true"
        },
        "window_right_wwr" : {
            "Name": "window_right_wwr",
            "Display Name": "Windows: Right Window-to-Wall Ratio",
            "Description": "The ratio of window area to wall area for the unit's right facade (when viewed from the front). Enter 0 if specifying Right Window Area instead. If the right wall is adiabatic, the value will be ignored.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.18",
            "Required": "true"
        },
        "window_area_front" : {
            "Name": "window_area_front",
            "Display Name": "Windows: Front Window Area",
            "Description": "The amount of window area on the unit's front facade. Enter 0 if specifying Front Window-to-Wall Ratio instead. If the front wall is adiabatic, the value will be ignored.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "window_area_back" : {
            "Name": "window_area_back",
            "Display Name": "Windows: Back Window Area",
            "Description": "The amount of window area on the unit's back facade. Enter 0 if specifying Back Window-to-Wall Ratio instead. If the back wall is adiabatic, the value will be ignored.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "window_area_left" : {
            "Name": "window_area_left",
            "Display Name": "Windows: Left Window Area",
            "Description": "The amount of window area on the unit's left facade (when viewed from the front). Enter 0 if specifying Left Window-to-Wall Ratio instead. If the left wall is adiabatic, the value will be ignored.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "window_area_right" : {
            "Name": "window_area_right",
            "Display Name": "Windows: Right Window Area",
            "Description": "The amount of window area on the unit's right facade (when viewed from the front). Enter 0 if specifying Right Window-to-Wall Ratio instead. If the right wall is adiabatic, the value will be ignored.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "window_aspect_ratio" : {
            "Name": "window_aspect_ratio",
            "Display Name": "Windows: Aspect Ratio",
            "Description": "Ratio of window height to width.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "1.333",
            "Required": "true"
        },
        "window_fraction_operable" : {
            "Name": "window_fraction_operable",
            "Display Name": "Windows: Fraction Operable",
            "Description": "Fraction of windows that are operable. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "window_natvent_availability" : {
            "Name": "window_natvent_availability",
            "Display Name": "Windows: Natural Ventilation Availability",
            "Description": "For operable windows, the number of days/week that windows can be opened by occupants for natural ventilation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "Integer",
            "Units": "Days/week",
            "Required": "false"
        },
        "window_ufactor" : {
            "Name": "window_ufactor",
            "Display Name": "Windows: U-Factor",
            "Description": "Full-assembly NFRC U-factor.",
            "Type": "Double",
            "Units": "Btu/hr-ft^2-R",
            "Default Value": "0.37",
            "Required": "true"
        },
        "window_shgc" : {
            "Name": "window_shgc",
            "Display Name": "Windows: SHGC",
            "Description": "Full-assembly NFRC solar heat gain coefficient.",
            "Type": "Double",
            "Default Value": "0.3",
            "Required": "true"
        },
        "window_interior_shading_type" : {
            "Name": "window_interior_shading_type",
            "Display Name": "Windows: Interior Shading Type",
            "Description": "Type of window interior shading. Summer/winter shading coefficients can be provided below instead. If neither is provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-interior-shading'>HPXML Interior Shading</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "light curtains",
                "light shades",
                "light blinds",
                "medium curtains",
                "medium shades",
                "medium blinds",
                "dark curtains",
                "dark shades",
                "dark blinds",
                "none"
            ],
            "Required": "false"
        },
        "window_interior_shading_winter" : {
            "Name": "window_interior_shading_winter",
            "Display Name": "Windows: Winter Interior Shading Coefficient",
            "Description": "Interior shading coefficient for the winter season, which if provided overrides the shading type input. 1.0 indicates no reduction in solar gain, 0.85 indicates 15% reduction, etc. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-interior-shading'>HPXML Interior Shading</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "window_interior_shading_summer" : {
            "Name": "window_interior_shading_summer",
            "Display Name": "Windows: Summer Interior Shading Coefficient",
            "Description": "Interior shading coefficient for the summer season, which if provided overrides the shading type input. 1.0 indicates no reduction in solar gain, 0.85 indicates 15% reduction, etc. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-interior-shading'>HPXML Interior Shading</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "window_exterior_shading_type" : {
            "Name": "window_exterior_shading_type",
            "Display Name": "Windows: Exterior Shading Type",
            "Description": "Type of window exterior shading. Summer/winter shading coefficients can be provided below instead. If neither is provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-exterior-shading'>HPXML Exterior Shading</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "solar film",
                "solar screens",
                "none"
            ],
            "Required": "false"
        },
        "window_exterior_shading_winter" : {
            "Name": "window_exterior_shading_winter",
            "Display Name": "Windows: Winter Exterior Shading Coefficient",
            "Description": "Exterior shading coefficient for the winter season, which if provided overrides the shading type input. 1.0 indicates no reduction in solar gain, 0.85 indicates 15% reduction, etc. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-exterior-shading'>HPXML Exterior Shading</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "window_exterior_shading_summer" : {
            "Name": "window_exterior_shading_summer",
            "Display Name": "Windows: Summer Exterior Shading Coefficient",
            "Description": "Exterior shading coefficient for the summer season, which if provided overrides the shading type input. 1.0 indicates no reduction in solar gain, 0.85 indicates 15% reduction, etc. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-exterior-shading'>HPXML Exterior Shading</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "window_shading_summer_season" : {
            "Name": "window_shading_summer_season",
            "Display Name": "Windows: Shading Summer Season",
            "Description": "Enter a date range like 'May 1 - Sep 30'. Defines the summer season for purposes of shading coefficients; the rest of the year is assumed to be winter. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "String",
            "Required": "false"
        },
        "window_insect_screens" : {
            "Name": "window_insect_screens",
            "Display Name": "Windows: Insect Screens",
            "Description": "The type of insect screens, if present. If not provided, assumes there are no insect screens.",
            "Type": "Choice",
            "Choices": [
                "none",
                "exterior",
                "interior"
            ],
            "Required": "false"
        },
        "window_storm_type" : {
            "Name": "window_storm_type",
            "Display Name": "Windows: Storm Type",
            "Description": "The type of storm, if present. If not provided, assumes there is no storm.",
            "Type": "Choice",
            "Choices": [
                "clear",
                "low-e"
            ],
            "Required": "false"
        },
        "overhangs_front_depth" : {
            "Name": "overhangs_front_depth",
            "Display Name": "Overhangs: Front Depth",
            "Description": "The depth of overhangs for windows for the front facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "overhangs_front_distance_to_top_of_window" : {
            "Name": "overhangs_front_distance_to_top_of_window",
            "Display Name": "Overhangs: Front Distance to Top of Window",
            "Description": "The overhangs distance to the top of window for the front facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "overhangs_front_distance_to_bottom_of_window" : {
            "Name": "overhangs_front_distance_to_bottom_of_window",
            "Display Name": "Overhangs: Front Distance to Bottom of Window",
            "Description": "The overhangs distance to the bottom of window for the front facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "4",
            "Required": "true"
        },
        "overhangs_back_depth" : {
            "Name": "overhangs_back_depth",
            "Display Name": "Overhangs: Back Depth",
            "Description": "The depth of overhangs for windows for the back facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "overhangs_back_distance_to_top_of_window" : {
            "Name": "overhangs_back_distance_to_top_of_window",
            "Display Name": "Overhangs: Back Distance to Top of Window",
            "Description": "The overhangs distance to the top of window for the back facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "overhangs_back_distance_to_bottom_of_window" : {
            "Name": "overhangs_back_distance_to_bottom_of_window",
            "Display Name": "Overhangs: Back Distance to Bottom of Window",
            "Description": "The overhangs distance to the bottom of window for the back facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "4",
            "Required": "true"
        },
        "overhangs_left_depth" : {
            "Name": "overhangs_left_depth",
            "Display Name": "Overhangs: Left Depth",
            "Description": "The depth of overhangs for windows for the left facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "overhangs_left_distance_to_top_of_window" : {
            "Name": "overhangs_left_distance_to_top_of_window",
            "Display Name": "Overhangs: Left Distance to Top of Window",
            "Description": "The overhangs distance to the top of window for the left facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "overhangs_left_distance_to_bottom_of_window" : {
            "Name": "overhangs_left_distance_to_bottom_of_window",
            "Display Name": "Overhangs: Left Distance to Bottom of Window",
            "Description": "The overhangs distance to the bottom of window for the left facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "4",
            "Required": "true"
        },
        "overhangs_right_depth" : {
            "Name": "overhangs_right_depth",
            "Display Name": "Overhangs: Right Depth",
            "Description": "The depth of overhangs for windows for the right facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "overhangs_right_distance_to_top_of_window" : {
            "Name": "overhangs_right_distance_to_top_of_window",
            "Display Name": "Overhangs: Right Distance to Top of Window",
            "Description": "The overhangs distance to the top of window for the right facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
        },
        "overhangs_right_distance_to_bottom_of_window" : {
            "Name": "overhangs_right_distance_to_bottom_of_window",
            "Display Name": "Overhangs: Right Distance to Bottom of Window",
            "Description": "The overhangs distance to the bottom of window for the right facade.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "4",
            "Required": "true"
        },
        "skylight_area_front" : {
            "Name": "skylight_area_front",
            "Display Name": "Skylights: Front Roof Area",
            "Description": "The amount of skylight area on the unit's front conditioned roof facade.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "skylight_area_back" : {
            "Name": "skylight_area_back",
            "Display Name": "Skylights: Back Roof Area",
            "Description": "The amount of skylight area on the unit's back conditioned roof facade.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "skylight_area_left" : {
            "Name": "skylight_area_left",
            "Display Name": "Skylights: Left Roof Area",
            "Description": "The amount of skylight area on the unit's left conditioned roof facade (when viewed from the front).",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "skylight_area_right" : {
            "Name": "skylight_area_right",
            "Display Name": "Skylights: Right Roof Area",
            "Description": "The amount of skylight area on the unit's right conditioned roof facade (when viewed from the front).",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "skylight_ufactor" : {
            "Name": "skylight_ufactor",
            "Display Name": "Skylights: U-Factor",
            "Description": "Full-assembly NFRC U-factor.",
            "Type": "Double",
            "Units": "Btu/hr-ft^2-R",
            "Default Value": "0.33",
            "Required": "true"
        },
        "skylight_shgc" : {
            "Name": "skylight_shgc",
            "Display Name": "Skylights: SHGC",
            "Description": "Full-assembly NFRC solar heat gain coefficient.",
            "Type": "Double",
            "Default Value": "0.45",
            "Required": "true"
        },
        "skylight_storm_type" : {
            "Name": "skylight_storm_type",
            "Display Name": "Skylights: Storm Type",
            "Description": "The type of storm, if present. If not provided, assumes there is no storm.",
            "Type": "Choice",
            "Choices": [
                "clear",
                "low-e"
            ],
            "Required": "false"
        },
        "door_area" : {
            "Name": "door_area",
            "Display Name": "Doors: Area",
            "Description": "The area of the opaque door(s).",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "20",
            "Required": "true"
        },
        "door_rvalue" : {
            "Name": "door_rvalue",
            "Display Name": "Doors: R-value",
            "Description": "R-value of the opaque door(s).",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "4.4",
            "Required": "true"
        },
        "air_leakage_leakiness_description" : {
            "Name": "air_leakage_leakiness_description",
            "Display Name": "Air Leakage: Leakiness Description",
            "Description": "Qualitative description of infiltration. If provided, the Year Built of the home is required. Either provide this input or provide a numeric air leakage value below.",
            "Type": "Choice",
            "Default Value": "average",
            "Choices": [
                "very tight",
                "tight",
                "average",
                "leaky",
                "very leaky"
            ],
            "Required": "false"
        },
        "air_leakage_units" : {
            "Name": "air_leakage_units",
            "Display Name": "Air Leakage: Units",
            "Description": "The unit of measure for the air leakage if providing a numeric air leakage value.",
            "Type": "Choice",
            "Choices": [
                "ACH",
                "CFM",
                "ACHnatural",
                "CFMnatural",
                "EffectiveLeakageArea"
            ],
            "Required": "false"
        },
        "air_leakage_house_pressure" : {
            "Name": "air_leakage_house_pressure",
            "Display Name": "Air Leakage: House Pressure",
            "Description": "The house pressure relative to outside if providing a numeric air leakage value. Required when units are ACH or CFM.",
            "Type": "Double",
            "Units": "Pa",
            "Required": "false"
        },
        "air_leakage_value" : {
            "Name": "air_leakage_value",
            "Display Name": "Air Leakage: Value",
            "Description": "Numeric air leakage value. For 'EffectiveLeakageArea', provide value in sq. in. If provided, overrides Leakiness Description input.",
            "Type": "Double",
            "Required": "false"
        },
        "air_leakage_type" : {
            "Name": "air_leakage_type",
            "Display Name": "Air Leakage: Type",
            "Description": "Type of air leakage if providing a numeric air leakage value. If 'unit total', represents the total infiltration to the unit as measured by a compartmentalization test, in which case the air leakage value will be adjusted by the ratio of exterior envelope surface area to total envelope surface area. Otherwise, if 'unit exterior only', represents the infiltration to the unit from outside only as measured by a guarded test. Required when unit type is single-family attached or apartment unit.",
            "Type": "Choice",
            "Choices": [
                "unit total",
                "unit exterior only"
            ],
            "Required": "false"
        },
        "air_leakage_has_flue_or_chimney_in_conditioned_space" : {
            "Name": "air_leakage_has_flue_or_chimney_in_conditioned_space",
            "Display Name": "Air Leakage: Has Flue or Chimney in Conditioned Space",
            "Description": "Presence of flue or chimney with combustion air from conditioned space; used for infiltration model. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#flue-or-chimney'>Flue or Chimney</a>) is used.",
            "Type": "Boolean",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "heating_system_type" : {
            "Name": "heating_system_type",
            "Display Name": "Heating System: Type",
            "Description": "The type of heating system. Use 'none' if there is no heating system or if there is a heat pump serving a heating load.",
            "Type": "Choice",
            "Default Value": "Furnace",
            "Choices": [
                "none",
                "Furnace",
                "WallFurnace",
                "FloorFurnace",
                "Boiler",
                "ElectricResistance",
                "Stove",
                "SpaceHeater",
                "Fireplace",
                "Shared Boiler w/ Baseboard",
                "Shared Boiler w/ Ductless Fan Coil"
            ],
            "Required": "true"
        },
        "heating_system_fuel" : {
            "Name": "heating_system_fuel",
            "Display Name": "Heating System: Fuel Type",
            "Description": "The fuel type of the heating system. Ignored for ElectricResistance.",
            "Type": "Choice",
            "Default Value": "natural gas",
            "Choices": [
                "electricity",
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "wood pellets",
                "coal"
            ],
            "Required": "true"
        },
        "heating_system_heating_efficiency" : {
            "Name": "heating_system_heating_efficiency",
            "Display Name": "Heating System: Rated AFUE or Percent",
            "Description": "The rated heating efficiency value of the heating system.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.78",
            "Required": "true"
        },
        "heating_system_heating_capacity" : {
            "Name": "heating_system_heating_capacity",
            "Display Name": "Heating System: Heating Capacity",
            "Description": "The output heating capacity of the heating system. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-heating-systems'>HPXML Heating Systems</a>) is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heating_system_heating_autosizing_factor" : {
            "Name": "heating_system_heating_autosizing_factor",
            "Display Name": "Heating System: Heating Autosizing Factor",
            "Description": "The capacity scaling factor applied to the auto-sizing methodology. If not provided, 1.0 is used.",
            "Type": "Double",
            "Required": "false"
        },
        "heating_system_heating_autosizing_limit" : {
            "Name": "heating_system_heating_autosizing_limit",
            "Display Name": "Heating System: Heating Autosizing Limit",
            "Description": "The maximum capacity limit applied to the auto-sizing methodology. If not provided, no limit is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heating_system_fraction_heat_load_served" : {
            "Name": "heating_system_fraction_heat_load_served",
            "Display Name": "Heating System: Fraction Heat Load Served",
            "Description": "The heating load served by the heating system.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "1",
            "Required": "true"
        },
        "heating_system_pilot_light" : {
            "Name": "heating_system_pilot_light",
            "Display Name": "Heating System: Pilot Light",
            "Description": "The fuel usage of the pilot light. Applies only to Furnace, WallFurnace, FloorFurnace, Stove, Boiler, and Fireplace with non-electric fuel type. If not provided, assumes no pilot light.",
            "Type": "Double",
            "Units": "Btuh",
            "Required": "false"
        },
        "heating_system_airflow_defect_ratio" : {
            "Name": "heating_system_airflow_defect_ratio",
            "Display Name": "Heating System: Airflow Defect Ratio",
            "Description": "The airflow defect ratio, defined as (InstalledAirflow - DesignAirflow) / DesignAirflow, of the heating system per ANSI/RESNET/ACCA Standard 310. A value of zero means no airflow defect. Applies only to Furnace. If not provided, assumes no defect.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "cooling_system_type" : {
            "Name": "cooling_system_type",
            "Display Name": "Cooling System: Type",
            "Description": "The type of cooling system. Use 'none' if there is no cooling system or if there is a heat pump serving a cooling load.",
            "Type": "Choice",
            "Default Value": "central air conditioner",
            "Choices": [
                "none",
                "central air conditioner",
                "room air conditioner",
                "evaporative cooler",
                "mini-split",
                "packaged terminal air conditioner"
            ],
            "Required": "true"
        },
        "cooling_system_cooling_efficiency_type" : {
            "Name": "cooling_system_cooling_efficiency_type",
            "Display Name": "Cooling System: Efficiency Type",
            "Description": "The efficiency type of the cooling system. System types central air conditioner and mini-split use SEER or SEER2. System types room air conditioner and packaged terminal air conditioner use EER or CEER. Ignored for system type evaporative cooler.",
            "Type": "Choice",
            "Default Value": "SEER",
            "Choices": [
                "SEER",
                "SEER2",
                "EER",
                "CEER"
            ],
            "Required": "true"
        },
        "cooling_system_cooling_efficiency" : {
            "Name": "cooling_system_cooling_efficiency",
            "Display Name": "Cooling System: Efficiency",
            "Description": "The rated efficiency value of the cooling system. Ignored for evaporative cooler.",
            "Type": "Double",
            "Default Value": "13",
            "Required": "true"
        },
        "cooling_system_cooling_compressor_type" : {
            "Name": "cooling_system_cooling_compressor_type",
            "Display Name": "Cooling System: Cooling Compressor Type",
            "Description": "The compressor type of the cooling system. Only applies to central air conditioner and mini-split.",
            "Type": "Choice",
            "Choices": [
                "single stage",
                "two stage",
                "variable speed"
            ],
            "Required": "false"
        },
        "cooling_system_cooling_sensible_heat_fraction" : {
            "Name": "cooling_system_cooling_sensible_heat_fraction",
            "Display Name": "Cooling System: Cooling Sensible Heat Fraction",
            "Description": "The sensible heat fraction of the cooling system. Ignored for evaporative cooler. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#central-air-conditioner'>Central Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner'>Room Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-air-conditioner'>Packaged Terminal Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-air-conditioner'>Mini-Split Air Conditioner</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "cooling_system_cooling_capacity" : {
            "Name": "cooling_system_cooling_capacity",
            "Display Name": "Cooling System: Cooling Capacity",
            "Description": "The output cooling capacity of the cooling system. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#central-air-conditioner'>Central Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner'>Room Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-air-conditioner'>Packaged Terminal Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#evaporative-cooler'>Evaporative Cooler</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-air-conditioner'>Mini-Split Air Conditioner</a>) is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "cooling_system_cooling_autosizing_factor" : {
            "Name": "cooling_system_cooling_autosizing_factor",
            "Display Name": "Cooling System: Cooling Autosizing Factor",
            "Description": "The capacity scaling factor applied to the auto-sizing methodology. If not provided, 1.0 is used.",
            "Type": "Double",
            "Required": "false"
        },
        "cooling_system_cooling_autosizing_limit" : {
            "Name": "cooling_system_cooling_autosizing_limit",
            "Display Name": "Cooling System: Cooling Autosizing Limit",
            "Description": "The maximum capacity limit applied to the auto-sizing methodology. If not provided, no limit is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "cooling_system_fraction_cool_load_served" : {
            "Name": "cooling_system_fraction_cool_load_served",
            "Display Name": "Cooling System: Fraction Cool Load Served",
            "Description": "The cooling load served by the cooling system.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "1",
            "Required": "true"
        },
        "cooling_system_is_ducted" : {
            "Name": "cooling_system_is_ducted",
            "Display Name": "Cooling System: Is Ducted",
            "Description": "Whether the cooling system is ducted or not. Only used for mini-split and evaporative cooler. It's assumed that central air conditioner is ducted, and room air conditioner and packaged terminal air conditioner are not ducted.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "cooling_system_airflow_defect_ratio" : {
            "Name": "cooling_system_airflow_defect_ratio",
            "Display Name": "Cooling System: Airflow Defect Ratio",
            "Description": "The airflow defect ratio, defined as (InstalledAirflow - DesignAirflow) / DesignAirflow, of the cooling system per ANSI/RESNET/ACCA Standard 310. A value of zero means no airflow defect. Applies only to central air conditioner and ducted mini-split. If not provided, assumes no defect.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "cooling_system_charge_defect_ratio" : {
            "Name": "cooling_system_charge_defect_ratio",
            "Display Name": "Cooling System: Charge Defect Ratio",
            "Description": "The refrigerant charge defect ratio, defined as (InstalledCharge - DesignCharge) / DesignCharge, of the cooling system per ANSI/RESNET/ACCA Standard 310. A value of zero means no refrigerant charge defect. Applies only to central air conditioner and mini-split. If not provided, assumes no defect.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "cooling_system_crankcase_heater_watts" : {
            "Name": "cooling_system_crankcase_heater_watts",
            "Display Name": "Cooling System: Crankcase Heater Power Watts",
            "Description": "Cooling system crankcase heater power consumption in Watts. Applies only to central air conditioner, room air conditioner, packaged terminal air conditioner and mini-split. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#central-air-conditioner'>Central Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner'>Room Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-air-conditioner'>Packaged Terminal Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-air-conditioner'>Mini-Split Air Conditioner</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "cooling_system_integrated_heating_system_fuel" : {
            "Name": "cooling_system_integrated_heating_system_fuel",
            "Display Name": "Cooling System: Integrated Heating System Fuel Type",
            "Description": "The fuel type of the heating system integrated into cooling system. Only used for packaged terminal air conditioner and room air conditioner.",
            "Type": "Choice",
            "Choices": [
                "electricity",
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "wood pellets",
                "coal"
            ],
            "Required": "false"
        },
        "cooling_system_integrated_heating_system_efficiency_percent" : {
            "Name": "cooling_system_integrated_heating_system_efficiency_percent",
            "Display Name": "Cooling System: Integrated Heating System Efficiency",
            "Description": "The rated heating efficiency value of the heating system integrated into cooling system. Only used for packaged terminal air conditioner and room air conditioner.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "cooling_system_integrated_heating_system_capacity" : {
            "Name": "cooling_system_integrated_heating_system_capacity",
            "Display Name": "Cooling System: Integrated Heating System Heating Capacity",
            "Description": "The output heating capacity of the heating system integrated into cooling system. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner'>Room Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-air-conditioner'>Packaged Terminal Air Conditioner</a>) is used. Only used for room air conditioner and packaged terminal air conditioner.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "cooling_system_integrated_heating_system_fraction_heat_load_served" : {
            "Name": "cooling_system_integrated_heating_system_fraction_heat_load_served",
            "Display Name": "Cooling System: Integrated Heating System Fraction Heat Load Served",
            "Description": "The heating load served by the heating system integrated into cooling system. Only used for packaged terminal air conditioner and room air conditioner.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_type" : {
            "Name": "heat_pump_type",
            "Display Name": "Heat Pump: Type",
            "Description": "The type of heat pump. Use 'none' if there is no heat pump.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "air-to-air",
                "mini-split",
                "ground-to-air",
                "packaged terminal heat pump",
                "room air conditioner with reverse cycle"
            ],
            "Required": "true"
        },
        "heat_pump_heating_efficiency_type" : {
            "Name": "heat_pump_heating_efficiency_type",
            "Display Name": "Heat Pump: Heating Efficiency Type",
            "Description": "The heating efficiency type of heat pump. System types air-to-air and mini-split use HSPF or HSPF2. System types ground-to-air, packaged terminal heat pump and room air conditioner with reverse cycle use COP.",
            "Type": "Choice",
            "Default Value": "HSPF",
            "Choices": [
                "HSPF",
                "HSPF2",
                "COP"
            ],
            "Required": "true"
        },
        "heat_pump_heating_efficiency" : {
            "Name": "heat_pump_heating_efficiency",
            "Display Name": "Heat Pump: Heating Efficiency",
            "Description": "The rated heating efficiency value of the heat pump.",
            "Type": "Double",
            "Default Value": "7.7",
            "Required": "true"
        },
        "heat_pump_cooling_efficiency_type" : {
            "Name": "heat_pump_cooling_efficiency_type",
            "Display Name": "Heat Pump: Cooling Efficiency Type",
            "Description": "The cooling efficiency type of heat pump. System types air-to-air and mini-split use SEER or SEER2. System types ground-to-air, packaged terminal heat pump and room air conditioner with reverse cycle use EER.",
            "Type": "Choice",
            "Default Value": "SEER",
            "Choices": [
                "SEER",
                "SEER2",
                "EER",
                "CEER"
            ],
            "Required": "true"
        },
        "heat_pump_cooling_efficiency" : {
            "Name": "heat_pump_cooling_efficiency",
            "Display Name": "Heat Pump: Cooling Efficiency",
            "Description": "The rated cooling efficiency value of the heat pump.",
            "Type": "Double",
            "Default Value": "13",
            "Required": "true"
        },
        "heat_pump_cooling_compressor_type" : {
            "Name": "heat_pump_cooling_compressor_type",
            "Display Name": "Heat Pump: Cooling Compressor Type",
            "Description": "The compressor type of the heat pump. Only applies to air-to-air, mini-split and ground-to-air.",
            "Type": "Choice",
            "Choices": [
                "single stage",
                "two stage",
                "variable speed"
            ],
            "Required": "false"
        },
        "heat_pump_cooling_sensible_heat_fraction" : {
            "Name": "heat_pump_cooling_sensible_heat_fraction",
            "Display Name": "Heat Pump: Cooling Sensible Heat Fraction",
            "Description": "The sensible heat fraction of the heat pump. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#ground-to-air-heat-pump'>Ground-to-Air Heat Pump</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_heating_capacity" : {
            "Name": "heat_pump_heating_capacity",
            "Display Name": "Heat Pump: Heating Capacity",
            "Description": "The output heating capacity of the heat pump. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#ground-to-air-heat-pump'>Ground-to-Air Heat Pump</a>) is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heat_pump_heating_autosizing_factor" : {
            "Name": "heat_pump_heating_autosizing_factor",
            "Display Name": "Heat Pump: Heating Autosizing Factor",
            "Description": "The capacity scaling factor applied to the auto-sizing methodology. If not provided, 1.0 is used.",
            "Type": "Double",
            "Required": "false"
        },
        "heat_pump_heating_autosizing_limit" : {
            "Name": "heat_pump_heating_autosizing_limit",
            "Display Name": "Heat Pump: Heating Autosizing Limit",
            "Description": "The maximum capacity limit applied to the auto-sizing methodology. If not provided, no limit is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heat_pump_heating_capacity_retention_fraction" : {
            "Name": "heat_pump_heating_capacity_retention_fraction",
            "Display Name": "Heat Pump: Heating Capacity Retention Fraction",
            "Description": "The output heating capacity of the heat pump at a user-specified temperature (e.g., 17F or 5F) divided by the above nominal heating capacity. Applies to all heat pump types except ground-to-air. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_heating_capacity_retention_temp" : {
            "Name": "heat_pump_heating_capacity_retention_temp",
            "Display Name": "Heat Pump: Heating Capacity Retention Temperature",
            "Description": "The user-specified temperature (e.g., 17F or 5F) for the above heating capacity retention fraction. Applies to all heat pump types except ground-to-air. Required if the Heating Capacity Retention Fraction is provided.",
            "Type": "Double",
            "Units": "F",
            "Required": "false"
        },
        "heat_pump_cooling_capacity" : {
            "Name": "heat_pump_cooling_capacity",
            "Display Name": "Heat Pump: Cooling Capacity",
            "Description": "The output cooling capacity of the heat pump. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#ground-to-air-heat-pump'>Ground-to-Air Heat Pump</a>) is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heat_pump_cooling_autosizing_factor" : {
            "Name": "heat_pump_cooling_autosizing_factor",
            "Display Name": "Heat Pump: Cooling Autosizing Factor",
            "Description": "The capacity scaling factor applied to the auto-sizing methodology. If not provided, 1.0 is used.",
            "Type": "Double",
            "Required": "false"
        },
        "heat_pump_cooling_autosizing_limit" : {
            "Name": "heat_pump_cooling_autosizing_limit",
            "Display Name": "Heat Pump: Cooling Autosizing Limit",
            "Description": "The maximum capacity limit applied to the auto-sizing methodology. If not provided, no limit is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heat_pump_fraction_heat_load_served" : {
            "Name": "heat_pump_fraction_heat_load_served",
            "Display Name": "Heat Pump: Fraction Heat Load Served",
            "Description": "The heating load served by the heat pump.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "1",
            "Required": "true"
        },
        "heat_pump_fraction_cool_load_served" : {
            "Name": "heat_pump_fraction_cool_load_served",
            "Display Name": "Heat Pump: Fraction Cool Load Served",
            "Description": "The cooling load served by the heat pump.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "1",
            "Required": "true"
        },
        "heat_pump_compressor_lockout_temp" : {
            "Name": "heat_pump_compressor_lockout_temp",
            "Display Name": "Heat Pump: Compressor Lockout Temperature",
            "Description": "The temperature below which the heat pump compressor is disabled. If both this and Backup Heating Lockout Temperature are provided and use the same value, it essentially defines a switchover temperature (for, e.g., a dual-fuel heat pump). Applies to all heat pump types other than ground-to-air. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>) is used.",
            "Type": "Double",
            "Units": "F",
            "Required": "false"
        },
        "heat_pump_backup_type" : {
            "Name": "heat_pump_backup_type",
            "Display Name": "Heat Pump: Backup Type",
            "Description": "The backup type of the heat pump. If 'integrated', represents e.g. built-in electric strip heat or dual-fuel integrated furnace. If 'separate', represents e.g. electric baseboard or boiler based on the Heating System 2 specified below. Use 'none' if there is no backup heating.",
            "Type": "Choice",
            "Default Value": "integrated",
            "Choices": [
                "none",
                "integrated",
                "separate"
            ],
            "Required": "true"
        },
        "heat_pump_backup_heating_autosizing_factor" : {
            "Name": "heat_pump_backup_heating_autosizing_factor",
            "Display Name": "Heat Pump: Backup Heating Autosizing Factor",
            "Description": "The capacity scaling factor applied to the auto-sizing methodology if Backup Type is 'integrated'. If not provided, 1.0 is used. If Backup Type is 'separate', use Heating System 2: Heating Autosizing Factor.",
            "Type": "Double",
            "Required": "false"
        },
        "heat_pump_backup_heating_autosizing_limit" : {
            "Name": "heat_pump_backup_heating_autosizing_limit",
            "Display Name": "Heat Pump: Backup Heating Autosizing Limit",
            "Description": "The maximum capacity limit applied to the auto-sizing methodology if Backup Type is 'integrated'. If not provided, no limit is used. If Backup Type is 'separate', use Heating System 2: Heating Autosizing Limit.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heat_pump_backup_fuel" : {
            "Name": "heat_pump_backup_fuel",
            "Display Name": "Heat Pump: Backup Fuel Type",
            "Description": "The backup fuel type of the heat pump. Only applies if Backup Type is 'integrated'.",
            "Type": "Choice",
            "Default Value": "electricity",
            "Choices": [
                "electricity",
                "natural gas",
                "fuel oil",
                "propane"
            ],
            "Required": "true"
        },
        "heat_pump_backup_heating_efficiency" : {
            "Name": "heat_pump_backup_heating_efficiency",
            "Display Name": "Heat Pump: Backup Rated Efficiency",
            "Description": "The backup rated efficiency value of the heat pump. Percent for electricity fuel type. AFUE otherwise. Only applies if Backup Type is 'integrated'.",
            "Type": "Double",
            "Default Value": "1",
            "Required": "true"
        },
        "heat_pump_backup_heating_capacity" : {
            "Name": "heat_pump_backup_heating_capacity",
            "Display Name": "Heat Pump: Backup Heating Capacity",
            "Description": "The backup output heating capacity of the heat pump. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#backup'>Backup</a>) is used. Only applies if Backup Type is 'integrated'.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heat_pump_backup_heating_lockout_temp" : {
            "Name": "heat_pump_backup_heating_lockout_temp",
            "Display Name": "Heat Pump: Backup Heating Lockout Temperature",
            "Description": "The temperature above which the heat pump backup system is disabled. If both this and Compressor Lockout Temperature are provided and use the same value, it essentially defines a switchover temperature (for, e.g., a dual-fuel heat pump). Applies for both Backup Type of 'integrated' and 'separate'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#backup'>Backup</a>) is used.",
            "Type": "Double",
            "Units": "F",
            "Required": "false"
        },
        "heat_pump_sizing_methodology" : {
            "Name": "heat_pump_sizing_methodology",
            "Display Name": "Heat Pump: Sizing Methodology",
            "Description": "The auto-sizing methodology to use when the heat pump capacity is not provided. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-hvac-sizing-control'>HPXML HVAC Sizing Control</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "ACCA",
                "HERS",
                "MaxLoad"
            ],
            "Required": "false"
        },
        "heat_pump_backup_sizing_methodology" : {
            "Name": "heat_pump_backup_sizing_methodology",
            "Display Name": "Heat Pump: Backup Sizing Methodology",
            "Description": "The auto-sizing methodology to use when the heat pump backup capacity is not provided. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-hvac-sizing-control'>HPXML HVAC Sizing Control</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "emergency",
                "supplemental"
            ],
            "Required": "false"
        },
        "heat_pump_is_ducted" : {
            "Name": "heat_pump_is_ducted",
            "Display Name": "Heat Pump: Is Ducted",
            "Description": "Whether the heat pump is ducted or not. Only used for mini-split. It's assumed that air-to-air and ground-to-air are ducted, and packaged terminal heat pump and room air conditioner with reverse cycle are not ducted. If not provided, assumes not ducted.",
            "Type": "Boolean",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "heat_pump_airflow_defect_ratio" : {
            "Name": "heat_pump_airflow_defect_ratio",
            "Display Name": "Heat Pump: Airflow Defect Ratio",
            "Description": "The airflow defect ratio, defined as (InstalledAirflow - DesignAirflow) / DesignAirflow, of the heat pump per ANSI/RESNET/ACCA Standard 310. A value of zero means no airflow defect. Applies only to air-to-air, ducted mini-split, and ground-to-air. If not provided, assumes no defect.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_charge_defect_ratio" : {
            "Name": "heat_pump_charge_defect_ratio",
            "Display Name": "Heat Pump: Charge Defect Ratio",
            "Description": "The refrigerant charge defect ratio, defined as (InstalledCharge - DesignCharge) / DesignCharge, of the heat pump per ANSI/RESNET/ACCA Standard 310. A value of zero means no refrigerant charge defect. Applies to all heat pump types. If not provided, assumes no defect.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_crankcase_heater_watts" : {
            "Name": "heat_pump_crankcase_heater_watts",
            "Display Name": "Heat Pump: Crankcase Heater Power Watts",
            "Description": "Heat Pump crankcase heater power consumption in Watts. Applies only to air-to-air, mini-split, packaged terminal heat pump and room air conditioner with reverse cycle. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "hvac_perf_data_capacity_type" : {
            "Name": "hvac_perf_data_capacity_type",
            "Display Name": "HVAC Detailed Performance Data: Capacity Type",
            "Description": "Type of capacity values for detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps).",
            "Type": "Choice",
            "Units": "Absolute capacities",
            "Choices": [
                "Absolute capacities",
                "Normalized capacity fractions"
            ],
            "Required": "false"
        },
        "hvac_perf_data_heating_outdoor_temperatures" : {
            "Name": "hvac_perf_data_heating_outdoor_temperatures",
            "Display Name": "HVAC Detailed Performance Data: Heating Outdoor Temperatures",
            "Description": "Outdoor temperatures of heating detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). One of the outdoor temperatures must be 47 F. At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "F",
            "Required": "false"
        },
        "hvac_perf_data_heating_min_speed_capacities" : {
            "Name": "hvac_perf_data_heating_min_speed_capacities",
            "Display Name": "HVAC Detailed Performance Data: Heating Minimum Speed Capacities",
            "Description": "Minimum speed capacities of heating detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "Btu/hr or Frac",
            "Required": "false"
        },
        "hvac_perf_data_heating_max_speed_capacities" : {
            "Name": "hvac_perf_data_heating_max_speed_capacities",
            "Display Name": "HVAC Detailed Performance Data: Heating Maximum Speed Capacities",
            "Description": "Maximum speed capacities of heating detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "Btu/hr or Frac",
            "Required": "false"
        },
        "hvac_perf_data_heating_min_speed_cops" : {
            "Name": "hvac_perf_data_heating_min_speed_cops",
            "Display Name": "HVAC Detailed Performance Data: Heating Minimum Speed COPs",
            "Description": "Minimum speed efficiency COP values of heating detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "W/W",
            "Required": "false"
        },
        "hvac_perf_data_heating_max_speed_cops" : {
            "Name": "hvac_perf_data_heating_max_speed_cops",
            "Display Name": "HVAC Detailed Performance Data: Heating Maximum Speed COPs",
            "Description": "Maximum speed efficiency COP values of heating detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "W/W",
            "Required": "false"
        },
        "hvac_perf_data_cooling_outdoor_temperatures" : {
            "Name": "hvac_perf_data_cooling_outdoor_temperatures",
            "Display Name": "HVAC Detailed Performance Data: Cooling Outdoor Temperatures",
            "Description": "Outdoor temperatures of cooling detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). One of the outdoor temperatures must be 95 F. At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "F",
            "Required": "false"
        },
        "hvac_perf_data_cooling_min_speed_capacities" : {
            "Name": "hvac_perf_data_cooling_min_speed_capacities",
            "Display Name": "HVAC Detailed Performance Data: Cooling Minimum Speed Capacities",
            "Description": "Minimum speed capacities of cooling detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "Btu/hr or Frac",
            "Required": "false"
        },
        "hvac_perf_data_cooling_max_speed_capacities" : {
            "Name": "hvac_perf_data_cooling_max_speed_capacities",
            "Display Name": "HVAC Detailed Performance Data: Cooling Maximum Speed Capacities",
            "Description": "Maximum speed capacities of cooling detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "Btu/hr or Frac",
            "Required": "false"
        },
        "hvac_perf_data_cooling_min_speed_cops" : {
            "Name": "hvac_perf_data_cooling_min_speed_cops",
            "Display Name": "HVAC Detailed Performance Data: Cooling Minimum Speed COPs",
            "Description": "Minimum speed efficiency COP values of cooling detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "W/W",
            "Required": "false"
        },
        "hvac_perf_data_cooling_max_speed_cops" : {
            "Name": "hvac_perf_data_cooling_max_speed_cops",
            "Display Name": "HVAC Detailed Performance Data: Cooling Maximum Speed COPs",
            "Description": "Maximum speed efficiency COP values of cooling detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "W/W",
            "Required": "false"
        },
        "geothermal_loop_configuration" : {
            "Name": "geothermal_loop_configuration",
            "Display Name": "Geothermal Loop: Configuration",
            "Description": "Configuration of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#ground-to-air-heat-pump'>Ground-to-Air Heat Pump</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "none",
                "vertical"
            ],
            "Required": "false"
        },
        "geothermal_loop_borefield_configuration" : {
            "Name": "geothermal_loop_borefield_configuration",
            "Display Name": "Geothermal Loop: Borefield Configuration",
            "Description": "Borefield configuration of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "Rectangle",
                "Open Rectangle",
                "C",
                "L",
                "U",
                "Lopsided U"
            ],
            "Required": "false"
        },
        "geothermal_loop_loop_flow" : {
            "Name": "geothermal_loop_loop_flow",
            "Display Name": "Geothermal Loop: Loop Flow",
            "Description": "Water flow rate through the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Double",
            "Units": "gpm",
            "Required": "false"
        },
        "geothermal_loop_boreholes_count" : {
            "Name": "geothermal_loop_boreholes_count",
            "Display Name": "Geothermal Loop: Boreholes Count",
            "Description": "Number of boreholes. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "geothermal_loop_boreholes_length" : {
            "Name": "geothermal_loop_boreholes_length",
            "Display Name": "Geothermal Loop: Boreholes Length",
            "Description": "Average length of each borehole (vertical). Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "geothermal_loop_boreholes_spacing" : {
            "Name": "geothermal_loop_boreholes_spacing",
            "Display Name": "Geothermal Loop: Boreholes Spacing",
            "Description": "Distance between bores. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "geothermal_loop_boreholes_diameter" : {
            "Name": "geothermal_loop_boreholes_diameter",
            "Display Name": "Geothermal Loop: Boreholes Diameter",
            "Description": "Diameter of bores. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Double",
            "Units": "in",
            "Required": "false"
        },
        "geothermal_loop_grout_type" : {
            "Name": "geothermal_loop_grout_type",
            "Display Name": "Geothermal Loop: Grout Type",
            "Description": "Grout type of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "standard",
                "thermally enhanced"
            ],
            "Required": "false"
        },
        "geothermal_loop_pipe_type" : {
            "Name": "geothermal_loop_pipe_type",
            "Display Name": "Geothermal Loop: Pipe Type",
            "Description": "Pipe type of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "standard",
                "thermally enhanced"
            ],
            "Required": "false"
        },
        "geothermal_loop_pipe_diameter" : {
            "Name": "geothermal_loop_pipe_diameter",
            "Display Name": "Geothermal Loop: Pipe Diameter",
            "Description": "Pipe diameter of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Choice",
            "Units": "in",
            "Choices": [
                "3/4\" pipe",
                "1\" pipe",
                "1-1/4\" pipe"
            ],
            "Required": "false"
        },
        "heating_system_2_type" : {
            "Name": "heating_system_2_type",
            "Display Name": "Heating System 2: Type",
            "Description": "The type of the second heating system. If a heat pump is specified and the backup type is 'separate', this heating system represents 'separate' backup heating. For ducted heat pumps where the backup heating system is a 'Furnace', the backup would typically be characterized as 'integrated' in that the furnace and heat pump share the same distribution system and blower fan; a 'Furnace' as 'separate' backup to a ducted heat pump is not supported.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "Furnace",
                "WallFurnace",
                "FloorFurnace",
                "Boiler",
                "ElectricResistance",
                "Stove",
                "SpaceHeater",
                "Fireplace"
            ],
            "Required": "true"
        },
        "heating_system_2_fuel" : {
            "Name": "heating_system_2_fuel",
            "Display Name": "Heating System 2: Fuel Type",
            "Description": "The fuel type of the second heating system. Ignored for ElectricResistance.",
            "Type": "Choice",
            "Default Value": "electricity",
            "Choices": [
                "electricity",
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "wood pellets",
                "coal"
            ],
            "Required": "true"
        },
        "heating_system_2_heating_efficiency" : {
            "Name": "heating_system_2_heating_efficiency",
            "Display Name": "Heating System 2: Rated AFUE or Percent",
            "Description": "The rated heating efficiency value of the second heating system.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "1",
            "Required": "true"
        },
        "heating_system_2_heating_capacity" : {
            "Name": "heating_system_2_heating_capacity",
            "Display Name": "Heating System 2: Heating Capacity",
            "Description": "The output heating capacity of the second heating system. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-heating-systems'>HPXML Heating Systems</a>) is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heating_system_2_heating_autosizing_factor" : {
            "Name": "heating_system_2_heating_autosizing_factor",
            "Display Name": "Heating System 2: Heating Autosizing Factor",
            "Description": "The capacity scaling factor applied to the auto-sizing methodology. If not provided, 1.0 is used.",
            "Type": "Double",
            "Required": "false"
        },
        "heating_system_2_heating_autosizing_limit" : {
            "Name": "heating_system_2_heating_autosizing_limit",
            "Display Name": "Heating System 2: Heating Autosizing Limit",
            "Description": "The maximum capacity limit applied to the auto-sizing methodology. If not provided, no limit is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heating_system_2_fraction_heat_load_served" : {
            "Name": "heating_system_2_fraction_heat_load_served",
            "Display Name": "Heating System 2: Fraction Heat Load Served",
            "Description": "The heat load served fraction of the second heating system. Ignored if this heating system serves as a backup system for a heat pump.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.25",
            "Required": "true"
        },
        "hvac_control_heating_weekday_setpoint" : {
            "Name": "hvac_control_heating_weekday_setpoint",
            "Display Name": "HVAC Control: Heating Weekday Setpoint Schedule",
            "Description": "Specify the constant or 24-hour comma-separated weekday heating setpoint schedule. Required unless a detailed CSV schedule is provided.",
            "Type": "String",
            "Units": "F",
            "Required": "false"
        },
        "hvac_control_heating_weekend_setpoint" : {
            "Name": "hvac_control_heating_weekend_setpoint",
            "Display Name": "HVAC Control: Heating Weekend Setpoint Schedule",
            "Description": "Specify the constant or 24-hour comma-separated weekend heating setpoint schedule. Required unless a detailed CSV schedule is provided.",
            "Type": "String",
            "Units": "F",
            "Required": "false"
        },
        "hvac_control_cooling_weekday_setpoint" : {
            "Name": "hvac_control_cooling_weekday_setpoint",
            "Display Name": "HVAC Control: Cooling Weekday Setpoint Schedule",
            "Description": "Specify the constant or 24-hour comma-separated weekday cooling setpoint schedule. Required unless a detailed CSV schedule is provided.",
            "Type": "String",
            "Units": "F",
            "Required": "false"
        },
        "hvac_control_cooling_weekend_setpoint" : {
            "Name": "hvac_control_cooling_weekend_setpoint",
            "Display Name": "HVAC Control: Cooling Weekend Setpoint Schedule",
            "Description": "Specify the constant or 24-hour comma-separated weekend cooling setpoint schedule. Required unless a detailed CSV schedule is provided.",
            "Type": "String",
            "Units": "F",
            "Required": "false"
        },
        "hvac_control_heating_season_period" : {
            "Name": "hvac_control_heating_season_period",
            "Display Name": "HVAC Control: Heating Season Period",
            "Description": "Enter a date range like 'Nov 1 - Jun 30'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-hvac-control'>HPXML HVAC Control</a>) is used. Can also provide 'BuildingAmerica' to use automatic seasons from the Building America House Simulation Protocols.",
            "Type": "String",
            "Required": "false"
        },
        "hvac_control_cooling_season_period" : {
            "Name": "hvac_control_cooling_season_period",
            "Display Name": "HVAC Control: Cooling Season Period",
            "Description": "Enter a date range like 'Jun 1 - Oct 31'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-hvac-control'>HPXML HVAC Control</a>) is used. Can also provide 'BuildingAmerica' to use automatic seasons from the Building America House Simulation Protocols.",
            "Type": "String",
            "Required": "false"
        },
        "hvac_blower_fan_watts_per_cfm" : {
            "Name": "hvac_blower_fan_watts_per_cfm",
            "Display Name": "HVAC Blower: Fan Efficiency",
            "Description": "The blower fan efficiency at maximum fan speed. Applies only to split (not packaged) systems (i.e., applies to ducted systems as well as ductless mini-split systems). If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-heating-systems'>HPXML Heating Systems</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-cooling-systems'>HPXML Cooling Systems</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-heat-pumps'>HPXML Heat Pumps</a>) is used.",
            "Type": "Double",
            "Units": "W/CFM",
            "Required": "false"
        },
        "ducts_leakage_units" : {
            "Name": "ducts_leakage_units",
            "Display Name": "Ducts: Leakage Units",
            "Description": "The leakage units of the ducts.",
            "Type": "Choice",
            "Default Value": "Percent",
            "Choices": [
                "CFM25",
                "CFM50",
                "Percent"
            ],
            "Required": "true"
        },
        "ducts_supply_leakage_to_outside_value" : {
            "Name": "ducts_supply_leakage_to_outside_value",
            "Display Name": "Ducts: Supply Leakage to Outside Value",
            "Description": "The leakage value to outside for the supply ducts.",
            "Type": "Double",
            "Default Value": "0.1",
            "Required": "true"
        },
        "ducts_supply_location" : {
            "Name": "ducts_supply_location",
            "Display Name": "Ducts: Supply Location",
            "Description": "The location of the supply ducts. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "crawlspace",
                "crawlspace - vented",
                "crawlspace - unvented",
                "crawlspace - conditioned",
                "attic",
                "attic - vented",
                "attic - unvented",
                "garage",
                "exterior wall",
                "under slab",
                "roof deck",
                "outside",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space",
                "manufactured home belly"
            ],
            "Required": "false"
        },
        "ducts_supply_insulation_r" : {
            "Name": "ducts_supply_insulation_r",
            "Display Name": "Ducts: Supply Insulation R-Value",
            "Description": "The nominal insulation r-value of the supply ducts excluding air films. Use 0 for uninsulated ducts.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "ducts_supply_buried_insulation_level" : {
            "Name": "ducts_supply_buried_insulation_level",
            "Display Name": "Ducts: Supply Buried Insulation Level",
            "Description": "Whether the supply ducts are buried in, e.g., attic loose-fill insulation. Partially buried ducts have insulation that does not cover the top of the ducts. Fully buried ducts have insulation that just covers the top of the ducts. Deeply buried ducts have insulation that continues above the top of the ducts.",
            "Type": "Choice",
            "Choices": [
                "not buried",
                "partially buried",
                "fully buried",
                "deeply buried"
            ],
            "Required": "false"
        },
        "ducts_supply_surface_area" : {
            "Name": "ducts_supply_surface_area",
            "Display Name": "Ducts: Supply Surface Area",
            "Description": "The supply ducts surface area in the given location. If neither Surface Area nor Area Fraction provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Double",
            "Units": "ft^2",
            "Required": "false"
        },
        "ducts_supply_surface_area_fraction" : {
            "Name": "ducts_supply_surface_area_fraction",
            "Display Name": "Ducts: Supply Area Fraction",
            "Description": "The fraction of supply ducts surface area in the given location. Only used if Surface Area is not provided. If the fraction is less than 1, the remaining duct area is assumed to be in conditioned space. If neither Surface Area nor Area Fraction provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Double",
            "Units": "frac",
            "Required": "false"
        },
        "ducts_supply_fraction_rectangular" : {
            "Name": "ducts_supply_fraction_rectangular",
            "Display Name": "Ducts: Supply Fraction Rectangular",
            "Description": "The fraction of supply ducts that are rectangular (as opposed to round); this affects the duct effective R-value used for modeling. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Double",
            "Units": "frac",
            "Required": "false"
        },
        "ducts_return_leakage_to_outside_value" : {
            "Name": "ducts_return_leakage_to_outside_value",
            "Display Name": "Ducts: Return Leakage to Outside Value",
            "Description": "The leakage value to outside for the return ducts.",
            "Type": "Double",
            "Default Value": "0.1",
            "Required": "true"
        },
        "ducts_return_location" : {
            "Name": "ducts_return_location",
            "Display Name": "Ducts: Return Location",
            "Description": "The location of the return ducts. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "crawlspace",
                "crawlspace - vented",
                "crawlspace - unvented",
                "crawlspace - conditioned",
                "attic",
                "attic - vented",
                "attic - unvented",
                "garage",
                "exterior wall",
                "under slab",
                "roof deck",
                "outside",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space",
                "manufactured home belly"
            ],
            "Required": "false"
        },
        "ducts_return_insulation_r" : {
            "Name": "ducts_return_insulation_r",
            "Display Name": "Ducts: Return Insulation R-Value",
            "Description": "The nominal insulation r-value of the return ducts excluding air films. Use 0 for uninsulated ducts.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "ducts_return_buried_insulation_level" : {
            "Name": "ducts_return_buried_insulation_level",
            "Display Name": "Ducts: Return Buried Insulation Level",
            "Description": "Whether the return ducts are buried in, e.g., attic loose-fill insulation. Partially buried ducts have insulation that does not cover the top of the ducts. Fully buried ducts have insulation that just covers the top of the ducts. Deeply buried ducts have insulation that continues above the top of the ducts.",
            "Type": "Choice",
            "Choices": [
                "not buried",
                "partially buried",
                "fully buried",
                "deeply buried"
            ],
            "Required": "false"
        },
        "ducts_return_surface_area" : {
            "Name": "ducts_return_surface_area",
            "Display Name": "Ducts: Return Surface Area",
            "Description": "The return ducts surface area in the given location. If neither Surface Area nor Area Fraction provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Double",
            "Units": "ft^2",
            "Required": "false"
        },
        "ducts_return_surface_area_fraction" : {
            "Name": "ducts_return_surface_area_fraction",
            "Display Name": "Ducts: Return Area Fraction",
            "Description": "The fraction of return ducts surface area in the given location. Only used if Surface Area is not provided. If the fraction is less than 1, the remaining duct area is assumed to be in conditioned space. If neither Surface Area nor Area Fraction provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Double",
            "Units": "frac",
            "Required": "false"
        },
        "ducts_number_of_return_registers" : {
            "Name": "ducts_number_of_return_registers",
            "Display Name": "Ducts: Number of Return Registers",
            "Description": "The number of return registers of the ducts. Only used to calculate default return duct surface area. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "ducts_return_fraction_rectangular" : {
            "Name": "ducts_return_fraction_rectangular",
            "Display Name": "Ducts: Return Fraction Rectangular",
            "Description": "The fraction of return ducts that are rectangular (as opposed to round); this affects the duct effective R-value used for modeling. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Double",
            "Units": "frac",
            "Required": "false"
        },
        "mech_vent_fan_type" : {
            "Name": "mech_vent_fan_type",
            "Display Name": "Mechanical Ventilation: Fan Type",
            "Description": "The type of the mechanical ventilation. Use 'none' if there is no mechanical ventilation system.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "exhaust only",
                "supply only",
                "energy recovery ventilator",
                "heat recovery ventilator",
                "balanced",
                "central fan integrated supply"
            ],
            "Required": "true"
        },
        "mech_vent_flow_rate" : {
            "Name": "mech_vent_flow_rate",
            "Display Name": "Mechanical Ventilation: Flow Rate",
            "Description": "The flow rate of the mechanical ventilation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-mechanical-ventilation-fans'>HPXML Mechanical Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "CFM",
            "Required": "false"
        },
        "mech_vent_hours_in_operation" : {
            "Name": "mech_vent_hours_in_operation",
            "Display Name": "Mechanical Ventilation: Hours In Operation",
            "Description": "The hours in operation of the mechanical ventilation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-mechanical-ventilation-fans'>HPXML Mechanical Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "hrs/day",
            "Required": "false"
        },
        "mech_vent_recovery_efficiency_type" : {
            "Name": "mech_vent_recovery_efficiency_type",
            "Display Name": "Mechanical Ventilation: Total Recovery Efficiency Type",
            "Description": "The total recovery efficiency type of the mechanical ventilation.",
            "Type": "Choice",
            "Default Value": "Unadjusted",
            "Choices": [
                "Unadjusted",
                "Adjusted"
            ],
            "Required": "true"
        },
        "mech_vent_total_recovery_efficiency" : {
            "Name": "mech_vent_total_recovery_efficiency",
            "Display Name": "Mechanical Ventilation: Total Recovery Efficiency",
            "Description": "The Unadjusted or Adjusted total recovery efficiency of the mechanical ventilation. Applies to energy recovery ventilator.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.48",
            "Required": "true"
        },
        "mech_vent_sensible_recovery_efficiency" : {
            "Name": "mech_vent_sensible_recovery_efficiency",
            "Display Name": "Mechanical Ventilation: Sensible Recovery Efficiency",
            "Description": "The Unadjusted or Adjusted sensible recovery efficiency of the mechanical ventilation. Applies to energy recovery ventilator and heat recovery ventilator.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.72",
            "Required": "true"
        },
        "mech_vent_fan_power" : {
            "Name": "mech_vent_fan_power",
            "Display Name": "Mechanical Ventilation: Fan Power",
            "Description": "The fan power of the mechanical ventilation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-mechanical-ventilation-fans'>HPXML Mechanical Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "mech_vent_num_units_served" : {
            "Name": "mech_vent_num_units_served",
            "Display Name": "Mechanical Ventilation: Number of Units Served",
            "Description": "Number of dwelling units served by the mechanical ventilation system. Must be 1 if single-family detached. Used to apportion flow rate and fan power to the unit.",
            "Type": "Integer",
            "Units": "#",
            "Default Value": "1",
            "Required": "true"
        },
        "mech_vent_shared_frac_recirculation" : {
            "Name": "mech_vent_shared_frac_recirculation",
            "Display Name": "Shared Mechanical Ventilation: Fraction Recirculation",
            "Description": "Fraction of the total supply air that is recirculated, with the remainder assumed to be outdoor air. The value must be 0 for exhaust only systems. Required for a shared mechanical ventilation system.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "mech_vent_shared_preheating_fuel" : {
            "Name": "mech_vent_shared_preheating_fuel",
            "Display Name": "Shared Mechanical Ventilation: Preheating Fuel",
            "Description": "Fuel type of the preconditioning heating equipment. Only used for a shared mechanical ventilation system. If not provided, assumes no preheating.",
            "Type": "Choice",
            "Choices": [
                "electricity",
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "wood pellets",
                "coal"
            ],
            "Required": "false"
        },
        "mech_vent_shared_preheating_efficiency" : {
            "Name": "mech_vent_shared_preheating_efficiency",
            "Display Name": "Shared Mechanical Ventilation: Preheating Efficiency",
            "Description": "Efficiency of the preconditioning heating equipment. Only used for a shared mechanical ventilation system. If not provided, assumes no preheating.",
            "Type": "Double",
            "Units": "COP",
            "Required": "false"
        },
        "mech_vent_shared_preheating_fraction_heat_load_served" : {
            "Name": "mech_vent_shared_preheating_fraction_heat_load_served",
            "Display Name": "Shared Mechanical Ventilation: Preheating Fraction Ventilation Heat Load Served",
            "Description": "Fraction of heating load introduced by the shared ventilation system that is met by the preconditioning heating equipment. If not provided, assumes no preheating.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "mech_vent_shared_precooling_fuel" : {
            "Name": "mech_vent_shared_precooling_fuel",
            "Display Name": "Shared Mechanical Ventilation: Precooling Fuel",
            "Description": "Fuel type of the preconditioning cooling equipment. Only used for a shared mechanical ventilation system. If not provided, assumes no precooling.",
            "Type": "Choice",
            "Choices": [
                "electricity"
            ],
            "Required": "false"
        },
        "mech_vent_shared_precooling_efficiency" : {
            "Name": "mech_vent_shared_precooling_efficiency",
            "Display Name": "Shared Mechanical Ventilation: Precooling Efficiency",
            "Description": "Efficiency of the preconditioning cooling equipment. Only used for a shared mechanical ventilation system. If not provided, assumes no precooling.",
            "Type": "Double",
            "Units": "COP",
            "Required": "false"
        },
        "mech_vent_shared_precooling_fraction_cool_load_served" : {
            "Name": "mech_vent_shared_precooling_fraction_cool_load_served",
            "Display Name": "Shared Mechanical Ventilation: Precooling Fraction Ventilation Cool Load Served",
            "Description": "Fraction of cooling load introduced by the shared ventilation system that is met by the preconditioning cooling equipment. If not provided, assumes no precooling.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "mech_vent_2_fan_type" : {
            "Name": "mech_vent_2_fan_type",
            "Display Name": "Mechanical Ventilation 2: Fan Type",
            "Description": "The type of the second mechanical ventilation. Use 'none' if there is no second mechanical ventilation system.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "exhaust only",
                "supply only",
                "energy recovery ventilator",
                "heat recovery ventilator",
                "balanced"
            ],
            "Required": "true"
        },
        "mech_vent_2_flow_rate" : {
            "Name": "mech_vent_2_flow_rate",
            "Display Name": "Mechanical Ventilation 2: Flow Rate",
            "Description": "The flow rate of the second mechanical ventilation.",
            "Type": "Double",
            "Units": "CFM",
            "Default Value": "110",
            "Required": "true"
        },
        "mech_vent_2_hours_in_operation" : {
            "Name": "mech_vent_2_hours_in_operation",
            "Display Name": "Mechanical Ventilation 2: Hours In Operation",
            "Description": "The hours in operation of the second mechanical ventilation.",
            "Type": "Double",
            "Units": "hrs/day",
            "Default Value": "24",
            "Required": "true"
        },
        "mech_vent_2_recovery_efficiency_type" : {
            "Name": "mech_vent_2_recovery_efficiency_type",
            "Display Name": "Mechanical Ventilation 2: Total Recovery Efficiency Type",
            "Description": "The total recovery efficiency type of the second mechanical ventilation.",
            "Type": "Choice",
            "Default Value": "Unadjusted",
            "Choices": [
                "Unadjusted",
                "Adjusted"
            ],
            "Required": "true"
        },
        "mech_vent_2_total_recovery_efficiency" : {
            "Name": "mech_vent_2_total_recovery_efficiency",
            "Display Name": "Mechanical Ventilation 2: Total Recovery Efficiency",
            "Description": "The Unadjusted or Adjusted total recovery efficiency of the second mechanical ventilation. Applies to energy recovery ventilator.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.48",
            "Required": "true"
        },
        "mech_vent_2_sensible_recovery_efficiency" : {
            "Name": "mech_vent_2_sensible_recovery_efficiency",
            "Display Name": "Mechanical Ventilation 2: Sensible Recovery Efficiency",
            "Description": "The Unadjusted or Adjusted sensible recovery efficiency of the second mechanical ventilation. Applies to energy recovery ventilator and heat recovery ventilator.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.72",
            "Required": "true"
        },
        "mech_vent_2_fan_power" : {
            "Name": "mech_vent_2_fan_power",
            "Display Name": "Mechanical Ventilation 2: Fan Power",
            "Description": "The fan power of the second mechanical ventilation.",
            "Type": "Double",
            "Units": "W",
            "Default Value": "30",
            "Required": "true"
        },
        "kitchen_fans_quantity" : {
            "Name": "kitchen_fans_quantity",
            "Display Name": "Kitchen Fans: Quantity",
            "Description": "The quantity of the kitchen fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "kitchen_fans_flow_rate" : {
            "Name": "kitchen_fans_flow_rate",
            "Display Name": "Kitchen Fans: Flow Rate",
            "Description": "The flow rate of the kitchen fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "CFM",
            "Required": "false"
        },
        "kitchen_fans_hours_in_operation" : {
            "Name": "kitchen_fans_hours_in_operation",
            "Display Name": "Kitchen Fans: Hours In Operation",
            "Description": "The hours in operation of the kitchen fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "hrs/day",
            "Required": "false"
        },
        "kitchen_fans_power" : {
            "Name": "kitchen_fans_power",
            "Display Name": "Kitchen Fans: Fan Power",
            "Description": "The fan power of the kitchen fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "kitchen_fans_start_hour" : {
            "Name": "kitchen_fans_start_hour",
            "Display Name": "Kitchen Fans: Start Hour",
            "Description": "The start hour of the kitchen fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Integer",
            "Units": "hr",
            "Required": "false"
        },
        "bathroom_fans_quantity" : {
            "Name": "bathroom_fans_quantity",
            "Display Name": "Bathroom Fans: Quantity",
            "Description": "The quantity of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "bathroom_fans_flow_rate" : {
            "Name": "bathroom_fans_flow_rate",
            "Display Name": "Bathroom Fans: Flow Rate",
            "Description": "The flow rate of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "CFM",
            "Required": "false"
        },
        "bathroom_fans_hours_in_operation" : {
            "Name": "bathroom_fans_hours_in_operation",
            "Display Name": "Bathroom Fans: Hours In Operation",
            "Description": "The hours in operation of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "hrs/day",
            "Required": "false"
        },
        "bathroom_fans_power" : {
            "Name": "bathroom_fans_power",
            "Display Name": "Bathroom Fans: Fan Power",
            "Description": "The fan power of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "bathroom_fans_start_hour" : {
            "Name": "bathroom_fans_start_hour",
            "Display Name": "Bathroom Fans: Start Hour",
            "Description": "The start hour of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-local-ventilation-fans'>HPXML Local Ventilation Fans</a>) is used.",
            "Type": "Integer",
            "Units": "hr",
            "Required": "false"
        },
        "whole_house_fan_present" : {
            "Name": "whole_house_fan_present",
            "Display Name": "Whole House Fan: Present",
            "Description": "Whether there is a whole house fan.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "whole_house_fan_flow_rate" : {
            "Name": "whole_house_fan_flow_rate",
            "Display Name": "Whole House Fan: Flow Rate",
            "Description": "The flow rate of the whole house fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-whole-house-fans'>HPXML Whole House Fans</a>) is used.",
            "Type": "Double",
            "Units": "CFM",
            "Required": "false"
        },
        "whole_house_fan_power" : {
            "Name": "whole_house_fan_power",
            "Display Name": "Whole House Fan: Fan Power",
            "Description": "The fan power of the whole house fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-whole-house-fans'>HPXML Whole House Fans</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "water_heater_type" : {
            "Name": "water_heater_type",
            "Display Name": "Water Heater: Type",
            "Description": "The type of water heater. Use 'none' if there is no water heater.",
            "Type": "Choice",
            "Default Value": "storage water heater",
            "Choices": [
                "none",
                "storage water heater",
                "instantaneous water heater",
                "heat pump water heater",
                "space-heating boiler with storage tank",
                "space-heating boiler with tankless coil"
            ],
            "Required": "true"
        },
        "water_heater_fuel_type" : {
            "Name": "water_heater_fuel_type",
            "Display Name": "Water Heater: Fuel Type",
            "Description": "The fuel type of water heater. Ignored for heat pump water heater.",
            "Type": "Choice",
            "Default Value": "natural gas",
            "Choices": [
                "electricity",
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "coal"
            ],
            "Required": "true"
        },
        "water_heater_location" : {
            "Name": "water_heater_location",
            "Display Name": "Water Heater: Location",
            "Description": "The location of water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-water-heating-systems'>HPXML Water Heating Systems</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "garage",
                "attic",
                "attic - vented",
                "attic - unvented",
                "crawlspace",
                "crawlspace - vented",
                "crawlspace - unvented",
                "crawlspace - conditioned",
                "other exterior",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space"
            ],
            "Required": "false"
        },
        "water_heater_tank_volume" : {
            "Name": "water_heater_tank_volume",
            "Display Name": "Water Heater: Tank Volume",
            "Description": "Nominal volume of water heater tank. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#heat-pump'>Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#combi-boiler-w-storage'>Combi Boiler w/ Storage</a>) is used.",
            "Type": "Double",
            "Units": "gal",
            "Required": "false"
        },
        "water_heater_efficiency_type" : {
            "Name": "water_heater_efficiency_type",
            "Display Name": "Water Heater: Efficiency Type",
            "Description": "The efficiency type of water heater. Does not apply to space-heating boilers.",
            "Type": "Choice",
            "Default Value": "EnergyFactor",
            "Choices": [
                "EnergyFactor",
                "UniformEnergyFactor"
            ],
            "Required": "true"
        },
        "water_heater_efficiency" : {
            "Name": "water_heater_efficiency",
            "Display Name": "Water Heater: Efficiency",
            "Description": "Rated Energy Factor or Uniform Energy Factor. Does not apply to space-heating boilers.",
            "Type": "Double",
            "Default Value": "0.67",
            "Required": "true"
        },
        "water_heater_usage_bin" : {
            "Name": "water_heater_usage_bin",
            "Display Name": "Water Heater: Usage Bin",
            "Description": "The usage of the water heater. Only applies if Efficiency Type is UniformEnergyFactor and Type is not instantaneous water heater. Does not apply to space-heating boilers. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#heat-pump'>Heat Pump</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "very small",
                "low",
                "medium",
                "high"
            ],
            "Required": "false"
        },
        "water_heater_recovery_efficiency" : {
            "Name": "water_heater_recovery_efficiency",
            "Display Name": "Water Heater: Recovery Efficiency",
            "Description": "Ratio of energy delivered to water heater to the energy content of the fuel consumed by the water heater. Only used for non-electric storage water heaters. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "water_heater_heating_capacity" : {
            "Name": "water_heater_heating_capacity",
            "Display Name": "Water Heater: Heating Capacity",
            "Description": "Heating capacity. Only applies to storage water heater and heat pump water heater (compressor). If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#heat-pump'>Heat Pump</a>) is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "water_heater_backup_heating_capacity" : {
            "Name": "water_heater_backup_heating_capacity",
            "Display Name": "Water Heater: Backup Heating Capacity",
            "Description": "Backup heating capacity for a heat pump water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#heat-pump'>Heat Pump</a>) is used.",
            "Type": "Double",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "water_heater_standby_loss" : {
            "Name": "water_heater_standby_loss",
            "Display Name": "Water Heater: Standby Loss",
            "Description": "The standby loss of water heater. Only applies to space-heating boilers. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#combi-boiler-w-storage'>Combi Boiler w/ Storage</a>) is used.",
            "Type": "Double",
            "Units": "F/hr",
            "Required": "false"
        },
        "water_heater_jacket_rvalue" : {
            "Name": "water_heater_jacket_rvalue",
            "Display Name": "Water Heater: Jacket R-value",
            "Description": "The jacket R-value of water heater. Doesn't apply to instantaneous water heater or space-heating boiler with tankless coil. If not provided, defaults to no jacket insulation.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "water_heater_setpoint_temperature" : {
            "Name": "water_heater_setpoint_temperature",
            "Display Name": "Water Heater: Setpoint Temperature",
            "Description": "The setpoint temperature of water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-water-heating-systems'>HPXML Water Heating Systems</a>) is used.",
            "Type": "Double",
            "Units": "F",
            "Required": "false"
        },
        "water_heater_num_bedrooms_served" : {
            "Name": "water_heater_num_bedrooms_served",
            "Display Name": "Water Heater: Number of Bedrooms Served",
            "Description": "Number of bedrooms served (directly or indirectly) by the water heater. Only needed if single-family attached or apartment unit and it is a shared water heater serving multiple dwelling units. Used to apportion water heater tank losses to the unit.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "water_heater_uses_desuperheater" : {
            "Name": "water_heater_uses_desuperheater",
            "Display Name": "Water Heater: Uses Desuperheater",
            "Description": "Requires that the dwelling unit has a air-to-air, mini-split, or ground-to-air heat pump or a central air conditioner or mini-split air conditioner. If not provided, assumes no desuperheater.",
            "Type": "Boolean",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "water_heater_tank_model_type" : {
            "Name": "water_heater_tank_model_type",
            "Display Name": "Water Heater: Tank Type",
            "Description": "Type of tank model to use. The 'stratified' tank generally provide more accurate results, but may significantly increase run time. Applies only to storage water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "mixed",
                "stratified"
            ],
            "Required": "false"
        },
        "water_heater_operating_mode" : {
            "Name": "water_heater_operating_mode",
            "Display Name": "Water Heater: Operating Mode",
            "Description": "The water heater operating mode. The 'heat pump only' option only uses the heat pump, while 'hybrid/auto' allows the backup electric resistance to come on in high demand situations. This is ignored if a scheduled operating mode type is selected. Applies only to heat pump water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#heat-pump'>Heat Pump</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "hybrid/auto",
                "heat pump only"
            ],
            "Required": "false"
        },
        "hot_water_distribution_system_type" : {
            "Name": "hot_water_distribution_system_type",
            "Display Name": "Hot Water Distribution: System Type",
            "Description": "The type of the hot water distribution system.",
            "Type": "Choice",
            "Default Value": "Standard",
            "Choices": [
                "Standard",
                "Recirculation"
            ],
            "Required": "true"
        },
        "hot_water_distribution_standard_piping_length" : {
            "Name": "hot_water_distribution_standard_piping_length",
            "Display Name": "Hot Water Distribution: Standard Piping Length",
            "Description": "If the distribution system is Standard, the length of the piping. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#standard'>Standard</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "hot_water_distribution_recirc_control_type" : {
            "Name": "hot_water_distribution_recirc_control_type",
            "Display Name": "Hot Water Distribution: Recirculation Control Type",
            "Description": "If the distribution system is Recirculation, the type of hot water recirculation control, if any.",
            "Type": "Choice",
            "Default Value": "no control",
            "Choices": [
                "no control",
                "timer",
                "temperature",
                "presence sensor demand control",
                "manual demand control"
            ],
            "Required": "false"
        },
        "hot_water_distribution_recirc_piping_length" : {
            "Name": "hot_water_distribution_recirc_piping_length",
            "Display Name": "Hot Water Distribution: Recirculation Piping Length",
            "Description": "If the distribution system is Recirculation, the length of the recirculation piping. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#recirculation-in-unit'>Recirculation (In-Unit)</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "hot_water_distribution_recirc_branch_piping_length" : {
            "Name": "hot_water_distribution_recirc_branch_piping_length",
            "Display Name": "Hot Water Distribution: Recirculation Branch Piping Length",
            "Description": "If the distribution system is Recirculation, the length of the recirculation branch piping. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#recirculation-in-unit'>Recirculation (In-Unit)</a>) is used.",
            "Type": "Double",
            "Units": "ft",
            "Required": "false"
        },
        "hot_water_distribution_recirc_pump_power" : {
            "Name": "hot_water_distribution_recirc_pump_power",
            "Display Name": "Hot Water Distribution: Recirculation Pump Power",
            "Description": "If the distribution system is Recirculation, the recirculation pump power. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#recirculation-in-unit'>Recirculation (In-Unit)</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "hot_water_distribution_pipe_r" : {
            "Name": "hot_water_distribution_pipe_r",
            "Display Name": "Hot Water Distribution: Pipe Insulation Nominal R-Value",
            "Description": "Nominal R-value of the pipe insulation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-hot-water-distribution'>HPXML Hot Water Distribution</a>) is used.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "dwhr_facilities_connected" : {
            "Name": "dwhr_facilities_connected",
            "Display Name": "Drain Water Heat Recovery: Facilities Connected",
            "Description": "Which facilities are connected for the drain water heat recovery. Use 'none' if there is no drain water heat recovery system.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "one",
                "all"
            ],
            "Required": "true"
        },
        "dwhr_equal_flow" : {
            "Name": "dwhr_equal_flow",
            "Display Name": "Drain Water Heat Recovery: Equal Flow",
            "Description": "Whether the drain water heat recovery has equal flow.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "dwhr_efficiency" : {
            "Name": "dwhr_efficiency",
            "Display Name": "Drain Water Heat Recovery: Efficiency",
            "Description": "The efficiency of the drain water heat recovery.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.55",
            "Required": "false"
        },
        "water_fixtures_shower_low_flow" : {
            "Name": "water_fixtures_shower_low_flow",
            "Display Name": "Hot Water Fixtures: Is Shower Low Flow",
            "Description": "Whether the shower fixture is low flow.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "water_fixtures_sink_low_flow" : {
            "Name": "water_fixtures_sink_low_flow",
            "Display Name": "Hot Water Fixtures: Is Sink Low Flow",
            "Description": "Whether the sink fixture is low flow.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "water_fixtures_usage_multiplier" : {
            "Name": "water_fixtures_usage_multiplier",
            "Display Name": "Hot Water Fixtures: Usage Multiplier",
            "Description": "Multiplier on the hot water usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-water-fixtures'>HPXML Water Fixtures</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "general_water_use_usage_multiplier" : {
            "Name": "general_water_use_usage_multiplier",
            "Display Name": "General Water Use: Usage Multiplier",
            "Description": "Multiplier on internal gains from general water use (floor mopping, shower evaporation, water films on showers, tubs & sinks surfaces, plant watering, etc.) that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-building-occupancy'>HPXML Building Occupancy</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "solar_thermal_system_type" : {
            "Name": "solar_thermal_system_type",
            "Display Name": "Solar Thermal: System Type",
            "Description": "The type of solar thermal system. Use 'none' if there is no solar thermal system.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "hot water"
            ],
            "Required": "true"
        },
        "solar_thermal_collector_area" : {
            "Name": "solar_thermal_collector_area",
            "Display Name": "Solar Thermal: Collector Area",
            "Description": "The collector area of the solar thermal system.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "40",
            "Required": "true"
        },
        "solar_thermal_collector_loop_type" : {
            "Name": "solar_thermal_collector_loop_type",
            "Display Name": "Solar Thermal: Collector Loop Type",
            "Description": "The collector loop type of the solar thermal system.",
            "Type": "Choice",
            "Default Value": "liquid direct",
            "Choices": [
                "liquid direct",
                "liquid indirect",
                "passive thermosyphon"
            ],
            "Required": "true"
        },
        "solar_thermal_collector_type" : {
            "Name": "solar_thermal_collector_type",
            "Display Name": "Solar Thermal: Collector Type",
            "Description": "The collector type of the solar thermal system.",
            "Type": "Choice",
            "Default Value": "evacuated tube",
            "Choices": [
                "evacuated tube",
                "single glazing black",
                "double glazing black",
                "integrated collector storage"
            ],
            "Required": "true"
        },
        "solar_thermal_collector_azimuth" : {
            "Name": "solar_thermal_collector_azimuth",
            "Display Name": "Solar Thermal: Collector Azimuth",
            "Description": "The collector azimuth of the solar thermal system. Azimuth is measured clockwise from north (e.g., North=0, East=90, South=180, West=270).",
            "Type": "Double",
            "Units": "degrees",
            "Default Value": "180",
            "Required": "true"
        },
        "solar_thermal_collector_tilt" : {
            "Name": "solar_thermal_collector_tilt",
            "Display Name": "Solar Thermal: Collector Tilt",
            "Description": "The collector tilt of the solar thermal system. Can also enter, e.g., RoofPitch, RoofPitch+20, Latitude, Latitude-15, etc.",
            "Type": "String",
            "Units": "degrees",
            "Default Value": "RoofPitch",
            "Required": "true"
        },
        "solar_thermal_collector_rated_optical_efficiency" : {
            "Name": "solar_thermal_collector_rated_optical_efficiency",
            "Display Name": "Solar Thermal: Collector Rated Optical Efficiency",
            "Description": "The collector rated optical efficiency of the solar thermal system.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.5",
            "Required": "true"
        },
        "solar_thermal_collector_rated_thermal_losses" : {
            "Name": "solar_thermal_collector_rated_thermal_losses",
            "Display Name": "Solar Thermal: Collector Rated Thermal Losses",
            "Description": "The collector rated thermal losses of the solar thermal system.",
            "Type": "Double",
            "Units": "Btu/hr-ft^2-R",
            "Default Value": "0.2799",
            "Required": "true"
        },
        "solar_thermal_storage_volume" : {
            "Name": "solar_thermal_storage_volume",
            "Display Name": "Solar Thermal: Storage Volume",
            "Description": "The storage volume of the solar thermal system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#detailed-inputs'>Detailed Inputs</a>) is used.",
            "Type": "Double",
            "Units": "gal",
            "Required": "false"
        },
        "solar_thermal_solar_fraction" : {
            "Name": "solar_thermal_solar_fraction",
            "Display Name": "Solar Thermal: Solar Fraction",
            "Description": "The solar fraction of the solar thermal system. If provided, overrides all other solar thermal inputs.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0",
            "Required": "true"
        },
        "pv_system_present" : {
            "Name": "pv_system_present",
            "Display Name": "PV System: Present",
            "Description": "Whether there is a PV system present.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "pv_system_module_type" : {
            "Name": "pv_system_module_type",
            "Display Name": "PV System: Module Type",
            "Description": "Module type of the PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "standard",
                "premium",
                "thin film"
            ],
            "Required": "false"
        },
        "pv_system_location" : {
            "Name": "pv_system_location",
            "Display Name": "PV System: Location",
            "Description": "Location of the PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "roof",
                "ground"
            ],
            "Required": "false"
        },
        "pv_system_tracking" : {
            "Name": "pv_system_tracking",
            "Display Name": "PV System: Tracking",
            "Description": "Type of tracking for the PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "fixed",
                "1-axis",
                "1-axis backtracked",
                "2-axis"
            ],
            "Required": "false"
        },
        "pv_system_array_azimuth" : {
            "Name": "pv_system_array_azimuth",
            "Display Name": "PV System: Array Azimuth",
            "Description": "Array azimuth of the PV system. Azimuth is measured clockwise from north (e.g., North=0, East=90, South=180, West=270).",
            "Type": "Double",
            "Units": "degrees",
            "Default Value": "180",
            "Required": "true"
        },
        "pv_system_array_tilt" : {
            "Name": "pv_system_array_tilt",
            "Display Name": "PV System: Array Tilt",
            "Description": "Array tilt of the PV system. Can also enter, e.g., RoofPitch, RoofPitch+20, Latitude, Latitude-15, etc.",
            "Type": "String",
            "Units": "degrees",
            "Default Value": "RoofPitch",
            "Required": "true"
        },
        "pv_system_max_power_output" : {
            "Name": "pv_system_max_power_output",
            "Display Name": "PV System: Maximum Power Output",
            "Description": "Maximum power output of the PV system. For a shared system, this is the total building maximum power output.",
            "Type": "Double",
            "Units": "W",
            "Default Value": "4000",
            "Required": "true"
        },
        "pv_system_inverter_efficiency" : {
            "Name": "pv_system_inverter_efficiency",
            "Display Name": "PV System: Inverter Efficiency",
            "Description": "Inverter efficiency of the PV system. If there are two PV systems, this will apply to both. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "pv_system_system_losses_fraction" : {
            "Name": "pv_system_system_losses_fraction",
            "Display Name": "PV System: System Losses Fraction",
            "Description": "System losses fraction of the PV system. If there are two PV systems, this will apply to both. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "pv_system_num_bedrooms_served" : {
            "Name": "pv_system_num_bedrooms_served",
            "Display Name": "PV System: Number of Bedrooms Served",
            "Description": "Number of bedrooms served by PV system. Only needed if single-family attached or apartment unit and it is a shared PV system serving multiple dwelling units. Used to apportion PV generation to the unit of a SFA/MF building. If there are two PV systems, this will apply to both.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "pv_system_2_present" : {
            "Name": "pv_system_2_present",
            "Display Name": "PV System 2: Present",
            "Description": "Whether there is a second PV system present.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "pv_system_2_module_type" : {
            "Name": "pv_system_2_module_type",
            "Display Name": "PV System 2: Module Type",
            "Description": "Module type of the second PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "standard",
                "premium",
                "thin film"
            ],
            "Required": "false"
        },
        "pv_system_2_location" : {
            "Name": "pv_system_2_location",
            "Display Name": "PV System 2: Location",
            "Description": "Location of the second PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "roof",
                "ground"
            ],
            "Required": "false"
        },
        "pv_system_2_tracking" : {
            "Name": "pv_system_2_tracking",
            "Display Name": "PV System 2: Tracking",
            "Description": "Type of tracking for the second PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "fixed",
                "1-axis",
                "1-axis backtracked",
                "2-axis"
            ],
            "Required": "false"
        },
        "pv_system_2_array_azimuth" : {
            "Name": "pv_system_2_array_azimuth",
            "Display Name": "PV System 2: Array Azimuth",
            "Description": "Array azimuth of the second PV system. Azimuth is measured clockwise from north (e.g., North=0, East=90, South=180, West=270).",
            "Type": "Double",
            "Units": "degrees",
            "Default Value": "180",
            "Required": "true"
        },
        "pv_system_2_array_tilt" : {
            "Name": "pv_system_2_array_tilt",
            "Display Name": "PV System 2: Array Tilt",
            "Description": "Array tilt of the second PV system. Can also enter, e.g., RoofPitch, RoofPitch+20, Latitude, Latitude-15, etc.",
            "Type": "String",
            "Units": "degrees",
            "Default Value": "RoofPitch",
            "Required": "true"
        },
        "pv_system_2_max_power_output" : {
            "Name": "pv_system_2_max_power_output",
            "Display Name": "PV System 2: Maximum Power Output",
            "Description": "Maximum power output of the second PV system. For a shared system, this is the total building maximum power output.",
            "Type": "Double",
            "Units": "W",
            "Default Value": "4000",
            "Required": "true"
        },
        "battery_present" : {
            "Name": "battery_present",
            "Display Name": "Battery: Present",
            "Description": "Whether there is a lithium ion battery present.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "battery_location" : {
            "Name": "battery_location",
            "Display Name": "Battery: Location",
            "Description": "The space type for the lithium ion battery location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "crawlspace",
                "crawlspace - vented",
                "crawlspace - unvented",
                "crawlspace - conditioned",
                "attic",
                "attic - vented",
                "attic - unvented",
                "garage",
                "outside"
            ],
            "Required": "false"
        },
        "battery_power" : {
            "Name": "battery_power",
            "Display Name": "Battery: Rated Power Output",
            "Description": "The rated power output of the lithium ion battery. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "battery_capacity" : {
            "Name": "battery_capacity",
            "Display Name": "Battery: Nominal Capacity",
            "Description": "The nominal capacity of the lithium ion battery. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "Double",
            "Units": "kWh",
            "Required": "false"
        },
        "battery_usable_capacity" : {
            "Name": "battery_usable_capacity",
            "Display Name": "Battery: Usable Capacity",
            "Description": "The usable capacity of the lithium ion battery. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "Double",
            "Units": "kWh",
            "Required": "false"
        },
        "battery_round_trip_efficiency" : {
            "Name": "battery_round_trip_efficiency",
            "Display Name": "Battery: Round Trip Efficiency",
            "Description": "The round trip efficiency of the lithium ion battery. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "battery_num_bedrooms_served" : {
            "Name": "battery_num_bedrooms_served",
            "Display Name": "Battery: Number of Bedrooms Served",
            "Description": "Number of bedrooms served by the lithium ion battery. Only needed if single-family attached or apartment unit and it is a shared battery serving multiple dwelling units. Used to apportion battery charging/discharging to the unit of a SFA/MF building.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "vehicle_type" : {
            "Name": "vehicle_type",
            "Display Name": "Vehicle: Type",
            "Description": "The type of vehicle present at the home.",
            "Type": "String",
            "Default Value": "none",
            "Required": "false"
        },
        "vehicle_battery_capacity" : {
            "Name": "vehicle_battery_capacity",
            "Display Name": "Vehicle: EV Battery Nominal Battery Capacity",
            "Description": "The nominal capacity of the vehicle battery, only applies to electric vehicles. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-vehicles'>HPXML Vehicles</a>) is used.",
            "Type": "Double",
            "Units": "kWh",
            "Required": "false"
        },
        "vehicle_battery_usable_capacity" : {
            "Name": "vehicle_battery_usable_capacity",
            "Display Name": "Vehicle: EV Battery Usable Capacity",
            "Description": "The usable capacity of the vehicle battery, only applies to electric vehicles. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-vehicles'>HPXML Vehicles</a>) is used.",
            "Type": "Double",
            "Units": "kWh",
            "Required": "false"
        },
        "vehicle_fuel_economy_units" : {
            "Name": "vehicle_fuel_economy_units",
            "Display Name": "Vehicle: Combined Fuel Economy Units",
            "Description": "The combined fuel economy units of the vehicle. Only 'kWh/mile', 'mile/kWh', or 'mpge' are allow for electric vehicles. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-vehicles'>HPXML Vehicles</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "kWh/mile",
                "mile/kWh",
                "mpge",
                "mpg"
            ],
            "Required": "false"
        },
        "vehicle_fuel_economy_combined" : {
            "Name": "vehicle_fuel_economy_combined",
            "Display Name": "Vehicle: Combined Fuel Economy",
            "Description": "The combined fuel economy of the vehicle. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-vehicles'>HPXML Vehicles</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "vehicle_miles_driven_per_year" : {
            "Name": "vehicle_miles_driven_per_year",
            "Display Name": "Vehicle: Miles Driven Per Year",
            "Description": "The annual miles the vehicle is driven. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-vehicles'>HPXML Vehicles</a>) is used.",
            "Type": "Double",
            "Units": "miles",
            "Required": "false"
        },
        "vehicle_hours_driven_per_week" : {
            "Name": "vehicle_hours_driven_per_week",
            "Display Name": "Vehicle: Hours Driven Per Week",
            "Description": "The weekly hours the vehicle is driven. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-vehicles'>HPXML Vehicles</a>) is used.",
            "Type": "Double",
            "Units": "hours",
            "Required": "false"
        },
        "vehicle_fraction_charged_home" : {
            "Name": "vehicle_fraction_charged_home",
            "Display Name": "Vehicle: Fraction Charged at Home",
            "Description": "The fraction of charging energy provided by the at-home charger to the vehicle, only applies to electric vehicles. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-vehicles'>HPXML Vehicles</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "ev_charger_present" : {
            "Name": "ev_charger_present",
            "Display Name": "Electric Vehicle Charger: Present",
            "Description": "Whether there is an electric vehicle charger present.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "ev_charger_level" : {
            "Name": "ev_charger_level",
            "Display Name": "Electric Vehicle Charger: Charging Level",
            "Description": "The charging level of the EV charger. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-electric-vehicle-chargers'>HPXML Electric Vehicle Chargers</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "1",
                "2",
                "3"
            ],
            "Required": "false"
        },
        "ev_charger_power" : {
            "Name": "ev_charger_power",
            "Display Name": "Electric Vehicle Charger: Rated Charging Power",
            "Description": "The rated power output of the EV charger. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-electric-vehicle-chargers'>HPXML Electric Vehicle Chargers</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "lighting_present" : {
            "Name": "lighting_present",
            "Display Name": "Lighting: Present",
            "Description": "Whether there is lighting energy use.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "lighting_interior_fraction_cfl" : {
            "Name": "lighting_interior_fraction_cfl",
            "Display Name": "Lighting: Interior Fraction CFL",
            "Description": "Fraction of all lamps (interior) that are compact fluorescent. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0.1",
            "Required": "true"
        },
        "lighting_interior_fraction_lfl" : {
            "Name": "lighting_interior_fraction_lfl",
            "Display Name": "Lighting: Interior Fraction LFL",
            "Description": "Fraction of all lamps (interior) that are linear fluorescent. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "lighting_interior_fraction_led" : {
            "Name": "lighting_interior_fraction_led",
            "Display Name": "Lighting: Interior Fraction LED",
            "Description": "Fraction of all lamps (interior) that are light emitting diodes. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "lighting_interior_usage_multiplier" : {
            "Name": "lighting_interior_usage_multiplier",
            "Display Name": "Lighting: Interior Usage Multiplier",
            "Description": "Multiplier on the lighting energy usage (interior) that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "lighting_exterior_fraction_cfl" : {
            "Name": "lighting_exterior_fraction_cfl",
            "Display Name": "Lighting: Exterior Fraction CFL",
            "Description": "Fraction of all lamps (exterior) that are compact fluorescent. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "lighting_exterior_fraction_lfl" : {
            "Name": "lighting_exterior_fraction_lfl",
            "Display Name": "Lighting: Exterior Fraction LFL",
            "Description": "Fraction of all lamps (exterior) that are linear fluorescent. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "lighting_exterior_fraction_led" : {
            "Name": "lighting_exterior_fraction_led",
            "Display Name": "Lighting: Exterior Fraction LED",
            "Description": "Fraction of all lamps (exterior) that are light emitting diodes. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "lighting_exterior_usage_multiplier" : {
            "Name": "lighting_exterior_usage_multiplier",
            "Display Name": "Lighting: Exterior Usage Multiplier",
            "Description": "Multiplier on the lighting energy usage (exterior) that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "lighting_garage_fraction_cfl" : {
            "Name": "lighting_garage_fraction_cfl",
            "Display Name": "Lighting: Garage Fraction CFL",
            "Description": "Fraction of all lamps (garage) that are compact fluorescent. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "lighting_garage_fraction_lfl" : {
            "Name": "lighting_garage_fraction_lfl",
            "Display Name": "Lighting: Garage Fraction LFL",
            "Description": "Fraction of all lamps (garage) that are linear fluorescent. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "lighting_garage_fraction_led" : {
            "Name": "lighting_garage_fraction_led",
            "Display Name": "Lighting: Garage Fraction LED",
            "Description": "Fraction of all lamps (garage) that are light emitting diodes. Lighting not specified as CFL, LFL, or LED is assumed to be incandescent.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "lighting_garage_usage_multiplier" : {
            "Name": "lighting_garage_usage_multiplier",
            "Display Name": "Lighting: Garage Usage Multiplier",
            "Description": "Multiplier on the lighting energy usage (garage) that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "holiday_lighting_present" : {
            "Name": "holiday_lighting_present",
            "Display Name": "Holiday Lighting: Present",
            "Description": "Whether there is holiday lighting.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "holiday_lighting_daily_kwh" : {
            "Name": "holiday_lighting_daily_kwh",
            "Display Name": "Holiday Lighting: Daily Consumption",
            "Description": "The daily energy consumption for holiday lighting (exterior). If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "Double",
            "Units": "kWh/day",
            "Required": "false"
        },
        "holiday_lighting_period" : {
            "Name": "holiday_lighting_period",
            "Display Name": "Holiday Lighting: Period",
            "Description": "Enter a date range like 'Nov 25 - Jan 5'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "String",
            "Required": "false"
        },
        "dehumidifier_type" : {
            "Name": "dehumidifier_type",
            "Display Name": "Dehumidifier: Type",
            "Description": "The type of dehumidifier.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "portable",
                "whole-home"
            ],
            "Required": "true"
        },
        "dehumidifier_efficiency_type" : {
            "Name": "dehumidifier_efficiency_type",
            "Display Name": "Dehumidifier: Efficiency Type",
            "Description": "The efficiency type of dehumidifier.",
            "Type": "Choice",
            "Default Value": "IntegratedEnergyFactor",
            "Choices": [
                "EnergyFactor",
                "IntegratedEnergyFactor"
            ],
            "Required": "true"
        },
        "dehumidifier_efficiency" : {
            "Name": "dehumidifier_efficiency",
            "Display Name": "Dehumidifier: Efficiency",
            "Description": "The efficiency of the dehumidifier.",
            "Type": "Double",
            "Units": "liters/kWh",
            "Default Value": "1.5",
            "Required": "true"
        },
        "dehumidifier_capacity" : {
            "Name": "dehumidifier_capacity",
            "Display Name": "Dehumidifier: Capacity",
            "Description": "The capacity (water removal rate) of the dehumidifier.",
            "Type": "Double",
            "Units": "pint/day",
            "Default Value": "40",
            "Required": "true"
        },
        "dehumidifier_rh_setpoint" : {
            "Name": "dehumidifier_rh_setpoint",
            "Display Name": "Dehumidifier: Relative Humidity Setpoint",
            "Description": "The relative humidity setpoint of the dehumidifier.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.5",
            "Required": "true"
        },
        "dehumidifier_fraction_dehumidification_load_served" : {
            "Name": "dehumidifier_fraction_dehumidification_load_served",
            "Display Name": "Dehumidifier: Fraction Dehumidification Load Served",
            "Description": "The dehumidification load served fraction of the dehumidifier.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "1",
            "Required": "true"
        },
        "clothes_washer_present" : {
            "Name": "clothes_washer_present",
            "Display Name": "Clothes Washer: Present",
            "Description": "Whether there is a clothes washer present.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "clothes_washer_location" : {
            "Name": "clothes_washer_location",
            "Display Name": "Clothes Washer: Location",
            "Description": "The space type for the clothes washer location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "garage",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space"
            ],
            "Required": "false"
        },
        "clothes_washer_efficiency_type" : {
            "Name": "clothes_washer_efficiency_type",
            "Display Name": "Clothes Washer: Efficiency Type",
            "Description": "The efficiency type of the clothes washer.",
            "Type": "Choice",
            "Default Value": "IntegratedModifiedEnergyFactor",
            "Choices": [
                "ModifiedEnergyFactor",
                "IntegratedModifiedEnergyFactor"
            ],
            "Required": "true"
        },
        "clothes_washer_efficiency" : {
            "Name": "clothes_washer_efficiency",
            "Display Name": "Clothes Washer: Efficiency",
            "Description": "The efficiency of the clothes washer. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Double",
            "Units": "ft^3/kWh-cyc",
            "Required": "false"
        },
        "clothes_washer_rated_annual_kwh" : {
            "Name": "clothes_washer_rated_annual_kwh",
            "Display Name": "Clothes Washer: Rated Annual Consumption",
            "Description": "The annual energy consumed by the clothes washer, as rated, obtained from the EnergyGuide label. This includes both the appliance electricity consumption and the energy required for water heating. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "clothes_washer_label_electric_rate" : {
            "Name": "clothes_washer_label_electric_rate",
            "Display Name": "Clothes Washer: Label Electric Rate",
            "Description": "The annual energy consumed by the clothes washer, as rated, obtained from the EnergyGuide label. This includes both the appliance electricity consumption and the energy required for water heating. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Double",
            "Units": "$/kWh",
            "Required": "false"
        },
        "clothes_washer_label_gas_rate" : {
            "Name": "clothes_washer_label_gas_rate",
            "Display Name": "Clothes Washer: Label Gas Rate",
            "Description": "The annual energy consumed by the clothes washer, as rated, obtained from the EnergyGuide label. This includes both the appliance electricity consumption and the energy required for water heating. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Double",
            "Units": "$/therm",
            "Required": "false"
        },
        "clothes_washer_label_annual_gas_cost" : {
            "Name": "clothes_washer_label_annual_gas_cost",
            "Display Name": "Clothes Washer: Label Annual Cost with Gas DHW",
            "Description": "The annual cost of using the system under test conditions. Input is obtained from the EnergyGuide label. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Double",
            "Units": "$",
            "Required": "false"
        },
        "clothes_washer_label_usage" : {
            "Name": "clothes_washer_label_usage",
            "Display Name": "Clothes Washer: Label Usage",
            "Description": "The clothes washer loads per week. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Double",
            "Units": "cyc/wk",
            "Required": "false"
        },
        "clothes_washer_capacity" : {
            "Name": "clothes_washer_capacity",
            "Display Name": "Clothes Washer: Drum Volume",
            "Description": "Volume of the washer drum. Obtained from the EnergyStar website or the manufacturer's literature. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Double",
            "Units": "ft^3",
            "Required": "false"
        },
        "clothes_washer_usage_multiplier" : {
            "Name": "clothes_washer_usage_multiplier",
            "Display Name": "Clothes Washer: Usage Multiplier",
            "Description": "Multiplier on the clothes washer energy and hot water usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "clothes_dryer_present" : {
            "Name": "clothes_dryer_present",
            "Display Name": "Clothes Dryer: Present",
            "Description": "Whether there is a clothes dryer present.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "clothes_dryer_location" : {
            "Name": "clothes_dryer_location",
            "Display Name": "Clothes Dryer: Location",
            "Description": "The space type for the clothes dryer location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-dryer'>HPXML Clothes Dryer</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "garage",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space"
            ],
            "Required": "false"
        },
        "clothes_dryer_fuel_type" : {
            "Name": "clothes_dryer_fuel_type",
            "Display Name": "Clothes Dryer: Fuel Type",
            "Description": "Type of fuel used by the clothes dryer.",
            "Type": "Choice",
            "Default Value": "natural gas",
            "Choices": [
                "electricity",
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "coal"
            ],
            "Required": "true"
        },
        "clothes_dryer_efficiency_type" : {
            "Name": "clothes_dryer_efficiency_type",
            "Display Name": "Clothes Dryer: Efficiency Type",
            "Description": "The efficiency type of the clothes dryer.",
            "Type": "Choice",
            "Default Value": "CombinedEnergyFactor",
            "Choices": [
                "EnergyFactor",
                "CombinedEnergyFactor"
            ],
            "Required": "true"
        },
        "clothes_dryer_efficiency" : {
            "Name": "clothes_dryer_efficiency",
            "Display Name": "Clothes Dryer: Efficiency",
            "Description": "The efficiency of the clothes dryer. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-dryer'>HPXML Clothes Dryer</a>) is used.",
            "Type": "Double",
            "Units": "lb/kWh",
            "Required": "false"
        },
        "clothes_dryer_vented_flow_rate" : {
            "Name": "clothes_dryer_vented_flow_rate",
            "Display Name": "Clothes Dryer: Vented Flow Rate",
            "Description": "The exhaust flow rate of the vented clothes dryer. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-dryer'>HPXML Clothes Dryer</a>) is used.",
            "Type": "Double",
            "Units": "CFM",
            "Required": "false"
        },
        "clothes_dryer_usage_multiplier" : {
            "Name": "clothes_dryer_usage_multiplier",
            "Display Name": "Clothes Dryer: Usage Multiplier",
            "Description": "Multiplier on the clothes dryer energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-clothes-dryer'>HPXML Clothes Dryer</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "dishwasher_present" : {
            "Name": "dishwasher_present",
            "Display Name": "Dishwasher: Present",
            "Description": "Whether there is a dishwasher present.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "dishwasher_location" : {
            "Name": "dishwasher_location",
            "Display Name": "Dishwasher: Location",
            "Description": "The space type for the dishwasher location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "garage",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space"
            ],
            "Required": "false"
        },
        "dishwasher_efficiency_type" : {
            "Name": "dishwasher_efficiency_type",
            "Display Name": "Dishwasher: Efficiency Type",
            "Description": "The efficiency type of dishwasher.",
            "Type": "Choice",
            "Default Value": "RatedAnnualkWh",
            "Choices": [
                "RatedAnnualkWh",
                "EnergyFactor"
            ],
            "Required": "true"
        },
        "dishwasher_efficiency" : {
            "Name": "dishwasher_efficiency",
            "Display Name": "Dishwasher: Efficiency",
            "Description": "The efficiency of the dishwasher. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Double",
            "Units": "RatedAnnualkWh or EnergyFactor",
            "Required": "false"
        },
        "dishwasher_label_electric_rate" : {
            "Name": "dishwasher_label_electric_rate",
            "Display Name": "Dishwasher: Label Electric Rate",
            "Description": "The label electric rate of the dishwasher. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Double",
            "Units": "$/kWh",
            "Required": "false"
        },
        "dishwasher_label_gas_rate" : {
            "Name": "dishwasher_label_gas_rate",
            "Display Name": "Dishwasher: Label Gas Rate",
            "Description": "The label gas rate of the dishwasher. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Double",
            "Units": "$/therm",
            "Required": "false"
        },
        "dishwasher_label_annual_gas_cost" : {
            "Name": "dishwasher_label_annual_gas_cost",
            "Display Name": "Dishwasher: Label Annual Gas Cost",
            "Description": "The label annual gas cost of the dishwasher. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Double",
            "Units": "$",
            "Required": "false"
        },
        "dishwasher_label_usage" : {
            "Name": "dishwasher_label_usage",
            "Display Name": "Dishwasher: Label Usage",
            "Description": "The dishwasher loads per week. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Double",
            "Units": "cyc/wk",
            "Required": "false"
        },
        "dishwasher_place_setting_capacity" : {
            "Name": "dishwasher_place_setting_capacity",
            "Display Name": "Dishwasher: Number of Place Settings",
            "Description": "The number of place settings for the unit. Data obtained from manufacturer's literature. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "dishwasher_usage_multiplier" : {
            "Name": "dishwasher_usage_multiplier",
            "Display Name": "Dishwasher: Usage Multiplier",
            "Description": "Multiplier on the dishwasher energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "refrigerator_present" : {
            "Name": "refrigerator_present",
            "Display Name": "Refrigerator: Present",
            "Description": "Whether there is a refrigerator present.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "refrigerator_location" : {
            "Name": "refrigerator_location",
            "Display Name": "Refrigerator: Location",
            "Description": "The space type for the refrigerator location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "garage",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space"
            ],
            "Required": "false"
        },
        "refrigerator_rated_annual_kwh" : {
            "Name": "refrigerator_rated_annual_kwh",
            "Display Name": "Refrigerator: Rated Annual Consumption",
            "Description": "The EnergyGuide rated annual energy consumption for a refrigerator. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "refrigerator_usage_multiplier" : {
            "Name": "refrigerator_usage_multiplier",
            "Display Name": "Refrigerator: Usage Multiplier",
            "Description": "Multiplier on the refrigerator energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "extra_refrigerator_present" : {
            "Name": "extra_refrigerator_present",
            "Display Name": "Extra Refrigerator: Present",
            "Description": "Whether there is an extra refrigerator present.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "extra_refrigerator_location" : {
            "Name": "extra_refrigerator_location",
            "Display Name": "Extra Refrigerator: Location",
            "Description": "The space type for the extra refrigerator location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "garage",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space"
            ],
            "Required": "false"
        },
        "extra_refrigerator_rated_annual_kwh" : {
            "Name": "extra_refrigerator_rated_annual_kwh",
            "Display Name": "Extra Refrigerator: Rated Annual Consumption",
            "Description": "The EnergyGuide rated annual energy consumption for an extra refrigerator. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "extra_refrigerator_usage_multiplier" : {
            "Name": "extra_refrigerator_usage_multiplier",
            "Display Name": "Extra Refrigerator: Usage Multiplier",
            "Description": "Multiplier on the extra refrigerator energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "freezer_present" : {
            "Name": "freezer_present",
            "Display Name": "Freezer: Present",
            "Description": "Whether there is a freezer present.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "freezer_location" : {
            "Name": "freezer_location",
            "Display Name": "Freezer: Location",
            "Description": "The space type for the freezer location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-freezers'>HPXML Freezers</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "garage",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space"
            ],
            "Required": "false"
        },
        "freezer_rated_annual_kwh" : {
            "Name": "freezer_rated_annual_kwh",
            "Display Name": "Freezer: Rated Annual Consumption",
            "Description": "The EnergyGuide rated annual energy consumption for a freezer. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-freezers'>HPXML Freezers</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "freezer_usage_multiplier" : {
            "Name": "freezer_usage_multiplier",
            "Display Name": "Freezer: Usage Multiplier",
            "Description": "Multiplier on the freezer energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-freezers'>HPXML Freezers</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "cooking_range_oven_present" : {
            "Name": "cooking_range_oven_present",
            "Display Name": "Cooking Range/Oven: Present",
            "Description": "Whether there is a cooking range/oven present.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "cooking_range_oven_location" : {
            "Name": "cooking_range_oven_location",
            "Display Name": "Cooking Range/Oven: Location",
            "Description": "The space type for the cooking range/oven location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-cooking-range-oven'>HPXML Cooking Range/Oven</a>) is used.",
            "Type": "Choice",
            "Choices": [
                "conditioned space",
                "basement - conditioned",
                "basement - unconditioned",
                "garage",
                "other housing unit",
                "other heated space",
                "other multifamily buffer space",
                "other non-freezing space"
            ],
            "Required": "false"
        },
        "cooking_range_oven_fuel_type" : {
            "Name": "cooking_range_oven_fuel_type",
            "Display Name": "Cooking Range/Oven: Fuel Type",
            "Description": "Type of fuel used by the cooking range/oven.",
            "Type": "Choice",
            "Default Value": "natural gas",
            "Choices": [
                "electricity",
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "coal"
            ],
            "Required": "true"
        },
        "cooking_range_oven_is_induction" : {
            "Name": "cooking_range_oven_is_induction",
            "Display Name": "Cooking Range/Oven: Is Induction",
            "Description": "Whether the cooking range is induction. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-cooking-range-oven'>HPXML Cooking Range/Oven</a>) is used.",
            "Type": "Boolean",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "cooking_range_oven_is_convection" : {
            "Name": "cooking_range_oven_is_convection",
            "Display Name": "Cooking Range/Oven: Is Convection",
            "Description": "Whether the oven is convection. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-cooking-range-oven'>HPXML Cooking Range/Oven</a>) is used.",
            "Type": "Boolean",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "cooking_range_oven_usage_multiplier" : {
            "Name": "cooking_range_oven_usage_multiplier",
            "Display Name": "Cooking Range/Oven: Usage Multiplier",
            "Description": "Multiplier on the cooking range/oven energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-cooking-range-oven'>HPXML Cooking Range/Oven</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "ceiling_fan_present" : {
            "Name": "ceiling_fan_present",
            "Display Name": "Ceiling Fan: Present",
            "Description": "Whether there are any ceiling fans.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "ceiling_fan_label_energy_use" : {
            "Name": "ceiling_fan_label_energy_use",
            "Display Name": "Ceiling Fan: Label Energy Use",
            "Description": "The label average energy use of the ceiling fan(s). If neither Efficiency nor Label Energy Use provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-ceiling-fans'>HPXML Ceiling Fans</a>) is used.",
            "Type": "Double",
            "Units": "W",
            "Required": "false"
        },
        "ceiling_fan_efficiency" : {
            "Name": "ceiling_fan_efficiency",
            "Display Name": "Ceiling Fan: Efficiency",
            "Description": "The efficiency rating of the ceiling fan(s) at medium speed. Only used if Label Energy Use not provided. If neither Efficiency nor Label Energy Use provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-ceiling-fans'>HPXML Ceiling Fans</a>) is used.",
            "Type": "Double",
            "Units": "CFM/W",
            "Required": "false"
        },
        "ceiling_fan_quantity" : {
            "Name": "ceiling_fan_quantity",
            "Display Name": "Ceiling Fan: Quantity",
            "Description": "Total number of ceiling fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-ceiling-fans'>HPXML Ceiling Fans</a>) is used.",
            "Type": "Integer",
            "Units": "#",
            "Required": "false"
        },
        "ceiling_fan_cooling_setpoint_temp_offset" : {
            "Name": "ceiling_fan_cooling_setpoint_temp_offset",
            "Display Name": "Ceiling Fan: Cooling Setpoint Temperature Offset",
            "Description": "The cooling setpoint temperature offset during months when the ceiling fans are operating. Only applies if ceiling fan quantity is greater than zero. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-ceiling-fans'>HPXML Ceiling Fans</a>) is used.",
            "Type": "Double",
            "Units": "F",
            "Required": "false"
        },
        "misc_plug_loads_television_present" : {
            "Name": "misc_plug_loads_television_present",
            "Display Name": "Misc Plug Loads: Television Present",
            "Description": "Whether there are televisions.",
            "Type": "Boolean",
            "Default Value": "true",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "misc_plug_loads_television_annual_kwh" : {
            "Name": "misc_plug_loads_television_annual_kwh",
            "Display Name": "Misc Plug Loads: Television Annual kWh",
            "Description": "The annual energy consumption of the television plug loads. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "misc_plug_loads_television_usage_multiplier" : {
            "Name": "misc_plug_loads_television_usage_multiplier",
            "Display Name": "Misc Plug Loads: Television Usage Multiplier",
            "Description": "Multiplier on the television energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "misc_plug_loads_other_annual_kwh" : {
            "Name": "misc_plug_loads_other_annual_kwh",
            "Display Name": "Misc Plug Loads: Other Annual kWh",
            "Description": "The annual energy consumption of the other residual plug loads. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "misc_plug_loads_other_frac_sensible" : {
            "Name": "misc_plug_loads_other_frac_sensible",
            "Display Name": "Misc Plug Loads: Other Sensible Fraction",
            "Description": "Fraction of other residual plug loads' internal gains that are sensible. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "misc_plug_loads_other_frac_latent" : {
            "Name": "misc_plug_loads_other_frac_latent",
            "Display Name": "Misc Plug Loads: Other Latent Fraction",
            "Description": "Fraction of other residual plug loads' internal gains that are latent. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "misc_plug_loads_other_usage_multiplier" : {
            "Name": "misc_plug_loads_other_usage_multiplier",
            "Display Name": "Misc Plug Loads: Other Usage Multiplier",
            "Description": "Multiplier on the other energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "misc_plug_loads_well_pump_present" : {
            "Name": "misc_plug_loads_well_pump_present",
            "Display Name": "Misc Plug Loads: Well Pump Present",
            "Description": "Whether there is a well pump.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "misc_plug_loads_well_pump_annual_kwh" : {
            "Name": "misc_plug_loads_well_pump_annual_kwh",
            "Display Name": "Misc Plug Loads: Well Pump Annual kWh",
            "Description": "The annual energy consumption of the well pump plug loads. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "misc_plug_loads_well_pump_usage_multiplier" : {
            "Name": "misc_plug_loads_well_pump_usage_multiplier",
            "Display Name": "Misc Plug Loads: Well Pump Usage Multiplier",
            "Description": "Multiplier on the well pump energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "misc_plug_loads_vehicle_present" : {
            "Name": "misc_plug_loads_vehicle_present",
            "Display Name": "Misc Plug Loads: Vehicle Present",
            "Description": "Whether there is an electric vehicle.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "misc_plug_loads_vehicle_annual_kwh" : {
            "Name": "misc_plug_loads_vehicle_annual_kwh",
            "Display Name": "Misc Plug Loads: Vehicle Annual kWh",
            "Description": "The annual energy consumption of the electric vehicle plug loads. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "misc_plug_loads_vehicle_usage_multiplier" : {
            "Name": "misc_plug_loads_vehicle_usage_multiplier",
            "Display Name": "Misc Plug Loads: Vehicle Usage Multiplier",
            "Description": "Multiplier on the electric vehicle energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "misc_fuel_loads_grill_present" : {
            "Name": "misc_fuel_loads_grill_present",
            "Display Name": "Misc Fuel Loads: Grill Present",
            "Description": "Whether there is a fuel loads grill.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "misc_fuel_loads_grill_fuel_type" : {
            "Name": "misc_fuel_loads_grill_fuel_type",
            "Display Name": "Misc Fuel Loads: Grill Fuel Type",
            "Description": "The fuel type of the fuel loads grill.",
            "Type": "Choice",
            "Default Value": "natural gas",
            "Choices": [
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "wood pellets"
            ],
            "Required": "true"
        },
        "misc_fuel_loads_grill_annual_therm" : {
            "Name": "misc_fuel_loads_grill_annual_therm",
            "Display Name": "Misc Fuel Loads: Grill Annual therm",
            "Description": "The annual energy consumption of the fuel loads grill. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "Double",
            "Units": "therm/yr",
            "Required": "false"
        },
        "misc_fuel_loads_grill_usage_multiplier" : {
            "Name": "misc_fuel_loads_grill_usage_multiplier",
            "Display Name": "Misc Fuel Loads: Grill Usage Multiplier",
            "Description": "Multiplier on the fuel loads grill energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "misc_fuel_loads_lighting_present" : {
            "Name": "misc_fuel_loads_lighting_present",
            "Display Name": "Misc Fuel Loads: Lighting Present",
            "Description": "Whether there is fuel loads lighting.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "misc_fuel_loads_lighting_fuel_type" : {
            "Name": "misc_fuel_loads_lighting_fuel_type",
            "Display Name": "Misc Fuel Loads: Lighting Fuel Type",
            "Description": "The fuel type of the fuel loads lighting.",
            "Type": "Choice",
            "Default Value": "natural gas",
            "Choices": [
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "wood pellets"
            ],
            "Required": "true"
        },
        "misc_fuel_loads_lighting_annual_therm" : {
            "Name": "misc_fuel_loads_lighting_annual_therm",
            "Display Name": "Misc Fuel Loads: Lighting Annual therm",
            "Description": "The annual energy consumption of the fuel loads lighting. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>)is used.",
            "Type": "Double",
            "Units": "therm/yr",
            "Required": "false"
        },
        "misc_fuel_loads_lighting_usage_multiplier" : {
            "Name": "misc_fuel_loads_lighting_usage_multiplier",
            "Display Name": "Misc Fuel Loads: Lighting Usage Multiplier",
            "Description": "Multiplier on the fuel loads lighting energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "misc_fuel_loads_fireplace_present" : {
            "Name": "misc_fuel_loads_fireplace_present",
            "Display Name": "Misc Fuel Loads: Fireplace Present",
            "Description": "Whether there is fuel loads fireplace.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "misc_fuel_loads_fireplace_fuel_type" : {
            "Name": "misc_fuel_loads_fireplace_fuel_type",
            "Display Name": "Misc Fuel Loads: Fireplace Fuel Type",
            "Description": "The fuel type of the fuel loads fireplace.",
            "Type": "Choice",
            "Default Value": "natural gas",
            "Choices": [
                "natural gas",
                "fuel oil",
                "propane",
                "wood",
                "wood pellets"
            ],
            "Required": "true"
        },
        "misc_fuel_loads_fireplace_annual_therm" : {
            "Name": "misc_fuel_loads_fireplace_annual_therm",
            "Display Name": "Misc Fuel Loads: Fireplace Annual therm",
            "Description": "The annual energy consumption of the fuel loads fireplace. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "Double",
            "Units": "therm/yr",
            "Required": "false"
        },
        "misc_fuel_loads_fireplace_frac_sensible" : {
            "Name": "misc_fuel_loads_fireplace_frac_sensible",
            "Display Name": "Misc Fuel Loads: Fireplace Sensible Fraction",
            "Description": "Fraction of fireplace residual fuel loads' internal gains that are sensible. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "misc_fuel_loads_fireplace_frac_latent" : {
            "Name": "misc_fuel_loads_fireplace_frac_latent",
            "Display Name": "Misc Fuel Loads: Fireplace Latent Fraction",
            "Description": "Fraction of fireplace residual fuel loads' internal gains that are latent. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "misc_fuel_loads_fireplace_usage_multiplier" : {
            "Name": "misc_fuel_loads_fireplace_usage_multiplier",
            "Display Name": "Misc Fuel Loads: Fireplace Usage Multiplier",
            "Description": "Multiplier on the fuel loads fireplace energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "pool_present" : {
            "Name": "pool_present",
            "Display Name": "Pool: Present",
            "Description": "Whether there is a pool.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "pool_pump_annual_kwh" : {
            "Name": "pool_pump_annual_kwh",
            "Display Name": "Pool: Pump Annual kWh",
            "Description": "The annual energy consumption of the pool pump. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#pool-pump'>Pool Pump</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "pool_pump_usage_multiplier" : {
            "Name": "pool_pump_usage_multiplier",
            "Display Name": "Pool: Pump Usage Multiplier",
            "Description": "Multiplier on the pool pump energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#pool-pump'>Pool Pump</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "pool_heater_type" : {
            "Name": "pool_heater_type",
            "Display Name": "Pool: Heater Type",
            "Description": "The type of pool heater. Use 'none' if there is no pool heater.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "electric resistance",
                "gas fired",
                "heat pump"
            ],
            "Required": "true"
        },
        "pool_heater_annual_kwh" : {
            "Name": "pool_heater_annual_kwh",
            "Display Name": "Pool: Heater Annual kWh",
            "Description": "The annual energy consumption of the electric resistance pool heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#pool-heater'>Pool Heater</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "pool_heater_annual_therm" : {
            "Name": "pool_heater_annual_therm",
            "Display Name": "Pool: Heater Annual therm",
            "Description": "The annual energy consumption of the gas fired pool heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#pool-heater'>Pool Heater</a>) is used.",
            "Type": "Double",
            "Units": "therm/yr",
            "Required": "false"
        },
        "pool_heater_usage_multiplier" : {
            "Name": "pool_heater_usage_multiplier",
            "Display Name": "Pool: Heater Usage Multiplier",
            "Description": "Multiplier on the pool heater energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#pool-heater'>Pool Heater</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "permanent_spa_present" : {
            "Name": "permanent_spa_present",
            "Display Name": "Permanent Spa: Present",
            "Description": "Whether there is a permanent spa.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "permanent_spa_pump_annual_kwh" : {
            "Name": "permanent_spa_pump_annual_kwh",
            "Display Name": "Permanent Spa: Pump Annual kWh",
            "Description": "The annual energy consumption of the permanent spa pump. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#permanent-spa-pump'>Permanent Spa Pump</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "permanent_spa_pump_usage_multiplier" : {
            "Name": "permanent_spa_pump_usage_multiplier",
            "Display Name": "Permanent Spa: Pump Usage Multiplier",
            "Description": "Multiplier on the permanent spa pump energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#permanent-spa-pump'>Permanent Spa Pump</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "permanent_spa_heater_type" : {
            "Name": "permanent_spa_heater_type",
            "Display Name": "Permanent Spa: Heater Type",
            "Description": "The type of permanent spa heater. Use 'none' if there is no permanent spa heater.",
            "Type": "Choice",
            "Default Value": "none",
            "Choices": [
                "none",
                "electric resistance",
                "gas fired",
                "heat pump"
            ],
            "Required": "true"
        },
        "permanent_spa_heater_annual_kwh" : {
            "Name": "permanent_spa_heater_annual_kwh",
            "Display Name": "Permanent Spa: Heater Annual kWh",
            "Description": "The annual energy consumption of the electric resistance permanent spa heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#permanent-spa-heater'>Permanent Spa Heater</a>) is used.",
            "Type": "Double",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "permanent_spa_heater_annual_therm" : {
            "Name": "permanent_spa_heater_annual_therm",
            "Display Name": "Permanent Spa: Heater Annual therm",
            "Description": "The annual energy consumption of the gas fired permanent spa heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#permanent-spa-heater'>Permanent Spa Heater</a>) is used.",
            "Type": "Double",
            "Units": "therm/yr",
            "Required": "false"
        },
        "permanent_spa_heater_usage_multiplier" : {
            "Name": "permanent_spa_heater_usage_multiplier",
            "Display Name": "Permanent Spa: Heater Usage Multiplier",
            "Description": "Multiplier on the permanent spa heater energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.10.0/workflow_inputs.html#permanent-spa-heater'>Permanent Spa Heater</a>) is used.",
            "Type": "Double",
            "Required": "false"
        },
        "emissions_scenario_names" : {
            "Name": "emissions_scenario_names",
            "Display Name": "Emissions: Scenario Names",
            "Description": "Names of emissions scenarios. If multiple scenarios, use a comma-separated list. If not provided, no emissions scenarios are calculated.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_types" : {
            "Name": "emissions_types",
            "Display Name": "Emissions: Types",
            "Description": "Types of emissions (e.g., CO2e, NOx, etc.). If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_electricity_units" : {
            "Name": "emissions_electricity_units",
            "Display Name": "Emissions: Electricity Units",
            "Description": "Electricity emissions factors units. If multiple scenarios, use a comma-separated list. Only lb/MWh and kg/MWh are allowed.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_electricity_values_or_filepaths" : {
            "Name": "emissions_electricity_values_or_filepaths",
            "Display Name": "Emissions: Electricity Values or File Paths",
            "Description": "Electricity emissions factors values, specified as either an annual factor or an absolute/relative path to a file with hourly factors. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_electricity_number_of_header_rows" : {
            "Name": "emissions_electricity_number_of_header_rows",
            "Display Name": "Emissions: Electricity Files Number of Header Rows",
            "Description": "The number of header rows in the electricity emissions factor file. Only applies when an electricity filepath is used. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_electricity_column_numbers" : {
            "Name": "emissions_electricity_column_numbers",
            "Display Name": "Emissions: Electricity Files Column Numbers",
            "Description": "The column number in the electricity emissions factor file. Only applies when an electricity filepath is used. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_fossil_fuel_units" : {
            "Name": "emissions_fossil_fuel_units",
            "Display Name": "Emissions: Fossil Fuel Units",
            "Description": "Fossil fuel emissions factors units. If multiple scenarios, use a comma-separated list. Only lb/MBtu and kg/MBtu are allowed.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_natural_gas_values" : {
            "Name": "emissions_natural_gas_values",
            "Display Name": "Emissions: Natural Gas Values",
            "Description": "Natural gas emissions factors values, specified as an annual factor. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_propane_values" : {
            "Name": "emissions_propane_values",
            "Display Name": "Emissions: Propane Values",
            "Description": "Propane emissions factors values, specified as an annual factor. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_fuel_oil_values" : {
            "Name": "emissions_fuel_oil_values",
            "Display Name": "Emissions: Fuel Oil Values",
            "Description": "Fuel oil emissions factors values, specified as an annual factor. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_coal_values" : {
            "Name": "emissions_coal_values",
            "Display Name": "Emissions: Coal Values",
            "Description": "Coal emissions factors values, specified as an annual factor. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_wood_values" : {
            "Name": "emissions_wood_values",
            "Display Name": "Emissions: Wood Values",
            "Description": "Wood emissions factors values, specified as an annual factor. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "emissions_wood_pellets_values" : {
            "Name": "emissions_wood_pellets_values",
            "Display Name": "Emissions: Wood Pellets Values",
            "Description": "Wood pellets emissions factors values, specified as an annual factor. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_scenario_names" : {
            "Name": "utility_bill_scenario_names",
            "Display Name": "Utility Bills: Scenario Names",
            "Description": "Names of utility bill scenarios. If multiple scenarios, use a comma-separated list. If not provided, no utility bills scenarios are calculated.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_electricity_filepaths" : {
            "Name": "utility_bill_electricity_filepaths",
            "Display Name": "Utility Bills: Electricity File Paths",
            "Description": "Electricity tariff file specified as an absolute/relative path to a file with utility rate structure information. Tariff file must be formatted to OpenEI API version 7. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_electricity_fixed_charges" : {
            "Name": "utility_bill_electricity_fixed_charges",
            "Display Name": "Utility Bills: Electricity Fixed Charges",
            "Description": "Electricity utility bill monthly fixed charges. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_natural_gas_fixed_charges" : {
            "Name": "utility_bill_natural_gas_fixed_charges",
            "Display Name": "Utility Bills: Natural Gas Fixed Charges",
            "Description": "Natural gas utility bill monthly fixed charges. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_propane_fixed_charges" : {
            "Name": "utility_bill_propane_fixed_charges",
            "Display Name": "Utility Bills: Propane Fixed Charges",
            "Description": "Propane utility bill monthly fixed charges. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_fuel_oil_fixed_charges" : {
            "Name": "utility_bill_fuel_oil_fixed_charges",
            "Display Name": "Utility Bills: Fuel Oil Fixed Charges",
            "Description": "Fuel oil utility bill monthly fixed charges. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_coal_fixed_charges" : {
            "Name": "utility_bill_coal_fixed_charges",
            "Display Name": "Utility Bills: Coal Fixed Charges",
            "Description": "Coal utility bill monthly fixed charges. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_wood_fixed_charges" : {
            "Name": "utility_bill_wood_fixed_charges",
            "Display Name": "Utility Bills: Wood Fixed Charges",
            "Description": "Wood utility bill monthly fixed charges. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_wood_pellets_fixed_charges" : {
            "Name": "utility_bill_wood_pellets_fixed_charges",
            "Display Name": "Utility Bills: Wood Pellets Fixed Charges",
            "Description": "Wood pellets utility bill monthly fixed charges. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_electricity_marginal_rates" : {
            "Name": "utility_bill_electricity_marginal_rates",
            "Display Name": "Utility Bills: Electricity Marginal Rates",
            "Description": "Electricity utility bill marginal rates. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_natural_gas_marginal_rates" : {
            "Name": "utility_bill_natural_gas_marginal_rates",
            "Display Name": "Utility Bills: Natural Gas Marginal Rates",
            "Description": "Natural gas utility bill marginal rates. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_propane_marginal_rates" : {
            "Name": "utility_bill_propane_marginal_rates",
            "Display Name": "Utility Bills: Propane Marginal Rates",
            "Description": "Propane utility bill marginal rates. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_fuel_oil_marginal_rates" : {
            "Name": "utility_bill_fuel_oil_marginal_rates",
            "Display Name": "Utility Bills: Fuel Oil Marginal Rates",
            "Description": "Fuel oil utility bill marginal rates. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_coal_marginal_rates" : {
            "Name": "utility_bill_coal_marginal_rates",
            "Display Name": "Utility Bills: Coal Marginal Rates",
            "Description": "Coal utility bill marginal rates. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_wood_marginal_rates" : {
            "Name": "utility_bill_wood_marginal_rates",
            "Display Name": "Utility Bills: Wood Marginal Rates",
            "Description": "Wood utility bill marginal rates. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_wood_pellets_marginal_rates" : {
            "Name": "utility_bill_wood_pellets_marginal_rates",
            "Display Name": "Utility Bills: Wood Pellets Marginal Rates",
            "Description": "Wood pellets utility bill marginal rates. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_pv_compensation_types" : {
            "Name": "utility_bill_pv_compensation_types",
            "Display Name": "Utility Bills: PV Compensation Types",
            "Description": "Utility bill PV compensation types. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_pv_net_metering_annual_excess_sellback_rate_types" : {
            "Name": "utility_bill_pv_net_metering_annual_excess_sellback_rate_types",
            "Display Name": "Utility Bills: PV Net Metering Annual Excess Sellback Rate Types",
            "Description": "Utility bill PV net metering annual excess sellback rate types. Only applies if the PV compensation type is 'NetMetering'. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_pv_net_metering_annual_excess_sellback_rates" : {
            "Name": "utility_bill_pv_net_metering_annual_excess_sellback_rates",
            "Display Name": "Utility Bills: PV Net Metering Annual Excess Sellback Rates",
            "Description": "Utility bill PV net metering annual excess sellback rates. Only applies if the PV compensation type is 'NetMetering' and the PV annual excess sellback rate type is 'User-Specified'. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_pv_feed_in_tariff_rates" : {
            "Name": "utility_bill_pv_feed_in_tariff_rates",
            "Display Name": "Utility Bills: PV Feed-In Tariff Rates",
            "Description": "Utility bill PV annual full/gross feed-in tariff rates. Only applies if the PV compensation type is 'FeedInTariff'. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_pv_monthly_grid_connection_fee_units" : {
            "Name": "utility_bill_pv_monthly_grid_connection_fee_units",
            "Display Name": "Utility Bills: PV Monthly Grid Connection Fee Units",
            "Description": "Utility bill PV monthly grid connection fee units. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "utility_bill_pv_monthly_grid_connection_fees" : {
            "Name": "utility_bill_pv_monthly_grid_connection_fees",
            "Display Name": "Utility Bills: PV Monthly Grid Connection Fees",
            "Description": "Utility bill PV monthly grid connection fees. If multiple scenarios, use a comma-separated list.",
            "Type": "String",
            "Required": "false"
        },
        "additional_properties" : {
            "Name": "additional_properties",
            "Display Name": "Additional Properties",
            "Description": "Additional properties specified as key-value pairs (i.e., key=value). If multiple additional properties, use a |-separated list. For example, 'LowIncome=false|Remodeled|Description=2-story home in Denver'. These properties will be stored in the HPXML file under /HPXML/SoftwareInfo/extension/AdditionalProperties.",
            "Type": "String",
            "Required": "false"
        },
        "combine_like_surfaces" : {
            "Name": "combine_like_surfaces",
            "Display Name": "Combine like surfaces?",
            "Description": "If true, combines like surfaces to simplify the HPXML file generated.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "apply_defaults" : {
            "Name": "apply_defaults",
            "Display Name": "Apply Default Values?",
            "Description": "If true, applies OS-HPXML default values to the HPXML output file. Setting to true will also force validation of the HPXML output file before applying OS-HPXML default values.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        "apply_validation" : {
            "Name": "apply_validation",
            "Display Name": "Apply Validation?",
            "Description": "If true, validates the HPXML output file. Set to false for faster performance. Note that validation is not needed if the HPXML file will be validated downstream (e.g., via the HPXMLtoOpenStudio measure).",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        }
