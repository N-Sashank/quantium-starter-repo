# app.py
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
import plotly.express as px

DATA_PATH = "data/processed_sales_data.csv"
PRICE_INCREASE_DATE = datetime.datetime(2021, 1, 15)

def load_and_prepare(path=DATA_PATH):
    df = pd.read_csv(path)
    # ensure proper types
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0)
    # keep Date, Region, Sales
    return df

df_all = load_and_prepare()

# Aggregated view used for initial plot (total sales per day)
def aggregate(df, region=None):
    dff = df.copy()
    if region and region != "All":
        dff = dff[dff["Region"] == region]
    agg = dff.groupby("Date", as_index=False)["Sales"].sum().sort_values("Date")
    return agg

# create initial figure
initial_agg = aggregate(df_all, region="All")
fig = px.line(
    initial_agg,
    x="Date",
    y="Sales",
    title="Daily Sales of Pink Morsels (Total)",
    labels={"Date": "Date", "Sales": "Sales (currency units)"},
)
# add price increase vertical line
fig.add_vline(
    x=PRICE_INCREASE_DATE,
    line_width=2,
    line_dash="dash",
    annotation_text="Price increase\n2021-01-15",
    annotation_position="top left",
)

# build Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # for deployments

app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H1("Soul Foods — Pink Morsel Sales Visualiser"), className="my-3")),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="region-filter",
                        options=[{"label": "All", "value": "All"}]
                        + [{"label": r, "value": r} for r in sorted(df_all["Region"].unique())],
                        value="All",
                        clearable=False,
                        style={"width": "300px"},
                    ),
                    width=4,
                )
            ],
            className="mb-2",
        ),
        dbc.Row(dbc.Col(dcc.Graph(id="sales-line", figure=fig), width=12)),
        dbc.Row(
            dbc.Col(
                html.Div(
                    "Question: Were sales higher before or after the price increase on 15 Jan 2021? "
                    "Use the dropdown to inspect regions individually.",
                    className="mt-2",
                )
            )
        ),
    ],
    fluid=True,
)


@app.callback(Output("sales-line", "figure"), Input("region-filter", "value"))
def update_figure(region):
    agg = aggregate(df_all, region=region)
    fig = px.line(
        agg,
        x="Date",
        y="Sales",
        title=f"Daily Sales of Pink Morsels — {region}",
        labels={"Date": "Date", "Sales": "Sales (currency units)"},
    )
    fig.add_vline(
        x=PRICE_INCREASE_DATE,
        line_width=2,
        line_dash="dash",
        annotation_text="Price increase\n2021-01-15",
        annotation_position="top left",
    )
    fig.update_layout(transition_duration=200)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
