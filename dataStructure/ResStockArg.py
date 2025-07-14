import sys
import os

import re
import json

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../")  # répertoire supérieur
#PACKAGE_DIR = os.path.abspath(PROJECT_DIR+ "/../")
sys.path.append(os.path.join(PROJECT_DIR))

from ParseHPXMLinputs.ParseHPXMLinputs import parse_xml_file

class ResStockArguments():
    arguments = {
        "schedules_vacancy_period" : {
            "Name": "schedules_vacancy_period",
            "Display Name": "Schedules: Vacancy Period",
            "Description": "Specifies the vacancy period. Enter a date like \"Dec 15 - Jan 15\". Optionally, can enter hour of the day like \"Dec 15 2 - Jan 15 20\" (start hour can be 0 through 23 and end hour can be 1 through 24).",
            "Type": "String",
            "Units": None,
            "Required": "false"
        },
        "schedules_power_outage_period" : {
            "Name": "schedules_power_outage_period",
            "Display Name": "Schedules: Power Outage Period",
            "Description": "Specifies the power outage period. Enter a date like \"Dec 15 - Jan 15\". Optionally, can enter hour of the day like \"Dec 15 2 - Jan 15 20\" (start hour can be 0 through 23 and end hour can be 1 through 24).",
            "Type": "String",
            "Units": None,
            "Required": "false"
        },
        "schedules_power_outage_window_natvent_availability" : {
            "Name": "schedules_power_outage_window_natvent_availability",
            "Display Name": "Schedules: Power Outage Period Window Natural Ventilation Availability",
            "Description": "The availability of the natural ventilation schedule during the outage period.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "regular schedule",
                "always available",
                "always unavailable"
            ],
            "Required": "false"
        },
        "simulation_control_daylight_saving_enabled" : {
            "Name": "simulation_control_daylight_saving_enabled",
            "Display Name": "Simulation Control: Daylight Saving Enabled",
            "Description": "Whether to use daylight saving. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-building-site'>HPXML Building Site</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "true",
                "false"
            ],
            "Required": "false"
        },
        "site_type" : {
            "Name": "site_type",
            "Display Name": "Site: Type",
            "Description": "The type of site. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "suburban",
                "urban",
                "rural"
            ],
            "Required": "false"
        },
        "site_shielding_of_home" : {
            "Name": "site_shielding_of_home",
            "Display Name": "Site: Shielding of Home",
            "Description": "Presence of nearby buildings, trees, obstructions for infiltration model. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "exposed",
                "normal",
                "well-shielded"
            ],
            "Required": "false"
        },
        "site_soil_and_moisture_type" : {
            "Name": "site_soil_and_moisture_type",
            "Display Name": "Site: Soil and Moisture Type",
            "Description": "Type of soil and moisture. This is used to inform ground conductivity and diffusivity. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Type": "String",
            "Units": "Btu/hr-ft-F",
            "Required": "false"
        },
        "site_ground_diffusivity" : {
            "Name": "site_ground_diffusivity",
            "Display Name": "Site: Ground Diffusivity",
            "Description": "Diffusivity of the ground soil. If provided, overrides the previous site and moisture type input.",
            "Type": "String",
            "Units": "ft^2/hr",
            "Required": "false"
        },
        "site_zip_code" : {
            "Name": "site_zip_code",
            "Display Name": "Site: Zip Code",
            "Description": "Zip code of the home address.",
            "Type": "String",
            "Units": None,
            "Required": "false"
        },
        "site_iecc_zone" : {
            "Name": "site_iecc_zone",
            "Display Name": "Site: IECC Zone",
            "Description": "IECC zone of the home address.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
        "site_state_code" : {
            "Name": "site_state_code",
            "Display Name": "Site: State Code",
            "Description": "State code of the home address.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
        "site_time_zone_utc_offset" : {
            "Name": "site_time_zone_utc_offset",
            "Display Name": "Site: Time Zone UTC Offset",
            "Description": "Time zone UTC offset of the home address. Must be between -12 and 14.",
            "Type": "String",
            "Units": "hr",
            "Required": "false"
        },
        "weather_station_epw_filepath" : {
            "Name": "weather_station_epw_filepath",
            "Display Name": "Weather Station: EnergyPlus Weather (EPW) Filepath",
            "Description": "Path of the EPW file.",
            "Type": "String",
            "Default Value": "USA_CO_Denver.Intl.AP.725650_TMY3.epw",
            "Required": "true"
        },
        "year_built" : {
            "Name": "year_built",
            "Display Name": "Building Construction: Year Built",
            "Description": "The year the building was built.",
            "Type": "String",
            "Units": None,
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
            "Description": "The number of bathrooms in the unit. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-building-construction'>HPXML Building Construction</a>) is used.",
            "Type": "String",
            "Units": "#",
            "Required": "false"
        },
        "geometry_unit_num_occupants" : {
            "Name": "geometry_unit_num_occupants",
            "Display Name": "Geometry: Unit Number of Occupants",
            "Description": "The number of occupants in the unit. If not provided, an *asset* calculation is performed assuming standard occupancy, in which various end use defaults (e.g., plug loads, appliances, and hot water usage) are calculated based on Number of Bedrooms and Conditioned Floor Area per ANSI/RESNET/ICC 301-2019. If provided, an *operational* calculation is instead performed in which the end use defaults are adjusted using the relationship between Number of Bedrooms and Number of Occupants from RECS 2015.",
            "Type": "String",
            "Units": "#",
            "Required": "false"
        },
        "geometry_building_num_units" : {
            "Name": "geometry_building_num_units",
            "Display Name": "Geometry: Building Number of Units",
            "Description": "The number of units in the building. Required for single-family attached and apartment units.",
            "Type": "String",
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
            "Type": "String",
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
            "Description": "The height of the neighboring building to the front. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "neighbor_back_height" : {
            "Name": "neighbor_back_height",
            "Display Name": "Neighbor: Back Height",
            "Description": "The height of the neighboring building to the back. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "neighbor_left_height" : {
            "Name": "neighbor_left_height",
            "Display Name": "Neighbor: Left Height",
            "Description": "The height of the neighboring building to the left. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "neighbor_right_height" : {
            "Name": "neighbor_right_height",
            "Display Name": "Neighbor: Right Height",
            "Description": "The height of the neighboring building to the right. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-site'>HPXML Site</a>) is used.",
            "Type": "String",
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
            "Description": "The material type of the foundation wall. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-foundation-walls'>HPXML Foundation Walls</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The thickness of the foundation wall. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-foundation-walls'>HPXML Foundation Walls</a>) is used.",
            "Type": "String",
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
            "Choices": [
                "auto",
                "interior",
                "exterior"
            ],
            "Required": "false"
        },
        "foundation_wall_insulation_distance_to_top" : {
            "Name": "foundation_wall_insulation_distance_to_top",
            "Display Name": "Foundation Wall: Insulation Distance To Top",
            "Description": "The distance from the top of the foundation wall to the top of the foundation wall insulation. Only applies to basements/crawlspaces. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-foundation-walls'>HPXML Foundation Walls</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "foundation_wall_insulation_distance_to_bottom" : {
            "Name": "foundation_wall_insulation_distance_to_bottom",
            "Display Name": "Foundation Wall: Insulation Distance To Bottom",
            "Description": "The distance from the top of the foundation wall to the bottom of the foundation wall insulation. Only applies to basements/crawlspaces. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-foundation-walls'>HPXML Foundation Walls</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "foundation_wall_assembly_r" : {
            "Name": "foundation_wall_assembly_r",
            "Display Name": "Foundation Wall: Assembly R-value",
            "Description": "Assembly R-value for the foundation walls. Only applies to basements/crawlspaces. If provided, overrides the previous foundation wall insulation inputs. If not provided, it is ignored.",
            "Type": "String",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "rim_joist_assembly_r" : {
            "Name": "rim_joist_assembly_r",
            "Display Name": "Rim Joist: Assembly R-value",
            "Description": "Assembly R-value for the rim joists. Only applies to basements/crawlspaces. Required if a rim joist height is provided.",
            "Type": "String",
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
        "slab_perimeter_depth" : {
            "Name": "slab_perimeter_depth",
            "Display Name": "Slab: Perimeter Insulation Depth",
            "Description": "Depth from grade to bottom of vertical slab perimeter insulation. Applies to slab-on-grade foundations and basement/crawlspace floors.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "0",
            "Required": "true"
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
        "slab_under_width" : {
            "Name": "slab_under_width",
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
            "Description": "The thickness of the slab. Zero can be entered if there is a dirt floor instead of a slab. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-slabs'>HPXML Slabs</a>) is used.",
            "Type": "String",
            "Units": "in",
            "Required": "false"
        },
        "slab_carpet_fraction" : {
            "Name": "slab_carpet_fraction",
            "Display Name": "Slab: Carpet Fraction",
            "Description": "Fraction of the slab floor area that is carpeted. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-slabs'>HPXML Slabs</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "slab_carpet_r" : {
            "Name": "slab_carpet_r",
            "Display Name": "Slab: Carpet R-value",
            "Description": "R-value of the slab carpet. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-slabs'>HPXML Slabs</a>) is used.",
            "Type": "String",
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
            "Description": "The material type of the roof. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-roofs'>HPXML Roofs</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The color of the roof. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-roofs'>HPXML Roofs</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The grade of the radiant barrier in the attic. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-roofs'>HPXML Roofs</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The siding type of the walls. Also applies to rim joists. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-walls'>HPXML Walls</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The color of the walls. Also applies to rim joists. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-walls'>HPXML Walls</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The ratio of window area to wall area for the unit's front facade. Enter 0 if specifying Front Window Area instead.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.18",
            "Required": "true"
        },
        "window_back_wwr" : {
            "Name": "window_back_wwr",
            "Display Name": "Windows: Back Window-to-Wall Ratio",
            "Description": "The ratio of window area to wall area for the unit's back facade. Enter 0 if specifying Back Window Area instead.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.18",
            "Required": "true"
        },
        "window_left_wwr" : {
            "Name": "window_left_wwr",
            "Display Name": "Windows: Left Window-to-Wall Ratio",
            "Description": "The ratio of window area to wall area for the unit's left facade (when viewed from the front). Enter 0 if specifying Left Window Area instead.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.18",
            "Required": "true"
        },
        "window_right_wwr" : {
            "Name": "window_right_wwr",
            "Display Name": "Windows: Right Window-to-Wall Ratio",
            "Description": "The ratio of window area to wall area for the unit's right facade (when viewed from the front). Enter 0 if specifying Right Window Area instead.",
            "Type": "Double",
            "Units": "Frac",
            "Default Value": "0.18",
            "Required": "true"
        },
        "window_area_front" : {
            "Name": "window_area_front",
            "Display Name": "Windows: Front Window Area",
            "Description": "The amount of window area on the unit's front facade. Enter 0 if specifying Front Window-to-Wall Ratio instead.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "window_area_back" : {
            "Name": "window_area_back",
            "Display Name": "Windows: Back Window Area",
            "Description": "The amount of window area on the unit's back facade. Enter 0 if specifying Back Window-to-Wall Ratio instead.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "window_area_left" : {
            "Name": "window_area_left",
            "Display Name": "Windows: Left Window Area",
            "Description": "The amount of window area on the unit's left facade (when viewed from the front). Enter 0 if specifying Left Window-to-Wall Ratio instead.",
            "Type": "Double",
            "Units": "ft^2",
            "Default Value": "0",
            "Required": "true"
        },
        "window_area_right" : {
            "Name": "window_area_right",
            "Display Name": "Windows: Right Window Area",
            "Description": "The amount of window area on the unit's right facade (when viewed from the front). Enter 0 if specifying Right Window-to-Wall Ratio instead.",
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
            "Description": "Fraction of windows that are operable. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "window_natvent_availability" : {
            "Name": "window_natvent_availability",
            "Display Name": "Windows: Natural Ventilation Availability",
            "Description": "For operable windows, the number of days/week that windows can be opened by occupants for natural ventilation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "String",
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
        "window_interior_shading_winter" : {
            "Name": "window_interior_shading_winter",
            "Display Name": "Windows: Winter Interior Shading",
            "Description": "Interior shading coefficient for the winter season. 1.0 indicates no reduction in solar gain, 0.85 indicates 15% reduction, etc. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "window_interior_shading_summer" : {
            "Name": "window_interior_shading_summer",
            "Display Name": "Windows: Summer Interior Shading",
            "Description": "Interior shading coefficient for the summer season. 1.0 indicates no reduction in solar gain, 0.85 indicates 15% reduction, etc. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "window_exterior_shading_winter" : {
            "Name": "window_exterior_shading_winter",
            "Display Name": "Windows: Winter Exterior Shading",
            "Description": "Exterior shading coefficient for the winter season. 1.0 indicates no reduction in solar gain, 0.85 indicates 15% reduction, etc. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "window_exterior_shading_summer" : {
            "Name": "window_exterior_shading_summer",
            "Display Name": "Windows: Summer Exterior Shading",
            "Description": "Exterior shading coefficient for the summer season. 1.0 indicates no reduction in solar gain, 0.85 indicates 15% reduction, etc. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "window_shading_summer_season" : {
            "Name": "window_shading_summer_season",
            "Display Name": "Windows: Shading Summer Season",
            "Description": "Enter a date like 'May 1 - Sep 30'. Defines the summer season for purposes of shading coefficients; the rest of the year is assumed to be winter. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-windows'>HPXML Windows</a>) is used.",
            "Type": "String",
            "Units": None,
            "Required": "false"
        },
        "window_storm_type" : {
            "Name": "window_storm_type",
            "Display Name": "Windows: Storm Type",
            "Description": "The type of storm, if present. If not provided, assumes there is no storm.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Units": None,
            "Choices": [
                "auto",
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
        "air_leakage_units" : {
            "Name": "air_leakage_units",
            "Display Name": "Air Leakage: Units",
            "Description": "The unit of measure for the air leakage.",
            "Type": "Choice",
            "Default Value": "ACH",
            "Choices": [
                "ACH",
                "CFM",
                "ACHnatural",
                "CFMnatural",
                "EffectiveLeakageArea"
            ],
            "Required": "true"
        },
        "air_leakage_house_pressure" : {
            "Name": "air_leakage_house_pressure",
            "Display Name": "Air Leakage: House Pressure",
            "Description": "The house pressure relative to outside. Required when units are ACH or CFM.",
            "Type": "Double",
            "Units": "Pa",
            "Default Value": "50",
            "Required": "true"
        },
        "air_leakage_value" : {
            "Name": "air_leakage_value",
            "Display Name": "Air Leakage: Value",
            "Description": "Air exchange rate value. For 'EffectiveLeakageArea', provide value in sq. in.",
            "Type": "Double",
            "Default Value": "3",
            "Required": "true"
        },
        "air_leakage_type" : {
            "Name": "air_leakage_type",
            "Display Name": "Air Leakage: Type",
            "Description": "Type of air leakage. If 'unit total', represents the total infiltration to the unit as measured by a compartmentalization test, in which case the air leakage value will be adjusted by the ratio of exterior envelope surface area to total envelope surface area. Otherwise, if 'unit exterior only', represents the infiltration to the unit from outside only as measured by a guarded test. Required when unit type is single-family attached or apartment unit.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "unit total",
                "unit exterior only"
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
            "Description": "The output heating capacity of the heating system. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-heating-systems'>HPXML Heating Systems</a>) is used.",
            "Type": "String",
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
            "Type": "String",
            "Units": "Btuh",
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
            "Description": "The compressor type of the cooling system. Only applies to central air conditioner and mini-split. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#central-air-conditioner'>Central Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-air-conditioner'>Mini-Split Air Conditioner</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "single stage",
                "two stage",
                "variable speed"
            ],
            "Required": "false"
        },
        "cooling_system_cooling_sensible_heat_fraction" : {
            "Name": "cooling_system_cooling_sensible_heat_fraction",
            "Display Name": "Cooling System: Cooling Sensible Heat Fraction",
            "Description": "The sensible heat fraction of the cooling system. Ignored for evaporative cooler. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#central-air-conditioner'>Central Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner'>Room Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-air-conditioner'>Packaged Terminal Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-air-conditioner'>Mini-Split Air Conditioner</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "cooling_system_cooling_capacity" : {
            "Name": "cooling_system_cooling_capacity",
            "Display Name": "Cooling System: Cooling Capacity",
            "Description": "The output cooling capacity of the cooling system. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#central-air-conditioner'>Central Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner'>Room Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-air-conditioner'>Packaged Terminal Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#evaporative-cooler'>Evaporative Cooler</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-air-conditioner'>Mini-Split Air Conditioner</a>) is used.",
            "Type": "String",
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
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "true",
                "false"
            ],
            "Required": "false"
        },
        "cooling_system_crankcase_heater_watts" : {
            "Name": "cooling_system_crankcase_heater_watts",
            "Display Name": "Cooling System: Crankcase Heater Power Watts",
            "Description": "Cooling system crankcase heater power consumption in Watts. Applies only to central air conditioner, room air conditioner, packaged terminal air conditioner and mini-split. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#central-air-conditioner'>Central Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner'>Room Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-air-conditioner'>Packaged Terminal Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-air-conditioner'>Mini-Split Air Conditioner</a>) is used.",
            "Type": "String",
            "Units": "W",
            "Required": "false"
        },
        "cooling_system_integrated_heating_system_fuel" : {
            "Name": "cooling_system_integrated_heating_system_fuel",
            "Display Name": "Cooling System: Integrated Heating System Fuel Type",
            "Description": "The fuel type of the heating system integrated into cooling system. Only used for packaged terminal air conditioner and room air conditioner.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "cooling_system_integrated_heating_system_capacity" : {
            "Name": "cooling_system_integrated_heating_system_capacity",
            "Display Name": "Cooling System: Integrated Heating System Heating Capacity",
            "Description": "The output heating capacity of the heating system integrated into cooling system. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner'>Room Air Conditioner</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-air-conditioner'>Packaged Terminal Air Conditioner</a>) is used. Only used for room air conditioner and packaged terminal air conditioner.",
            "Type": "String",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "cooling_system_integrated_heating_system_fraction_heat_load_served" : {
            "Name": "cooling_system_integrated_heating_system_fraction_heat_load_served",
            "Display Name": "Cooling System: Integrated Heating System Fraction Heat Load Served",
            "Description": "The heating load served by the heating system integrated into cooling system. Only used for packaged terminal air conditioner and room air conditioner.",
            "Type": "String",
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
            "Description": "The compressor type of the heat pump. Only applies to air-to-air and mini-split. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "single stage",
                "two stage",
                "variable speed"
            ],
            "Required": "false"
        },
        "heat_pump_cooling_sensible_heat_fraction" : {
            "Name": "heat_pump_cooling_sensible_heat_fraction",
            "Display Name": "Heat Pump: Cooling Sensible Heat Fraction",
            "Description": "The sensible heat fraction of the heat pump. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#ground-to-air-heat-pump'>Ground-to-Air Heat Pump</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_heating_capacity" : {
            "Name": "heat_pump_heating_capacity",
            "Display Name": "Heat Pump: Heating Capacity",
            "Description": "The output heating capacity of the heat pump. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#ground-to-air-heat-pump'>Ground-to-Air Heat Pump</a>) is used.",
            "Type": "String",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heat_pump_heating_capacity_retention_fraction" : {
            "Name": "heat_pump_heating_capacity_retention_fraction",
            "Display Name": "Heat Pump: Heating Capacity Retention Fraction",
            "Description": "The output heating capacity of the heat pump at a user-specified temperature (e.g., 17F or 5F) divided by the above nominal heating capacity. Applies to all heat pump types except ground-to-air. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_heating_capacity_retention_temp" : {
            "Name": "heat_pump_heating_capacity_retention_temp",
            "Display Name": "Heat Pump: Heating Capacity Retention Temperature",
            "Description": "The user-specified temperature (e.g., 17F or 5F) for the above heating capacity retention fraction. Applies to all heat pump types except ground-to-air. Required if the Heating Capacity Retention Fraction is provided.",
            "Type": "String",
            "Units": "deg-F",
            "Required": "false"
        },
        "heat_pump_cooling_capacity" : {
            "Name": "heat_pump_cooling_capacity",
            "Display Name": "Heat Pump: Cooling Capacity",
            "Description": "The output cooling capacity of the heat pump. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#ground-to-air-heat-pump'>Ground-to-Air Heat Pump</a>) is used.",
            "Type": "String",
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
            "Description": "The temperature below which the heat pump compressor is disabled. If both this and Backup Heating Lockout Temperature are provided and use the same value, it essentially defines a switchover temperature (for, e.g., a dual-fuel heat pump). Applies to all heat pump types other than ground-to-air. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>) is used.",
            "Type": "String",
            "Units": "deg-F",
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
            "Description": "The backup output heating capacity of the heat pump. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#backup'>Backup</a>) is used. Only applies if Backup Type is 'integrated'.",
            "Type": "String",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "heat_pump_backup_heating_lockout_temp" : {
            "Name": "heat_pump_backup_heating_lockout_temp",
            "Display Name": "Heat Pump: Backup Heating Lockout Temperature",
            "Description": "The temperature above which the heat pump backup system is disabled. If both this and Compressor Lockout Temperature are provided and use the same value, it essentially defines a switchover temperature (for, e.g., a dual-fuel heat pump). Applies for both Backup Type of 'integrated' and 'separate'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#backup'>Backup</a>) is used.",
            "Type": "String",
            "Units": "deg-F",
            "Required": "false"
        },
        "heat_pump_sizing_methodology" : {
            "Name": "heat_pump_sizing_methodology",
            "Display Name": "Heat Pump: Sizing Methodology",
            "Description": "The auto-sizing methodology to use when the heat pump capacity is not provided. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-hvac-sizing-control'>HPXML HVAC Sizing Control</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "ACCA",
                "HERS",
                "MaxLoad"
            ],
            "Required": "false"
        },
        "heat_pump_is_ducted" : {
            "Name": "heat_pump_is_ducted",
            "Display Name": "Heat Pump: Is Ducted",
            "Description": "Whether the heat pump is ducted or not. Only used for mini-split. It's assumed that air-to-air and ground-to-air are ducted, and packaged terminal heat pump and room air conditioner with reverse cycle are not ducted. If not provided, assumes not ducted.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "true",
                "false"
            ],
            "Required": "false"
        },
        "heat_pump_crankcase_heater_watts" : {
            "Name": "heat_pump_crankcase_heater_watts",
            "Display Name": "Heat Pump: Crankcase Heater Power Watts",
            "Description": "Heat Pump crankcase heater power consumption in Watts. Applies only to air-to-air, mini-split, packaged terminal heat pump and room air conditioner with reverse cycle. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-to-air-heat-pump'>Air-to-Air Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#mini-split-heat-pump'>Mini-Split Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#packaged-terminal-heat-pump'>Packaged Terminal Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#room-air-conditioner-w-reverse-cycle'>Room Air Conditioner w/ Reverse Cycle</a>) is used.",
            "Type": "String",
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
                "auto",
                "Absolute capacities"
            ],
            "Required": "false"
        },
        "hvac_perf_data_heating_outdoor_temperatures" : {
            "Name": "hvac_perf_data_heating_outdoor_temperatures",
            "Display Name": "HVAC Detailed Performance Data: Heating Outdoor Temperatures",
            "Description": "Outdoor temperatures of heating detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). One of the outdoor temperatures must be 47 deg-F. At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "deg-F",
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
            "Description": "Outdoor temperatures of cooling detailed performance data if available. Applies only to variable-speed air-source HVAC systems (central air conditioners, mini-split air conditioners, air-to-air heat pumps, and mini-split heat pumps). One of the outdoor temperatures must be 95 deg-F. At least two performance data points are required using a comma-separated list.",
            "Type": "String",
            "Units": "deg-F",
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
            "Description": "Configuration of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#ground-to-air-heat-pump'>Ground-to-Air Heat Pump</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "none",
                "vertical"
            ],
            "Required": "false"
        },
        "geothermal_loop_borefield_configuration" : {
            "Name": "geothermal_loop_borefield_configuration",
            "Display Name": "Geothermal Loop: Borefield Configuration",
            "Description": "Borefield configuration of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "Water flow rate through the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "String",
            "Units": "gpm",
            "Required": "false"
        },
        "geothermal_loop_boreholes_count" : {
            "Name": "geothermal_loop_boreholes_count",
            "Display Name": "Geothermal Loop: Boreholes Count",
            "Description": "Number of boreholes. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "String",
            "Units": "#",
            "Required": "false"
        },
        "geothermal_loop_boreholes_length" : {
            "Name": "geothermal_loop_boreholes_length",
            "Display Name": "Geothermal Loop: Boreholes Length",
            "Description": "Average length of each borehole (vertical). Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "geothermal_loop_boreholes_spacing" : {
            "Name": "geothermal_loop_boreholes_spacing",
            "Display Name": "Geothermal Loop: Boreholes Spacing",
            "Description": "Distance between bores. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "geothermal_loop_boreholes_diameter" : {
            "Name": "geothermal_loop_boreholes_diameter",
            "Display Name": "Geothermal Loop: Boreholes Diameter",
            "Description": "Diameter of bores. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "String",
            "Units": "in",
            "Required": "false"
        },
        "geothermal_loop_grout_type" : {
            "Name": "geothermal_loop_grout_type",
            "Display Name": "Geothermal Loop: Grout Type",
            "Description": "Grout type of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "standard",
                "thermally enhanced"
            ],
            "Required": "false"
        },
        "geothermal_loop_pipe_type" : {
            "Name": "geothermal_loop_pipe_type",
            "Display Name": "Geothermal Loop: Pipe Type",
            "Description": "Pipe type of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "standard",
                "thermally enhanced"
            ],
            "Required": "false"
        },
        "geothermal_loop_pipe_diameter" : {
            "Name": "geothermal_loop_pipe_diameter",
            "Display Name": "Geothermal Loop: Pipe Diameter",
            "Description": "Pipe diameter of the geothermal loop. Only applies to ground-to-air heat pump type. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-geothermal-loops'>HPXML Geothermal Loops</a>) is used.",
            "Type": "Choice",
            "Units": "in",
            "Choices": [
                "auto",
                "3/4\" pipe",
                "1\" pipe",
                "1-1/4\" pipe"
            ],
            "Required": "false"
        },
        "heating_system_2_type" : {
            "Name": "heating_system_2_type",
            "Display Name": "Heating System 2: Type",
            "Description": "The type of the second heating system.",
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
            "Description": "The output heating capacity of the second heating system. If not provided, the OS-HPXML autosized default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-heating-systems'>HPXML Heating Systems</a>) is used.",
            "Type": "String",
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
        "hvac_control_heating_season_period" : {
            "Name": "hvac_control_heating_season_period",
            "Display Name": "HVAC Control: Heating Season Period",
            "Description": "Enter a date like 'Nov 1 - Jun 30'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-hvac-control'>HPXML HVAC Control</a>) is used. Can also provide 'BuildingAmerica' to use automatic seasons from the Building America House Simulation Protocols.",
            "Type": "String",
            "Units": None,
            "Required": "false"
        },
        "hvac_control_cooling_season_period" : {
            "Name": "hvac_control_cooling_season_period",
            "Display Name": "HVAC Control: Cooling Season Period",
            "Description": "Enter a date like 'Jun 1 - Oct 31'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-hvac-control'>HPXML HVAC Control</a>) is used. Can also provide 'BuildingAmerica' to use automatic seasons from the Building America House Simulation Protocols.",
            "Type": "String",
            "Units": None,
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
        "ducts_return_leakage_to_outside_value" : {
            "Name": "ducts_return_leakage_to_outside_value",
            "Display Name": "Ducts: Return Leakage to Outside Value",
            "Description": "The leakage value to outside for the return ducts.",
            "Type": "Double",
            "Default Value": "0.1",
            "Required": "true"
        },
        "ducts_supply_location" : {
            "Name": "ducts_supply_location",
            "Display Name": "Ducts: Supply Location",
            "Description": "The location of the supply ducts. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The insulation r-value of the supply ducts excluding air films.",
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
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The supply ducts surface area in the given location. If neither Surface Area nor Area Fraction provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "String",
            "Units": "ft^2",
            "Required": "false"
        },
        "ducts_supply_surface_area_fraction" : {
            "Name": "ducts_supply_surface_area_fraction",
            "Display Name": "Ducts: Supply Area Fraction",
            "Description": "The fraction of supply ducts surface area in the given location. Only used if Surface Area is not provided. If the fraction is less than 1, the remaining duct area is assumed to be in conditioned space. If neither Surface Area nor Area Fraction provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "String",
            "Units": "frac",
            "Required": "false"
        },
        "ducts_return_location" : {
            "Name": "ducts_return_location",
            "Display Name": "Ducts: Return Location",
            "Description": "The location of the return ducts. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The insulation r-value of the return ducts excluding air films.",
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
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The return ducts surface area in the given location. If neither Surface Area nor Area Fraction provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "String",
            "Units": "ft^2",
            "Required": "false"
        },
        "ducts_return_surface_area_fraction" : {
            "Name": "ducts_return_surface_area_fraction",
            "Display Name": "Ducts: Return Area Fraction",
            "Description": "The fraction of return ducts surface area in the given location. Only used if Surface Area is not provided. If the fraction is less than 1, the remaining duct area is assumed to be in conditioned space. If neither Surface Area nor Area Fraction provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "String",
            "Units": "frac",
            "Required": "false"
        },
        "ducts_number_of_return_registers" : {
            "Name": "ducts_number_of_return_registers",
            "Display Name": "Ducts: Number of Return Registers",
            "Description": "The number of return registers of the ducts. Only used to calculate default return duct surface area. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#air-distribution'>Air Distribution</a>) is used.",
            "Type": "String",
            "Units": "#",
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
            "Description": "The flow rate of the mechanical ventilation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#whole-ventilation-fan'>Whole Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "CFM",
            "Required": "false"
        },
        "mech_vent_hours_in_operation" : {
            "Name": "mech_vent_hours_in_operation",
            "Display Name": "Mechanical Ventilation: Hours In Operation",
            "Description": "The hours in operation of the mechanical ventilation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#whole-ventilation-fan'>Whole Ventilation Fan</a>) is used.",
            "Type": "String",
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
            "Description": "The fan power of the mechanical ventilation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#whole-ventilation-fan'>Whole Ventilation Fan</a>) is used.",
            "Type": "String",
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
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "mech_vent_shared_preheating_fuel" : {
            "Name": "mech_vent_shared_preheating_fuel",
            "Display Name": "Shared Mechanical Ventilation: Preheating Fuel",
            "Description": "Fuel type of the preconditioning heating equipment. Only used for a shared mechanical ventilation system. If not provided, assumes no preheating.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Type": "String",
            "Units": "COP",
            "Required": "false"
        },
        "mech_vent_shared_preheating_fraction_heat_load_served" : {
            "Name": "mech_vent_shared_preheating_fraction_heat_load_served",
            "Display Name": "Shared Mechanical Ventilation: Preheating Fraction Ventilation Heat Load Served",
            "Description": "Fraction of heating load introduced by the shared ventilation system that is met by the preconditioning heating equipment. If not provided, assumes no preheating.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "mech_vent_shared_precooling_fuel" : {
            "Name": "mech_vent_shared_precooling_fuel",
            "Display Name": "Shared Mechanical Ventilation: Precooling Fuel",
            "Description": "Fuel type of the preconditioning cooling equipment. Only used for a shared mechanical ventilation system. If not provided, assumes no precooling.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "electricity"
            ],
            "Required": "false"
        },
        "mech_vent_shared_precooling_efficiency" : {
            "Name": "mech_vent_shared_precooling_efficiency",
            "Display Name": "Shared Mechanical Ventilation: Precooling Efficiency",
            "Description": "Efficiency of the preconditioning cooling equipment. Only used for a shared mechanical ventilation system. If not provided, assumes no precooling.",
            "Type": "String",
            "Units": "COP",
            "Required": "false"
        },
        "mech_vent_shared_precooling_fraction_cool_load_served" : {
            "Name": "mech_vent_shared_precooling_fraction_cool_load_served",
            "Display Name": "Shared Mechanical Ventilation: Precooling Fraction Ventilation Cool Load Served",
            "Description": "Fraction of cooling load introduced by the shared ventilation system that is met by the preconditioning cooling equipment. If not provided, assumes no precooling.",
            "Type": "String",
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
            "Description": "The quantity of the kitchen fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "#",
            "Required": "false"
        },
        "kitchen_fans_flow_rate" : {
            "Name": "kitchen_fans_flow_rate",
            "Display Name": "Kitchen Fans: Flow Rate",
            "Description": "The flow rate of the kitchen fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "CFM",
            "Required": "false"
        },
        "kitchen_fans_hours_in_operation" : {
            "Name": "kitchen_fans_hours_in_operation",
            "Display Name": "Kitchen Fans: Hours In Operation",
            "Description": "The hours in operation of the kitchen fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "hrs/day",
            "Required": "false"
        },
        "kitchen_fans_power" : {
            "Name": "kitchen_fans_power",
            "Display Name": "Kitchen Fans: Fan Power",
            "Description": "The fan power of the kitchen fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "W",
            "Required": "false"
        },
        "kitchen_fans_start_hour" : {
            "Name": "kitchen_fans_start_hour",
            "Display Name": "Kitchen Fans: Start Hour",
            "Description": "The start hour of the kitchen fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "hr",
            "Required": "false"
        },
        "bathroom_fans_quantity" : {
            "Name": "bathroom_fans_quantity",
            "Display Name": "Bathroom Fans: Quantity",
            "Description": "The quantity of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "#",
            "Required": "false"
        },
        "bathroom_fans_flow_rate" : {
            "Name": "bathroom_fans_flow_rate",
            "Display Name": "Bathroom Fans: Flow Rate",
            "Description": "The flow rate of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "CFM",
            "Required": "false"
        },
        "bathroom_fans_hours_in_operation" : {
            "Name": "bathroom_fans_hours_in_operation",
            "Display Name": "Bathroom Fans: Hours In Operation",
            "Description": "The hours in operation of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "hrs/day",
            "Required": "false"
        },
        "bathroom_fans_power" : {
            "Name": "bathroom_fans_power",
            "Display Name": "Bathroom Fans: Fan Power",
            "Description": "The fan power of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
            "Units": "W",
            "Required": "false"
        },
        "bathroom_fans_start_hour" : {
            "Name": "bathroom_fans_start_hour",
            "Display Name": "Bathroom Fans: Start Hour",
            "Description": "The start hour of the bathroom fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#local-ventilation-fan'>Local Ventilation Fan</a>) is used.",
            "Type": "String",
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
            "Description": "The flow rate of the whole house fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#whole-house-fan'>Whole House Fan</a>) is used.",
            "Type": "String",
            "Units": "CFM",
            "Required": "false"
        },
        "whole_house_fan_power" : {
            "Name": "whole_house_fan_power",
            "Display Name": "Whole House Fan: Fan Power",
            "Description": "The fan power of the whole house fan. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#whole-house-fan'>Whole House Fan</a>) is used.",
            "Type": "String",
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
            "Description": "The location of water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-water-heating-systems'>HPXML Water Heating Systems</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "Nominal volume of water heater tank. Only applies to storage water heater, heat pump water heater, and space-heating boiler with storage tank. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#heat-pump'>Heat Pump</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#combi-boiler-w-storage'>Combi Boiler w/ Storage</a>) is used.",
            "Type": "String",
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
            "Description": "The usage of the water heater. Only applies if Efficiency Type is UniformEnergyFactor and Type is not instantaneous water heater. Does not apply to space-heating boilers. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>, <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#heat-pump'>Heat Pump</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "Ratio of energy delivered to water heater to the energy content of the fuel consumed by the water heater. Only used for non-electric storage water heaters. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "water_heater_heating_capacity" : {
            "Name": "water_heater_heating_capacity",
            "Display Name": "Water Heater: Heating Capacity",
            "Description": "Heating capacity. Only applies to storage water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>) is used.",
            "Type": "String",
            "Units": "Btu/hr",
            "Required": "false"
        },
        "water_heater_standby_loss" : {
            "Name": "water_heater_standby_loss",
            "Display Name": "Water Heater: Standby Loss",
            "Description": "The standby loss of water heater. Only applies to space-heating boilers. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#combi-boiler-w-storage'>Combi Boiler w/ Storage</a>) is used.",
            "Type": "String",
            "Units": "deg-F/hr",
            "Required": "false"
        },
        "water_heater_jacket_rvalue" : {
            "Name": "water_heater_jacket_rvalue",
            "Display Name": "Water Heater: Jacket R-value",
            "Description": "The jacket R-value of water heater. Doesn't apply to instantaneous water heater or space-heating boiler with tankless coil. If not provided, defaults to no jacket insulation.",
            "Type": "String",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "water_heater_setpoint_temperature" : {
            "Name": "water_heater_setpoint_temperature",
            "Display Name": "Water Heater: Setpoint Temperature",
            "Description": "The setpoint temperature of water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-water-heating-systems'>HPXML Water Heating Systems</a>) is used.",
            "Type": "String",
            "Units": "deg-F",
            "Required": "false"
        },
        "water_heater_num_units_served" : {
            "Name": "water_heater_num_units_served",
            "Display Name": "Water Heater: Number of Units Served",
            "Description": "Number of dwelling units served (directly or indirectly) by the water heater. Must be 1 if single-family detached. Used to apportion water heater tank losses to the unit.",
            "Type": "Integer",
            "Units": "#",
            "Default Value": "1",
            "Required": "true"
        },
        "water_heater_uses_desuperheater" : {
            "Name": "water_heater_uses_desuperheater",
            "Display Name": "Water Heater: Uses Desuperheater",
            "Description": "Requires that the dwelling unit has a air-to-air, mini-split, or ground-to-air heat pump or a central air conditioner or mini-split air conditioner. If not provided, assumes no desuperheater.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "true",
                "false"
            ],
            "Required": "false"
        },
        "water_heater_tank_model_type" : {
            "Name": "water_heater_tank_model_type",
            "Display Name": "Water Heater: Tank Type",
            "Description": "Type of tank model to use. The 'stratified' tank generally provide more accurate results, but may significantly increase run time. Applies only to storage water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#conventional-storage'>Conventional Storage</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "mixed",
                "stratified"
            ],
            "Required": "false"
        },
        "water_heater_operating_mode" : {
            "Name": "water_heater_operating_mode",
            "Display Name": "Water Heater: Operating Mode",
            "Description": "The water heater operating mode. The 'heat pump only' option only uses the heat pump, while 'hybrid/auto' allows the backup electric resistance to come on in high demand situations. This is ignored if a scheduled operating mode type is selected. Applies only to heat pump water heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#heat-pump'>Heat Pump</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "If the distribution system is Standard, the length of the piping. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#standard'>Standard</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "hot_water_distribution_recirc_control_type" : {
            "Name": "hot_water_distribution_recirc_control_type",
            "Display Name": "Hot Water Distribution: Recirculation Control Type",
            "Description": "If the distribution system is Recirculation, the type of hot water recirculation control, if any.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "If the distribution system is Recirculation, the length of the recirculation piping. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#recirculation'>Recirculation</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "hot_water_distribution_recirc_branch_piping_length" : {
            "Name": "hot_water_distribution_recirc_branch_piping_length",
            "Display Name": "Hot Water Distribution: Recirculation Branch Piping Length",
            "Description": "If the distribution system is Recirculation, the length of the recirculation branch piping. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#recirculation'>Recirculation</a>) is used.",
            "Type": "String",
            "Units": "ft",
            "Required": "false"
        },
        "hot_water_distribution_recirc_pump_power" : {
            "Name": "hot_water_distribution_recirc_pump_power",
            "Display Name": "Hot Water Distribution: Recirculation Pump Power",
            "Description": "If the distribution system is Recirculation, the recirculation pump power. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#recirculation'>Recirculation</a>) is used.",
            "Type": "String",
            "Units": "W",
            "Required": "false"
        },
        "hot_water_distribution_pipe_r" : {
            "Name": "hot_water_distribution_pipe_r",
            "Display Name": "Hot Water Distribution: Pipe Insulation Nominal R-Value",
            "Description": "Nominal R-value of the pipe insulation. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-hot-water-distribution'>HPXML Hot Water Distribution</a>) is used.",
            "Type": "String",
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
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "true",
                "false"
            ],
            "Required": "false"
        },
        "dwhr_efficiency" : {
            "Name": "dwhr_efficiency",
            "Display Name": "Drain Water Heat Recovery: Efficiency",
            "Description": "The efficiency of the drain water heat recovery.",
            "Type": "String",
            "Units": "Frac",
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
            "Description": "Multiplier on the hot water usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-water-fixtures'>HPXML Water Fixtures</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The storage volume of the solar thermal system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#detailed-inputs'>Detailed Inputs</a>) is used.",
            "Type": "String",
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
            "Description": "Module type of the PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "standard",
                "premium",
                "thin film"
            ],
            "Required": "false"
        },
        "pv_system_location" : {
            "Name": "pv_system_location",
            "Display Name": "PV System: Location",
            "Description": "Location of the PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "roof",
                "ground"
            ],
            "Required": "false"
        },
        "pv_system_tracking" : {
            "Name": "pv_system_tracking",
            "Display Name": "PV System: Tracking",
            "Description": "Type of tracking for the PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "Inverter efficiency of the PV system. If there are two PV systems, this will apply to both. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "pv_system_system_losses_fraction" : {
            "Name": "pv_system_system_losses_fraction",
            "Display Name": "PV System: System Losses Fraction",
            "Description": "System losses fraction of the PV system. If there are two PV systems, this will apply to both. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "String",
            "Units": "Frac",
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
            "Description": "Module type of the second PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "standard",
                "premium",
                "thin film"
            ],
            "Required": "false"
        },
        "pv_system_2_location" : {
            "Name": "pv_system_2_location",
            "Display Name": "PV System 2: Location",
            "Description": "Location of the second PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "roof",
                "ground"
            ],
            "Required": "false"
        },
        "pv_system_2_tracking" : {
            "Name": "pv_system_2_tracking",
            "Display Name": "PV System 2: Tracking",
            "Description": "Type of tracking for the second PV system. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-photovoltaics'>HPXML Photovoltaics</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The space type for the lithium ion battery location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The rated power output of the lithium ion battery. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "String",
            "Units": "W",
            "Required": "false"
        },
        "battery_capacity" : {
            "Name": "battery_capacity",
            "Display Name": "Battery: Nominal Capacity",
            "Description": "The nominal capacity of the lithium ion battery. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "String",
            "Units": "kWh",
            "Required": "false"
        },
        "battery_usable_capacity" : {
            "Name": "battery_usable_capacity",
            "Display Name": "Battery: Usable Capacity",
            "Description": "The usable capacity of the lithium ion battery. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "String",
            "Units": "kWh",
            "Required": "false"
        },
        "battery_round_trip_efficiency" : {
            "Name": "battery_round_trip_efficiency",
            "Display Name": "Battery: Round Trip Efficiency",
            "Description": "The round trip efficiency of the lithium ion battery. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-batteries'>HPXML Batteries</a>) is used.",
            "Type": "String",
            "Units": "Frac",
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
            "Description": "Multiplier on the lighting energy usage (interior) that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "Multiplier on the lighting energy usage (exterior) that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "Multiplier on the lighting energy usage (garage) that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The daily energy consumption for holiday lighting (exterior). If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "String",
            "Units": "kWh/day",
            "Required": "false"
        },
        "holiday_lighting_period" : {
            "Name": "holiday_lighting_period",
            "Display Name": "Holiday Lighting: Period",
            "Description": "Enter a date like 'Nov 25 - Jan 5'. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-lighting'>HPXML Lighting</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The space type for the clothes washer location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The efficiency of the clothes washer. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "String",
            "Units": "ft^3/kWh-cyc",
            "Required": "false"
        },
        "clothes_washer_rated_annual_kwh" : {
            "Name": "clothes_washer_rated_annual_kwh",
            "Display Name": "Clothes Washer: Rated Annual Consumption",
            "Description": "The annual energy consumed by the clothes washer, as rated, obtained from the EnergyGuide label. This includes both the appliance electricity consumption and the energy required for water heating. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "clothes_washer_label_electric_rate" : {
            "Name": "clothes_washer_label_electric_rate",
            "Display Name": "Clothes Washer: Label Electric Rate",
            "Description": "The annual energy consumed by the clothes washer, as rated, obtained from the EnergyGuide label. This includes both the appliance electricity consumption and the energy required for water heating. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "String",
            "Units": "$/kWh",
            "Required": "false"
        },
        "clothes_washer_label_gas_rate" : {
            "Name": "clothes_washer_label_gas_rate",
            "Display Name": "Clothes Washer: Label Gas Rate",
            "Description": "The annual energy consumed by the clothes washer, as rated, obtained from the EnergyGuide label. This includes both the appliance electricity consumption and the energy required for water heating. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "String",
            "Units": "$/therm",
            "Required": "false"
        },
        "clothes_washer_label_annual_gas_cost" : {
            "Name": "clothes_washer_label_annual_gas_cost",
            "Display Name": "Clothes Washer: Label Annual Cost with Gas DHW",
            "Description": "The annual cost of using the system under test conditions. Input is obtained from the EnergyGuide label. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "String",
            "Units": "$",
            "Required": "false"
        },
        "clothes_washer_label_usage" : {
            "Name": "clothes_washer_label_usage",
            "Display Name": "Clothes Washer: Label Usage",
            "Description": "The clothes washer loads per week. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "String",
            "Units": "cyc/wk",
            "Required": "false"
        },
        "clothes_washer_capacity" : {
            "Name": "clothes_washer_capacity",
            "Display Name": "Clothes Washer: Drum Volume",
            "Description": "Volume of the washer drum. Obtained from the EnergyStar website or the manufacturer's literature. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "String",
            "Units": "ft^3",
            "Required": "false"
        },
        "clothes_washer_usage_multiplier" : {
            "Name": "clothes_washer_usage_multiplier",
            "Display Name": "Clothes Washer: Usage Multiplier",
            "Description": "Multiplier on the clothes washer energy and hot water usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-washer'>HPXML Clothes Washer</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The space type for the clothes dryer location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-dryer'>HPXML Clothes Dryer</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The efficiency of the clothes dryer. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-dryer'>HPXML Clothes Dryer</a>) is used.",
            "Type": "String",
            "Units": "lb/kWh",
            "Required": "false"
        },
        "clothes_dryer_vented_flow_rate" : {
            "Name": "clothes_dryer_vented_flow_rate",
            "Display Name": "Clothes Dryer: Vented Flow Rate",
            "Description": "The exhaust flow rate of the vented clothes dryer. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-dryer'>HPXML Clothes Dryer</a>) is used.",
            "Type": "String",
            "Units": "CFM",
            "Required": "false"
        },
        "clothes_dryer_usage_multiplier" : {
            "Name": "clothes_dryer_usage_multiplier",
            "Display Name": "Clothes Dryer: Usage Multiplier",
            "Description": "Multiplier on the clothes dryer energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-clothes-dryer'>HPXML Clothes Dryer</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The space type for the dishwasher location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The efficiency of the dishwasher. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "String",
            "Units": "RatedAnnualkWh or EnergyFactor",
            "Required": "false"
        },
        "dishwasher_label_electric_rate" : {
            "Name": "dishwasher_label_electric_rate",
            "Display Name": "Dishwasher: Label Electric Rate",
            "Description": "The label electric rate of the dishwasher. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "String",
            "Units": "$/kWh",
            "Required": "false"
        },
        "dishwasher_label_gas_rate" : {
            "Name": "dishwasher_label_gas_rate",
            "Display Name": "Dishwasher: Label Gas Rate",
            "Description": "The label gas rate of the dishwasher. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "String",
            "Units": "$/therm",
            "Required": "false"
        },
        "dishwasher_label_annual_gas_cost" : {
            "Name": "dishwasher_label_annual_gas_cost",
            "Display Name": "Dishwasher: Label Annual Gas Cost",
            "Description": "The label annual gas cost of the dishwasher. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "String",
            "Units": "$",
            "Required": "false"
        },
        "dishwasher_label_usage" : {
            "Name": "dishwasher_label_usage",
            "Display Name": "Dishwasher: Label Usage",
            "Description": "The dishwasher loads per week. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "String",
            "Units": "cyc/wk",
            "Required": "false"
        },
        "dishwasher_place_setting_capacity" : {
            "Name": "dishwasher_place_setting_capacity",
            "Display Name": "Dishwasher: Number of Place Settings",
            "Description": "The number of place settings for the unit. Data obtained from manufacturer's literature. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "String",
            "Units": "#",
            "Required": "false"
        },
        "dishwasher_usage_multiplier" : {
            "Name": "dishwasher_usage_multiplier",
            "Display Name": "Dishwasher: Usage Multiplier",
            "Description": "Multiplier on the dishwasher energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-dishwasher'>HPXML Dishwasher</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The space type for the refrigerator location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The EnergyGuide rated annual energy consumption for a refrigerator. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "refrigerator_usage_multiplier" : {
            "Name": "refrigerator_usage_multiplier",
            "Display Name": "Refrigerator: Usage Multiplier",
            "Description": "Multiplier on the refrigerator energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The space type for the extra refrigerator location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The EnergyGuide rated annual energy consumption for an extra rrefrigerator. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "extra_refrigerator_usage_multiplier" : {
            "Name": "extra_refrigerator_usage_multiplier",
            "Display Name": "Extra Refrigerator: Usage Multiplier",
            "Description": "Multiplier on the extra refrigerator energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-refrigerators'>HPXML Refrigerators</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The space type for the freezer location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-freezers'>HPXML Freezers</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "The EnergyGuide rated annual energy consumption for a freezer. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-freezers'>HPXML Freezers</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "freezer_usage_multiplier" : {
            "Name": "freezer_usage_multiplier",
            "Display Name": "Freezer: Usage Multiplier",
            "Description": "Multiplier on the freezer energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-freezers'>HPXML Freezers</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The space type for the cooking range/oven location. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-cooking-range-oven'>HPXML Cooking Range/Oven</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
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
            "Description": "Whether the cooking range is induction. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-cooking-range-oven'>HPXML Cooking Range/Oven</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "true",
                "false"
            ],
            "Required": "false"
        },
        "cooking_range_oven_is_convection" : {
            "Name": "cooking_range_oven_is_convection",
            "Display Name": "Cooking Range/Oven: Is Convection",
            "Description": "Whether the oven is convection. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-cooking-range-oven'>HPXML Cooking Range/Oven</a>) is used.",
            "Type": "Choice",
            "Units": None,
            "Choices": [
                "auto",
                "true",
                "false"
            ],
            "Required": "false"
        },
        "cooking_range_oven_usage_multiplier" : {
            "Name": "cooking_range_oven_usage_multiplier",
            "Display Name": "Cooking Range/Oven: Usage Multiplier",
            "Description": "Multiplier on the cooking range/oven energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-cooking-range-oven'>HPXML Cooking Range/Oven</a>) is used.",
            "Type": "String",
            "Units": None,
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
        "ceiling_fan_efficiency" : {
            "Name": "ceiling_fan_efficiency",
            "Display Name": "Ceiling Fan: Efficiency",
            "Description": "The efficiency rating of the ceiling fan(s) at medium speed. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-ceiling-fans'>HPXML Ceiling Fans</a>) is used.",
            "Type": "String",
            "Units": "CFM/W",
            "Required": "false"
        },
        "ceiling_fan_quantity" : {
            "Name": "ceiling_fan_quantity",
            "Display Name": "Ceiling Fan: Quantity",
            "Description": "Total number of ceiling fans. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-ceiling-fans'>HPXML Ceiling Fans</a>) is used.",
            "Type": "String",
            "Units": "#",
            "Required": "false"
        },
        "ceiling_fan_cooling_setpoint_temp_offset" : {
            "Name": "ceiling_fan_cooling_setpoint_temp_offset",
            "Display Name": "Ceiling Fan: Cooling Setpoint Temperature Offset",
            "Description": "The cooling setpoint temperature offset during months when the ceiling fans are operating. Only applies if ceiling fan quantity is greater than zero. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-ceiling-fans'>HPXML Ceiling Fans</a>) is used.",
            "Type": "String",
            "Units": "deg-F",
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
        "misc_plug_loads_other_annual_kwh" : {
            "Name": "misc_plug_loads_other_annual_kwh",
            "Display Name": "Misc Plug Loads: Other Annual kWh",
            "Description": "The annual energy consumption of the other residual plug loads. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "misc_plug_loads_other_frac_sensible" : {
            "Name": "misc_plug_loads_other_frac_sensible",
            "Display Name": "Misc Plug Loads: Other Sensible Fraction",
            "Description": "Fraction of other residual plug loads' internal gains that are sensible. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "misc_plug_loads_other_frac_latent" : {
            "Name": "misc_plug_loads_other_frac_latent",
            "Display Name": "Misc Plug Loads: Other Latent Fraction",
            "Description": "Fraction of other residual plug loads' internal gains that are latent. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "misc_plug_loads_other_usage_multiplier" : {
            "Name": "misc_plug_loads_other_usage_multiplier",
            "Display Name": "Misc Plug Loads: Other Usage Multiplier",
            "Description": "Multiplier on the other energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the well pump plug loads. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "misc_plug_loads_well_pump_usage_multiplier" : {
            "Name": "misc_plug_loads_well_pump_usage_multiplier",
            "Display Name": "Misc Plug Loads: Well Pump Usage Multiplier",
            "Description": "Multiplier on the well pump energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the electric vehicle plug loads. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "misc_plug_loads_vehicle_usage_multiplier" : {
            "Name": "misc_plug_loads_vehicle_usage_multiplier",
            "Display Name": "Misc Plug Loads: Vehicle Usage Multiplier",
            "Description": "Multiplier on the electric vehicle energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-plug-loads'>HPXML Plug Loads</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the fuel loads grill. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "String",
            "Units": "therm/yr",
            "Required": "false"
        },
        "misc_fuel_loads_grill_usage_multiplier" : {
            "Name": "misc_fuel_loads_grill_usage_multiplier",
            "Display Name": "Misc Fuel Loads: Grill Usage Multiplier",
            "Description": "Multiplier on the fuel loads grill energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the fuel loads lighting. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>)is used.",
            "Type": "String",
            "Units": "therm/yr",
            "Required": "false"
        },
        "misc_fuel_loads_lighting_usage_multiplier" : {
            "Name": "misc_fuel_loads_lighting_usage_multiplier",
            "Display Name": "Misc Fuel Loads: Lighting Usage Multiplier",
            "Description": "Multiplier on the fuel loads lighting energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the fuel loads fireplace. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "String",
            "Units": "therm/yr",
            "Required": "false"
        },
        "misc_fuel_loads_fireplace_frac_sensible" : {
            "Name": "misc_fuel_loads_fireplace_frac_sensible",
            "Display Name": "Misc Fuel Loads: Fireplace Sensible Fraction",
            "Description": "Fraction of fireplace residual fuel loads' internal gains that are sensible. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "misc_fuel_loads_fireplace_frac_latent" : {
            "Name": "misc_fuel_loads_fireplace_frac_latent",
            "Display Name": "Misc Fuel Loads: Fireplace Latent Fraction",
            "Description": "Fraction of fireplace residual fuel loads' internal gains that are latent. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "String",
            "Units": "Frac",
            "Required": "false"
        },
        "misc_fuel_loads_fireplace_usage_multiplier" : {
            "Name": "misc_fuel_loads_fireplace_usage_multiplier",
            "Display Name": "Misc Fuel Loads: Fireplace Usage Multiplier",
            "Description": "Multiplier on the fuel loads fireplace energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#hpxml-fuel-loads'>HPXML Fuel Loads</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the pool pump. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#pool-pump'>Pool Pump</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "pool_pump_usage_multiplier" : {
            "Name": "pool_pump_usage_multiplier",
            "Display Name": "Pool: Pump Usage Multiplier",
            "Description": "Multiplier on the pool pump energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#pool-pump'>Pool Pump</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the electric resistance pool heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#pool-heater'>Pool Heater</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "pool_heater_annual_therm" : {
            "Name": "pool_heater_annual_therm",
            "Display Name": "Pool: Heater Annual therm",
            "Description": "The annual energy consumption of the gas fired pool heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#pool-heater'>Pool Heater</a>) is used.",
            "Type": "String",
            "Units": "therm/yr",
            "Required": "false"
        },
        "pool_heater_usage_multiplier" : {
            "Name": "pool_heater_usage_multiplier",
            "Display Name": "Pool: Heater Usage Multiplier",
            "Description": "Multiplier on the pool heater energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#pool-heater'>Pool Heater</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the permanent spa pump. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#permanent-spa-pump'>Permanent Spa Pump</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "permanent_spa_pump_usage_multiplier" : {
            "Name": "permanent_spa_pump_usage_multiplier",
            "Display Name": "Permanent Spa: Pump Usage Multiplier",
            "Description": "Multiplier on the permanent spa pump energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#permanent-spa-pump'>Permanent Spa Pump</a>) is used.",
            "Type": "String",
            "Units": None,
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
            "Description": "The annual energy consumption of the electric resistance permanent spa heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#permanent-spa-heater'>Permanent Spa Heater</a>) is used.",
            "Type": "String",
            "Units": "kWh/yr",
            "Required": "false"
        },
        "permanent_spa_heater_annual_therm" : {
            "Name": "permanent_spa_heater_annual_therm",
            "Display Name": "Permanent Spa: Heater Annual therm",
            "Description": "The annual energy consumption of the gas fired permanent spa heater. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#permanent-spa-heater'>Permanent Spa Heater</a>) is used.",
            "Type": "String",
            "Units": "therm/yr",
            "Required": "false"
        },
        "permanent_spa_heater_usage_multiplier" : {
            "Name": "permanent_spa_heater_usage_multiplier",
            "Display Name": "Permanent Spa: Heater Usage Multiplier",
            "Description": "Multiplier on the permanent spa heater energy usage that can reflect, e.g., high/low usage occupants. If not provided, the OS-HPXML default (see <a href='https://openstudio-hpxml.readthedocs.io/en/v1.7.0/workflow_inputs.html#permanent-spa-heater'>Permanent Spa Heater</a>) is used.",
            "Type": "String",
            "Units": None,
            "Required": "false"
        },
        "geometry_unit_cfa_bin" : {
            "Name": "geometry_unit_cfa_bin",
            "Display Name": "Geometry: Unit Conditioned Floor Area Bin",
            "Description": "E.g., '2000-2499'.",
            "Type": "String",
            "Default Value": "2000-2499",
            "Required": "true"
        },
        "geometry_unit_cfa" : {
            "Name": "geometry_unit_cfa",
            "Display Name": "Geometry: Unit Conditioned Floor Area",
            "Description": "E.g., '2000' or 'auto'.",
            "Type": "String",
            "Units": "sqft",
            "Default Value": "2000",
            "Required": "true"
        },
        "vintage" : {
            "Name": "vintage",
            "Display Name": "Building Construction: Vintage",
            "Description": "The building vintage, used for informational purposes only.",
            "Type": "String",
            "Required": "false"
        },
        "exterior_finish_r" : {
            "Name": "exterior_finish_r",
            "Display Name": "Building Construction: Exterior Finish R-Value",
            "Description": "R-value of the exterior finish.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0.6",
            "Required": "true"
        },
        "geometry_unit_level" : {
            "Name": "geometry_unit_level",
            "Display Name": "Geometry: Unit Level",
            "Description": "The level of the unit. This is required for apartment units.",
            "Type": "Choice",
            "Choices": [
                "Bottom",
                "Middle",
                "Top"
            ],
            "Required": "false"
        },
        "geometry_unit_horizontal_location" : {
            "Name": "geometry_unit_horizontal_location",
            "Display Name": "Geometry: Unit Horizontal Location",
            "Description": "The horizontal location of the unit when viewing the front of the building. This is required for single-family attached and apartment units.",
            "Type": "Choice",
            "Choices": [
                "None",
                "Left",
                "Middle",
                "Right"
            ],
            "Required": "false"
        },
        "geometry_num_floors_above_grade" : {
            "Name": "geometry_num_floors_above_grade",
            "Display Name": "Geometry: Number of Floors Above Grade",
            "Description": "The number of floors above grade (in the unit if single-family detached or single-family attached, and in the building if apartment unit). Conditioned attics are included.",
            "Type": "Integer",
            "Units": "#",
            "Default Value": "2",
            "Required": "true"
        },
        "geometry_corridor_position" : {
            "Name": "geometry_corridor_position",
            "Display Name": "Geometry: Corridor Position",
            "Description": "The position of the corridor. Only applies to single-family attached and apartment units. Exterior corridors are shaded, but not enclosed. Interior corridors are enclosed and conditioned.",
            "Type": "Choice",
            "Choices": [
                "Double-Loaded Interior",
                "Double Exterior",
                "Single Exterior (Front)",
                "None"
            ],
            "Required": "true"
        },
        "geometry_corridor_width" : {
            "Name": "geometry_corridor_width",
            "Display Name": "Geometry: Corridor Width",
            "Description": "The width of the corridor. Only applies to apartment units.",
            "Type": "Double",
            "Units": "ft",
            "Default Value": "10",
            "Required": "true"
        },
        "wall_continuous_exterior_r" : {
            "Name": "wall_continuous_exterior_r",
            "Display Name": "Wall: Continuous Exterior Insulation Nominal R-value",
            "Description": "Nominal R-value for the wall continuous exterior insulation.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Required": "false"
        },
        "ceiling_insulation_r" : {
            "Name": "ceiling_insulation_r",
            "Display Name": "Ceiling: Insulation Nominal R-value",
            "Description": "Nominal R-value for the ceiling (attic floor).",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "rim_joist_continuous_exterior_r" : {
            "Name": "rim_joist_continuous_exterior_r",
            "Display Name": "Rim Joist: Continuous Exterior Insulation Nominal R-value",
            "Description": "Nominal R-value for the rim joist continuous exterior insulation. Only applies to basements/crawlspaces.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "rim_joist_continuous_interior_r" : {
            "Name": "rim_joist_continuous_interior_r",
            "Display Name": "Rim Joist: Continuous Interior Insulation Nominal R-value",
            "Description": "Nominal R-value for the rim joist continuous interior insulation that runs parallel to floor joists. Only applies to basements/crawlspaces.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "rim_joist_assembly_interior_r" : {
            "Name": "rim_joist_assembly_interior_r",
            "Display Name": "Rim Joist: Interior Assembly R-value",
            "Description": "Assembly R-value for the rim joist assembly interior insulation that runs perpendicular to floor joists. Only applies to basements/crawlspaces.",
            "Type": "Double",
            "Units": "h-ft^2-R/Btu",
            "Default Value": "0",
            "Required": "true"
        },
        "air_leakage_percent_reduction" : {
            "Name": "air_leakage_percent_reduction",
            "Display Name": "Air Leakage: Value Reduction",
            "Description": "Reduction (%) on the air exchange rate value.",
            "Type": "Double",
            "Required": "false"
        },
        "misc_plug_loads_other_2_usage_multiplier" : {
            "Name": "misc_plug_loads_other_2_usage_multiplier",
            "Display Name": "Plug Loads: Other Usage Multiplier 2",
            "Description": "Additional multiplier on the other energy usage that can reflect, e.g., high/low usage occupants.",
            "Type": "Double",
            "Default Value": "1",
            "Required": "true"
        },
        "misc_plug_loads_well_pump_2_usage_multiplier" : {
            "Name": "misc_plug_loads_well_pump_2_usage_multiplier",
            "Display Name": "Plug Loads: Well Pump Usage Multiplier 2",
            "Description": "Additional multiplier on the well pump energy usage that can reflect, e.g., high/low usage occupants.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "misc_plug_loads_vehicle_2_usage_multiplier" : {
            "Name": "misc_plug_loads_vehicle_2_usage_multiplier",
            "Display Name": "Plug Loads: Vehicle Usage Multiplier 2",
            "Description": "Additional multiplier on the electric vehicle energy usage that can reflect, e.g., high/low usage occupants.",
            "Type": "Double",
            "Default Value": "0",
            "Required": "true"
        },
        "hvac_control_heating_weekday_setpoint_temp" : {
            "Name": "hvac_control_heating_weekday_setpoint_temp",
            "Display Name": "Heating Setpoint: Weekday Temperature",
            "Description": "Specify the weekday heating setpoint temperature.",
            "Type": "Double",
            "Units": "deg-F",
            "Default Value": "71",
            "Required": "true"
        },
        "hvac_control_heating_weekend_setpoint_temp" : {
            "Name": "hvac_control_heating_weekend_setpoint_temp",
            "Display Name": "Heating Setpoint: Weekend Temperature",
            "Description": "Specify the weekend heating setpoint temperature.",
            "Type": "Double",
            "Units": "deg-F",
            "Default Value": "71",
            "Required": "true"
        },
        "hvac_control_heating_weekday_setpoint_offset_magnitude" : {
            "Name": "hvac_control_heating_weekday_setpoint_offset_magnitude",
            "Display Name": "Heating Setpoint: Weekday Offset Magnitude",
            "Description": "Specify the weekday heating offset magnitude.",
            "Type": "Double",
            "Units": "deg-F",
            "Default Value": "0",
            "Required": "true"
        },
        "hvac_control_heating_weekend_setpoint_offset_magnitude" : {
            "Name": "hvac_control_heating_weekend_setpoint_offset_magnitude",
            "Display Name": "Heating Setpoint: Weekend Offset Magnitude",
            "Description": "Specify the weekend heating offset magnitude.",
            "Type": "Double",
            "Units": "deg-F",
            "Default Value": "0",
            "Required": "true"
        },
        "hvac_control_heating_weekday_setpoint_schedule" : {
            "Name": "hvac_control_heating_weekday_setpoint_schedule",
            "Display Name": "Heating Setpoint: Weekday Schedule",
            "Description": "Specify the 24-hour comma-separated weekday heating schedule of 0s and 1s.",
            "Type": "String",
            "Default Value": "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0",
            "Required": "true"
        },
        "hvac_control_heating_weekend_setpoint_schedule" : {
            "Name": "hvac_control_heating_weekend_setpoint_schedule",
            "Display Name": "Heating Setpoint: Weekend Schedule",
            "Description": "Specify the 24-hour comma-separated weekend heating schedule of 0s and 1s.",
            "Type": "String",
            "Default Value": "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0",
            "Required": "true"
        },
        "use_auto_heating_season" : {
            "Name": "use_auto_heating_season",
            "Display Name": "Use Auto Heating Season",
            "Description": "Specifies whether to automatically define the heating season based on the weather file.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "hvac_control_cooling_weekday_setpoint_temp" : {
            "Name": "hvac_control_cooling_weekday_setpoint_temp",
            "Display Name": "Cooling Setpoint: Weekday Temperature",
            "Description": "Specify the weekday cooling setpoint temperature.",
            "Type": "Double",
            "Units": "deg-F",
            "Default Value": "76",
            "Required": "true"
        },
        "hvac_control_cooling_weekend_setpoint_temp" : {
            "Name": "hvac_control_cooling_weekend_setpoint_temp",
            "Display Name": "Cooling Setpoint: Weekend Temperature",
            "Description": "Specify the weekend cooling setpoint temperature.",
            "Type": "Double",
            "Units": "deg-F",
            "Default Value": "76",
            "Required": "true"
        },
        "hvac_control_cooling_weekday_setpoint_offset_magnitude" : {
            "Name": "hvac_control_cooling_weekday_setpoint_offset_magnitude",
            "Display Name": "Cooling Setpoint: Weekday Offset Magnitude",
            "Description": "Specify the weekday cooling offset magnitude.",
            "Type": "Double",
            "Units": "deg-F",
            "Default Value": "0",
            "Required": "true"
        },
        "hvac_control_cooling_weekend_setpoint_offset_magnitude" : {
            "Name": "hvac_control_cooling_weekend_setpoint_offset_magnitude",
            "Display Name": "Cooling Setpoint: Weekend Offset Magnitude",
            "Description": "Specify the weekend cooling offset magnitude.",
            "Type": "Double",
            "Units": "deg-F",
            "Default Value": "0",
            "Required": "true"
        },
        "hvac_control_cooling_weekday_setpoint_schedule" : {
            "Name": "hvac_control_cooling_weekday_setpoint_schedule",
            "Display Name": "Cooling Setpoint: Weekday Schedule",
            "Description": "Specify the 24-hour comma-separated weekday cooling schedule of 0s and 1s.",
            "Type": "String",
            "Default Value": "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0",
            "Required": "true"
        },
        "hvac_control_cooling_weekend_setpoint_schedule" : {
            "Name": "hvac_control_cooling_weekend_setpoint_schedule",
            "Display Name": "Cooling Setpoint: Weekend Schedule",
            "Description": "Specify the 24-hour comma-separated weekend cooling schedule of 0s and 1s.",
            "Type": "String",
            "Default Value": "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0",
            "Required": "true"
        },
        "use_auto_cooling_season" : {
            "Name": "use_auto_cooling_season",
            "Display Name": "Use Auto Cooling Season",
            "Description": "Specifies whether to automatically define the cooling season based on the weather file.",
            "Type": "Boolean",
            "Default Value": "false",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "true"
        },
        "heating_system_has_flue_or_chimney" : {
            "Name": "heating_system_has_flue_or_chimney",
            "Display Name": "Heating System: Has Flue or Chimney",
            "Description": "Whether the heating system has a flue or chimney.",
            "Type": "String",
            "Default Value": "auto",
            "Required": "true"
        },
        "heating_system_2_has_flue_or_chimney" : {
            "Name": "heating_system_2_has_flue_or_chimney",
            "Display Name": "Heating System 2: Has Flue or Chimney",
            "Description": "Whether the second heating system has a flue or chimney.",
            "Type": "String",
            "Default Value": "auto",
            "Required": "true"
        },
        "water_heater_has_flue_or_chimney" : {
            "Name": "water_heater_has_flue_or_chimney",
            "Display Name": "Water Heater: Has Flue or Chimney",
            "Description": "Whether the water heater has a flue or chimney.",
            "Type": "String",
            "Default Value": "auto",
            "Required": "true"
        },
        "heating_system_rated_cfm_per_ton" : {
            "Name": "heating_system_rated_cfm_per_ton",
            "Display Name": "Heating System: Rated CFM Per Ton",
            "Description": "The rated cfm per ton of the heating system.",
            "Type": "Double",
            "Units": "cfm/ton",
            "Required": "false"
        },
        "heating_system_actual_cfm_per_ton" : {
            "Name": "heating_system_actual_cfm_per_ton",
            "Display Name": "Heating System: Actual CFM Per Ton",
            "Description": "The actual cfm per ton of the heating system.",
            "Type": "Double",
            "Units": "cfm/ton",
            "Required": "false"
        },
        "cooling_system_rated_cfm_per_ton" : {
            "Name": "cooling_system_rated_cfm_per_ton",
            "Display Name": "Cooling System: Rated CFM Per Ton",
            "Description": "The rated cfm per ton of the cooling system.",
            "Type": "Double",
            "Units": "cfm/ton",
            "Required": "false"
        },
        "cooling_system_actual_cfm_per_ton" : {
            "Name": "cooling_system_actual_cfm_per_ton",
            "Display Name": "Cooling System: Actual CFM Per Ton",
            "Description": "The actual cfm per ton of the cooling system.",
            "Type": "Double",
            "Units": "cfm/ton",
            "Required": "false"
        },
        "cooling_system_frac_manufacturer_charge" : {
            "Name": "cooling_system_frac_manufacturer_charge",
            "Display Name": "Cooling System: Fraction of Manufacturer Recommended Charge",
            "Description": "The fraction of manufacturer recommended charge of the cooling system.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_rated_cfm_per_ton" : {
            "Name": "heat_pump_rated_cfm_per_ton",
            "Display Name": "Heat Pump: Rated CFM Per Ton",
            "Description": "The rated cfm per ton of the heat pump.",
            "Type": "Double",
            "Units": "cfm/ton",
            "Required": "false"
        },
        "heat_pump_actual_cfm_per_ton" : {
            "Name": "heat_pump_actual_cfm_per_ton",
            "Display Name": "Heat Pump: Actual CFM Per Ton",
            "Description": "The actual cfm per ton of the heat pump.",
            "Type": "Double",
            "Units": "cfm/ton",
            "Required": "false"
        },
        "heat_pump_frac_manufacturer_charge" : {
            "Name": "heat_pump_frac_manufacturer_charge",
            "Display Name": "Heat Pump: Fraction of Manufacturer Recommended Charge",
            "Description": "The fraction of manufacturer recommended charge of the heat pump.",
            "Type": "Double",
            "Units": "Frac",
            "Required": "false"
        },
        "heat_pump_backup_use_existing_system" : {
            "Name": "heat_pump_backup_use_existing_system",
            "Display Name": "Heat Pump: Backup Use Existing System",
            "Description": "Whether the heat pump uses the existing system as backup.",
            "Type": "Boolean",
            "Choices": [
                "true",
                "false"
            ],
            "Required": "false"
        },
        }
    