import base64
import logging
import webbrowser
from threading import Timer

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from graffan.library.models.analysis import AnalysedIteration
from graffan.utilities.rdkit import smiles_to_grid_svg, smiles_to_svg

logger = logging.getLogger(__name__)

INNER_STATE = "inner-state"

TARGET_SELECT = "target-select"
PARAMETER_SELECT = "parameter-select"

X_ATTRIBUTE_SELECT = "x-attribute-select"
Y_ATTRIBUTE_SELECT = "y-attribute-select"

MOLECULE_IMAGE = "mol-image"
MOLECULE_IMAGE_LABEL = "mol-image-label"

PARAMETER_ID_LABEL = "parameter-id-label"
PARAMETER_SMIRKS_LABEL = "parameter-smirks-label"

MAIN_PLOT = "plot-area"

_app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


class DashboardApp:
    @staticmethod
    @_app.callback(
        Output(PARAMETER_SELECT, "options"),
        Output(PARAMETER_SELECT, "value"),
        Input(TARGET_SELECT, "value"),
        State(INNER_STATE, "data"),
    )
    def _select_parameter_options(selected_target, inner_data_json):

        if selected_target is None or len(selected_target) == 0:
            return [], None

        inner_data = AnalysedIteration.parse_raw(inner_data_json)
        targets = {target.type: target for target in inner_data.targets}

        parameter_ids = [
            {"label": parameter_id, "value": parameter_id}
            for parameter_id in targets[selected_target].gradients
        ]

        return parameter_ids, parameter_ids[0]["value"]

    @staticmethod
    @_app.callback(
        Output(X_ATTRIBUTE_SELECT, "options"),
        Output(Y_ATTRIBUTE_SELECT, "options"),
        Output(X_ATTRIBUTE_SELECT, "value"),
        Output(Y_ATTRIBUTE_SELECT, "value"),
        Input(TARGET_SELECT, "value"),
        Input(PARAMETER_SELECT, "value"),
        State(INNER_STATE, "data"),
    )
    def _select_attribute_options(selected_target, selected_parameter, inner_data_json):

        if (
            selected_target is None
            or len(selected_target) == 0
            or selected_parameter is None
            or len(selected_parameter) == 0
        ):
            return [], [], None, None

        inner_data = AnalysedIteration.parse_raw(inner_data_json)
        targets = {target.type: target for target in inner_data.targets}

        attributes = [
            {"label": attribute, "value": attribute}
            for attribute in targets[selected_target].gradients[selected_parameter]
        ]

        return attributes, attributes, attributes[0]["value"], attributes[-1]["value"]

    @staticmethod
    @_app.callback(
        Output(PARAMETER_ID_LABEL, "children"),
        Output(PARAMETER_SMIRKS_LABEL, "children"),
        Input(PARAMETER_SELECT, "value"),
        State(INNER_STATE, "data"),
    )
    def _on_parameter_changed(selected_parameter, inner_data_json):

        if selected_parameter is None or len(selected_parameter) == 0:
            return "", ""

        inner_data = AnalysedIteration.parse_raw(inner_data_json)

        parameter_smirks = [
            parameter.smirks
            for parameter in inner_data.refit_parameters
            if parameter.id == selected_parameter
        ][0]

        return selected_parameter, parameter_smirks

    @staticmethod
    @_app.callback(
        Output(MOLECULE_IMAGE, "src"),
        Output(MOLECULE_IMAGE_LABEL, "children"),
        Input(MAIN_PLOT, "hoverData"),
        Input(PARAMETER_SELECT, "value"),
        State(INNER_STATE, "data"),
    )
    def _hover_data_point(hoverData, selected_parameter, inner_data_json):

        from openforcefield.topology import Molecule

        if hoverData is None or len(hoverData["points"]) == 0:
            raise PreventUpdate

        if "hovertext" not in hoverData["points"][0]:
            raise PreventUpdate

        inner_data = AnalysedIteration.parse_raw(inner_data_json)

        parameter_smirks = [
            parameter.smirks
            for parameter in inner_data.refit_parameters
            if parameter.id == selected_parameter
        ][0]

        smiles = hoverData["points"][0]["hovertext"]
        svg_content = smiles_to_svg(smiles, parameter_smirks)

        encoded_image = base64.b64encode(svg_content.encode()).decode()

        smiles = Molecule.from_smiles(smiles, allow_undefined_stereo=True).to_smiles(
            explicit_hydrogens=False
        )
        return f"data:image/svg+xml;base64,{encoded_image}", smiles

    @staticmethod
    @_app.callback(
        Output(MAIN_PLOT, "figure"),
        Input(TARGET_SELECT, "value"),
        Input(PARAMETER_SELECT, "value"),
        Input(X_ATTRIBUTE_SELECT, "value"),
        Input(Y_ATTRIBUTE_SELECT, "value"),
        State(INNER_STATE, "data"),
    )
    def _build_plot(
        selected_target,
        selected_parameter,
        selected_x_attribute,
        selected_y_attribute,
        inner_data_json,
    ):

        if (
            selected_target is None
            or len(selected_target) == 0
            or selected_parameter is None
            or len(selected_parameter) == 0
            or selected_x_attribute is None
            or len(selected_x_attribute) == 0
            or selected_y_attribute is None
            or len(selected_y_attribute) == 0
        ):
            return {}

        inner_data = AnalysedIteration.parse_raw(inner_data_json)
        targets = {target.type: target for target in inner_data.targets}

        target = targets[selected_target]

        if selected_parameter not in target.gradients:
            return {}

        parameter_gradients = target.gradients[selected_parameter]

        if (
            selected_x_attribute not in parameter_gradients
            or selected_y_attribute not in parameter_gradients
        ):
            return {}

        x = []
        y = []

        labels = []

        for smiles in parameter_gradients[selected_x_attribute]:

            if smiles not in parameter_gradients[selected_y_attribute]:
                continue

            x.append(parameter_gradients[selected_x_attribute][smiles])
            y.append(parameter_gradients[selected_y_attribute][smiles])

            labels.append(smiles)

        x_label = f"d<X2> / d {selected_x_attribute}"
        y_label = f"d<X2> / d {selected_y_attribute}"

        plot_data = pandas.DataFrame({x_label: x, y_label: y, "labels": labels})

        figure = px.scatter(
            plot_data,
            x=x_label,
            y=y_label,
            hover_name="labels",
            marginal_x="histogram",
            marginal_y="histogram",
        )
        figure.update_traces(hoverinfo="none", hovertemplate=None)
        figure.update_layout(hovermode="closest")

        return figure

    @staticmethod
    @_app.callback(
        Output("generic-output", "src"),
        Input(MAIN_PLOT, "relayoutData"),
        Input(TARGET_SELECT, "value"),
        Input(PARAMETER_SELECT, "value"),
        Input(X_ATTRIBUTE_SELECT, "value"),
        Input(Y_ATTRIBUTE_SELECT, "value"),
        State(INNER_STATE, "data"),
    )
    def on_plot_zoomed(
        relayout_data,
        selected_target,
        selected_parameter,
        selected_x_attribute,
        selected_y_attribute,
        inner_data_json,
    ):

        if relayout_data is None:
            return ""

        if (
            "xaxis.range[0]" not in relayout_data
            and "yaxis.range[0]" not in relayout_data
        ):
            return ""

        if (
            selected_target is None
            or len(selected_target) == 0
            or selected_parameter is None
            or len(selected_parameter) == 0
            or selected_x_attribute is None
            or len(selected_x_attribute) == 0
            or selected_y_attribute is None
            or len(selected_y_attribute) == 0
        ):
            return ""

        inner_data = AnalysedIteration.parse_raw(inner_data_json)
        targets = {target.type: target for target in inner_data.targets}

        target = targets[selected_target]

        if selected_parameter not in target.gradients:
            return ""

        parameter_gradients = target.gradients[selected_parameter]

        if (
            selected_x_attribute not in parameter_gradients
            or selected_y_attribute not in parameter_gradients
        ):
            return ""

        x_range = (
            (-1e10, 1e10)
            if "xaxis.range[0]" not in relayout_data
            else (relayout_data["xaxis.range[0]"], relayout_data["xaxis.range[1]"])
        )
        y_range = (
            (-1e10, 1e10)
            if "yaxis.range[0]" not in relayout_data
            else (relayout_data["yaxis.range[0]"], relayout_data["yaxis.range[1]"])
        )

        smiles_list = []

        for smiles in parameter_gradients[selected_x_attribute]:

            if smiles not in parameter_gradients[selected_y_attribute]:
                continue

            x = parameter_gradients[selected_x_attribute][smiles]
            y = parameter_gradients[selected_y_attribute][smiles]

            if x < x_range[0] or x > x_range[1]:
                continue
            if y < y_range[0] or y > y_range[1]:
                continue

            smiles_list.append(smiles)

        svg_content = smiles_to_grid_svg(smiles_list)
        encoded_image = base64.b64encode(svg_content.encode()).decode()

        return f"data:image/svg+xml;base64,{encoded_image}"

    @staticmethod
    def _build_select_target(analyzed_output: AnalysedIteration):

        target_types = [target.type for target in analyzed_output.targets]

        return dbc.Col(
            [
                dbc.Label("Target type"),
                dbc.Select(
                    id=TARGET_SELECT,
                    options=[
                        {"label": target_type, "value": target_type}
                        for target_type in target_types
                    ],
                ),
            ]
        )

    @staticmethod
    def _build_select_parameter():

        return dbc.Col(
            [
                dbc.Label("Parameter"),
                dbc.Select(
                    id=PARAMETER_SELECT,
                    options=[],
                ),
            ]
        )

    @staticmethod
    def _build_select_attributes():

        return [
            dbc.Col(
                [
                    dbc.Label("X-Axis Attribute"),
                    dbc.Select(
                        id=X_ATTRIBUTE_SELECT,
                        options=[],
                    ),
                ]
            ),
            dbc.Col(
                [
                    dbc.Label("Y-Axis Attribute"),
                    dbc.Select(
                        id=Y_ATTRIBUTE_SELECT,
                        options=[],
                    ),
                ]
            ),
        ]

    @classmethod
    def _build_layout(cls, analyzed_output: AnalysedIteration):

        _app.layout = dbc.Container(
            children=[
                html.H1(children="Visualise Target Gradients"),
                dcc.Store(INNER_STATE, data=analyzed_output.json()),
                dbc.Row(
                    [
                        cls._build_select_target(analyzed_output),
                        cls._build_select_parameter(),
                    ]
                ),
                html.Br(),
                dbc.Row(cls._build_select_attributes()),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id=MAIN_PLOT)),
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        html.B(id=PARAMETER_ID_LABEL),
                                        html.Span(id=PARAMETER_SMIRKS_LABEL),
                                    ]
                                ),
                                dbc.Row(html.Img(id=MOLECULE_IMAGE)),
                                dbc.Row(html.Div(id=MOLECULE_IMAGE_LABEL)),
                            ]
                        ),
                    ]
                ),
                html.Br(),
                dbc.Row([html.Img(id="generic-output")]),
            ]
        )

    @classmethod
    def launch(cls, analyzed_output: AnalysedIteration, debug: bool = False):

        cls._build_layout(analyzed_output)

        if not debug:
            Timer(1, lambda: webbrowser.open_new("http://localhost:8050")).start()

        _app.run_server(debug=debug)
