from collections import defaultdict

import plotly.graph_objects as go
from viktor import ViktorController
from viktor.api_v1 import API
from viktor.parametrization import ActionButton
from viktor.parametrization import ChildEntityManager
from viktor.parametrization import Text
from viktor.parametrization import ViktorParametrization
from viktor.views import PlotlyResult
from viktor.views import PlotlyView

from app.speckle_functions import get_speckle_concrete_volume_dataframe
from app.speckle_functions import get_speckle_lighting_dataframe
from app.speckle_functions import push_prices_to_speckle


class Parametrization(ViktorParametrization):
    """Viktor parametrization."""

    text1 = Text(
        """
# Welcome to Open Bid!
This app allows any contractor to bid for construction.
        """
    )
    button = ActionButton("Update prices in model", method="push_prices_to_model")
    childs = ChildEntityManager("MyEntityType")


class Controller(ViktorController):
    """Viktor Controller."""

    children = ["MyEntityType"]
    show_children_as = "Table"
    label = "Project"
    parametrization = Parametrization
    viktor_enforce_field_constraints = True

    @staticmethod
    def push_prices_to_model(params, entity_id, **kwargs):
        api = API()
        children = api.get_entity_children(entity_id=entity_id)
        contractor_concrete_prices = []
        contractor_lighting_prices = []
        concrete_prices_dict = defaultdict(dict)
        lighting_prices_dict = defaultdict(dict)
        for child in children:
            contractor_name = child.name
            for concrete_type_row in child.last_saved_params.concrete:
                contractor_concrete_prices.append(
                    {
                        "Contractor name": contractor_name,
                        "Concrete pre cast option": concrete_type_row.pre_cast_option,
                        "Concrete type": concrete_type_row.concrete_type,
                        "Concrete lead time": concrete_type_row.lead_time,
                        "Concrete price per unit": concrete_type_row.price_per_unit,
                    }
                )
                concrete_prices_dict[concrete_type_row.concrete_type].update(
                    {contractor_name: concrete_type_row.price_per_unit}
                )
            for lighting_type_row in child.last_saved_params.lighting:
                contractor_lighting_prices.append(
                    {
                        "Contractor name": contractor_name,
                        "Lighting type": lighting_type_row.lighting_type,
                        "Lighting lead time": lighting_type_row.lead_time,
                        "Lighting price per unit": lighting_type_row.price_per_unit,
                    }
                )
                lighting_prices_dict[lighting_type_row.lighting_type].update(
                    {contractor_name: lighting_type_row.price_per_unit}
                )
        push_prices_to_speckle("concrete", concrete_prices_dict)
        push_prices_to_speckle("lighting", lighting_prices_dict)
        return

    @PlotlyView("Concrete price comparison", duration_guess=1)
    def price_comparison(self, params, entity_id, **kwargs):
        concrete_data = get_speckle_concrete_volume_dataframe()
        lighting_data = get_speckle_lighting_dataframe()

        api = API()
        children = api.get_entity_children(entity_id=entity_id)
        contractor_concrete_prices = []
        contractor_lighting_prices = []
        concrete_prices_dict = defaultdict(list)
        lighting_prices_dict = defaultdict(list)
        for child in children:
            contractor_name = child.name
            for concrete_type_row in child.last_saved_params.concrete:
                contractor_concrete_prices.append(
                    {
                        "Contractor name": contractor_name,
                        "Concrete pre cast option": concrete_type_row.pre_cast_option,
                        "Concrete type": concrete_type_row.concrete_type,
                        "Concrete lead time": concrete_type_row.lead_time,
                        "Concrete price per unit": concrete_type_row.price_per_unit,
                        "Concrete volume": concrete_data[concrete_type_row.concrete_type],
                        "Concrete total price": concrete_data[concrete_type_row.concrete_type]
                        * concrete_type_row.price_per_unit,
                    }
                )
                concrete_prices_dict[concrete_type_row.concrete_type].append(concrete_type_row.price_per_unit)
            for lighting_type_row in child.last_saved_params.lighting:
                contractor_lighting_prices.append(
                    {
                        "Contractor name": contractor_name,
                        "Lighting type": lighting_type_row.lighting_type,
                        "Lighting lead time": lighting_type_row.lead_time,
                        "Lighting price per unit": lighting_type_row.price_per_unit,
                        "Lighting volume": lighting_data[lighting_type_row.lighting_type],
                        "Lighting total price": lighting_data[lighting_type_row.lighting_type]
                        * lighting_type_row.price_per_unit,
                    }
                )
                lighting_prices_dict[lighting_type_row.lighting_type].append(lighting_type_row.price_per_unit)
        print(contractor_concrete_prices)

        print(contractor_lighting_prices)

        # Extracting unique contractors and concrete types
        contractors = list(set(entry["Contractor name"] for entry in contractor_concrete_prices))
        concrete_types = list(set(entry["Concrete type"] for entry in contractor_concrete_prices))

        # Initialize a dictionary to store the price per unit for each contractor and concrete type
        price_per_unit_dict = {
            contractor: {concrete_type: 0 for concrete_type in concrete_types} for contractor in contractors
        }

        # Fill the dictionary with the price per unit data
        for entry in contractor_concrete_prices:
            contractor = entry["Contractor name"]
            concrete_type = entry["Concrete type"]
            price_per_unit = entry["Concrete total price"]
            price_per_unit_dict[contractor][concrete_type] = price_per_unit

        # Create a stacked bar chart trace for each contractor
        traces = []
        for contractor in contractors:
            prices = [price_per_unit_dict[contractor][concrete_type] for concrete_type in concrete_types]
            trace = go.Bar(x=concrete_types, y=prices, name=contractor)
            traces.append(trace)

        # Create the figure
        fig = go.Figure(data=traces)

        # Update layout
        fig.update_layout(
            title="Concrete Prices by Contractor and Type",
            xaxis_title="Concrete Type",
            yaxis_title="Concrete Price",
            barmode="group",
        )

        return PlotlyResult(fig.to_json())

    @PlotlyView("Lighting price comparison", duration_guess=1)
    def price_comparison_lighting(self, params, entity_id, **kwargs):
        concrete_data = get_speckle_concrete_volume_dataframe()
        lighting_data = get_speckle_lighting_dataframe()

        api = API()
        children = api.get_entity_children(entity_id=entity_id)
        contractor_concrete_prices = []
        contractor_lighting_prices = []
        concrete_prices_dict = defaultdict(list)
        lighting_prices_dict = defaultdict(list)
        for child in children:
            contractor_name = child.name
            for concrete_type_row in child.last_saved_params.concrete:
                contractor_concrete_prices.append(
                    {
                        "Contractor name": contractor_name,
                        "Concrete pre cast option": concrete_type_row.pre_cast_option,
                        "Concrete type": concrete_type_row.concrete_type,
                        "Concrete lead time": concrete_type_row.lead_time,
                        "Concrete price per unit": concrete_type_row.price_per_unit,
                        "Concrete volume": concrete_data[concrete_type_row.concrete_type],
                        "Concrete total price": concrete_data[concrete_type_row.concrete_type]
                        * concrete_type_row.price_per_unit,
                    }
                )
                concrete_prices_dict[concrete_type_row.concrete_type].append(concrete_type_row.price_per_unit)
            for lighting_type_row in child.last_saved_params.lighting:
                contractor_lighting_prices.append(
                    {
                        "Contractor name": contractor_name,
                        "Lighting type": lighting_type_row.lighting_type,
                        "Lighting lead time": lighting_type_row.lead_time,
                        "Lighting price per unit": lighting_type_row.price_per_unit,
                        "Lighting volume": lighting_data[lighting_type_row.lighting_type],
                        "Lighting total price": lighting_data[lighting_type_row.lighting_type]
                        * lighting_type_row.price_per_unit,
                    }
                )
                lighting_prices_dict[lighting_type_row.lighting_type].append(lighting_type_row.price_per_unit)
        print(contractor_concrete_prices)

        print(contractor_lighting_prices)

        # Extracting unique contractors and concrete types
        contractors = list(set(entry["Contractor name"] for entry in contractor_lighting_prices))
        lighting_types = list(set(entry["Lighting type"] for entry in contractor_lighting_prices))

        # Initialize a dictionary to store the price per unit for each contractor and lighting type
        price_per_unit_dict = {
            contractor: {lighting_type: 0 for lighting_type in lighting_types} for contractor in contractors
        }

        # Fill the dictionary with the price per unit data
        for entry in contractor_lighting_prices:
            contractor = entry["Contractor name"]
            lighting_type = entry["Lighting type"]
            price_per_unit = entry["Lighting total price"]
            price_per_unit_dict[contractor][lighting_type] = price_per_unit

        # Create a stacked bar chart trace for each contractor
        traces = []
        for contractor in contractors:
            prices = [price_per_unit_dict[contractor][lighting_type] for lighting_type in lighting_types]
            trace = go.Bar(x=lighting_types, y=prices, name=contractor)
            traces.append(trace)

        # Create the figure
        fig = go.Figure(data=traces)

        # Update layout
        fig.update_layout(
            title="Lighting Prices by Contractor and Type",
            xaxis_title="Lighting Type",
            yaxis_title="Lighting Price",
            barmode="group",
        )

        return PlotlyResult(fig.to_json())
