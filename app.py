import base64
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

from dash.dependencies import Input, Output, State

upload_style = {
    "width": "50%",
    "height": "120px",
    "lineHeight": "60px",
    "borderWidth": "1px",
    "borderStyle": "dashed",
    "borderRadius": "5px",
    "textAlign": "center",
    "margin": "10px",
    "margin": "3% auto",
}
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    [
        dcc.Upload(
            id="my_okodukai",
            children=html.Div(["お小遣いのファイルを", html.A("csvかexcelで頂戴！")]),
            style=upload_style,
        ),
        dcc.Dropdown(
            id="my_dropdown", multi=True, style={"width": "75%", "margin": "auto"}
        ),
        dcc.Graph(id="my_okodukai_graph"),
        dcc.Store(id="tin_man", storage_type="memory"),
    ]
)


def parse_content(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["ファイルの読み込みでエラーが発生しました"])

    return df


@app.callback(
    [
        Output("my_dropdown", "options"),
        Output("my_dropdown", "value"),
        Output("tin_man", "data"),
    ],
    [Input("my_okodukai", "contents")],
    [State("my_okodukai", "filename")],
    prevent_initial_call=True,
)
def update_dropdown(contents, filename):
    df = parse_content(contents, filename)
    options = [{"label": name, "value": name} for name in df["variable"].unique()]
    select_value = df["variable"].unique()[0]
    df_dict = df.to_dict("records")
    return options, [select_value], df_dict


@app.callback(
    Output("my_okodukai_graph", "figure"),
    [Input("my_dropdown", "value")],
    [State("tin_man", "data")],
    prevent_initial_call=True,
)
def update_graph(selected_values, data):
    df = pd.DataFrame(data)
    df_selected = df[df["variable"].isin(selected_values)]
    return px.line(df_selected, x="date", y="value", color="variable")


if __name__ == "__main__":
    app.run_server(debug=True)
