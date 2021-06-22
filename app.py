#import dash_design_kit as ddk
import dash
import dash_core_components as dcc
import dash_html_components as html

from exe_evaluation import run

run(write_file=False)

out = ''
with open('tmp.md', 'r') as file:
    for line in file.readlines():
        out += line

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    dcc.Markdown(out)
])

if __name__ == '__main__':
    app.run_server(debug=False)
    # needed for gunicorn
    server = app.server