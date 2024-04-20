import math

from viktor import ViktorController
from viktor.parametrization import BooleanField
from viktor.parametrization import DynamicArray
from viktor.parametrization import GeoPointField
from viktor.parametrization import LineBreak
from viktor.parametrization import NumberField
from viktor.parametrization import OptionField
from viktor.parametrization import OutputField
from viktor.parametrization import Text
from viktor.parametrization import ViktorParametrization
from viktor.views import DataGroup
from viktor.views import DataItem
from viktor.views import MapAndDataResult
from viktor.views import MapAndDataView
from viktor.views import MapPoint

from app.speckle_functions import get_speckle_concrete_names
from app.speckle_functions import get_speckle_concrete_volume_dataframe
from app.speckle_functions import get_speckle_lighting_dataframe
from app.speckle_functions import get_speckle_lighting_names

PROJECT_LOCATION = MapPoint(41.390608, 2.177505)

def haversine_distance(coord1, coord2):
    """
    Calculate the Haversine distance between two latitude-longitude coordinates.

    Args:
        coord1: A tuple of two floats representing the first coordinate (latitude, longitude).
        coord2: A tuple of two floats representing the second coordinate (latitude, longitude).

    Returns:
        The distance in kilometers between the two coordinates.
    """
    lat1, lon1 = coord1.lat, coord1.lon
    lat2, lon2 = coord2.lat, coord2.lon

    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of the Earth in kilometers
    R = 6371

    # Distance in kilometers
    distance = R * c
    return distance




def get_distance_to_project_location(params, **kwargs):
    if params.constructor_location:
        return f"{haversine_distance(params.constructor_location, PROJECT_LOCATION):.0f} km"
    return None


class Parametrization(ViktorParametrization):
    welcome = Text("Welcome to the open bidding application! Please start by filling in the location of your distribution"
                   " facility, and your distance to the project will be calculated. Then proceed by filling your price estimate "
                   "for each of the different items.")
    constructor_header = Text("# Location")
    constructor_location = GeoPointField("Constructor location")
    distance_to_project = OutputField("Distance to project", value=get_distance_to_project_location)
    concrete_header = Text("# Concrete")
    concrete = DynamicArray("Concrete bids")
    concrete.pre_cast_option = BooleanField("Pre-cast option")
    concrete.line_break = LineBreak()
    concrete.concrete_type = OptionField("Concrete type", options=get_speckle_concrete_names())
    concrete.lead_time = NumberField("Lead time", suffix="weeks")
    concrete.price_per_unit = NumberField("Price per m³", suffix="€ / m³")
    line_break = LineBreak()
    lighting_header = Text("# Lighting")
    lighting = DynamicArray("Lighting bids")
    lighting.lighting_type = OptionField("Lighting type", options=get_speckle_lighting_names())
    lighting.lead_time = NumberField("Lead time", suffix="weeks")
    lighting.price_per_unit = NumberField("Price per piece", suffix="€")


class Controller(ViktorController):
    label = 'Bid'
    parametrization = Parametrization

    @MapAndDataView("Constructor location", duration_guess=1)
    def constructor_location(self, params, **kwargs):
        map_elements = [PROJECT_LOCATION]
        if params.constructor_location:
            map_elements.append(MapPoint.from_geo_point(params.constructor_location))

        concrete_data = get_speckle_concrete_volume_dataframe()
        lighting_data = get_speckle_lighting_dataframe()
        return MapAndDataResult(features=map_elements, data=DataGroup(
            DataItem("Concrete", value=f"{concrete_data.sum():.0f}", suffix="m³", subgroup=DataGroup(
                *(DataItem(key, value=f"{value:.0f}", suffix="m³") for key, value in concrete_data.items())
            )),
            DataItem("Lighting", value=f"{lighting_data.sum():.0f}", suffix="pieces", subgroup=DataGroup(
                *(DataItem(key, value=f"{value:.0f}", suffix="pieces") for key, value in lighting_data.items())
            ))
        ))

