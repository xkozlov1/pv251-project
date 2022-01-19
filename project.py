import dash
import pandas as pd
import plotly.express as px


from dash import dcc
from dash import html
from dash.dependencies import Input, Output


app = dash.Dash(__name__)

frame = pd.read_csv('fires.csv')

assert isinstance(frame, pd.DataFrame)

frame = frame[frame['FIRE_SIZE'] >= 100]
STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}


years = list(range(1992, 2016))
states = list(set(frame['STATE']))
sts = []
for state in states:
    sts.extend([state] * len(years))
geoframe = pd.DataFrame({
    'STATE': sts,
    'YEAR': years * len(states)

})

def get_center(df):
    lon_min = df['LONGITUDE'].min()
    lon_max = df['LONGITUDE'].max()
    lat_min = df['LATITUDE'].min()
    lat_max = df['LATITUDE'].max()
    return {'lat': (lat_min + lat_max) / 2,
            'lon': (lon_min + lon_max) / 2}


# with open('./geo.json', 'r', encoding='utf-8') as file:
    # geojson = json.load(file)


app.layout = html.Div(children=[
    html.H1(children='Wildfires in the United States from 1992 to 2015.'),
    dcc.Dropdown(id='slct_state',
                 options=[
                     {'label': name, 'value': code}
                     for code, name in STATES.items()
                 ],
                 multi=False,
                 placeholder='Select a state'),
    dcc.Checklist(
        id='is_year_range',
        options=[
            {'label': 'Custom year range', 'value': 'True'},
        ],
        value=['True']
    ),
    dcc.RangeSlider(
        id='year_range',
        marks={i: str(i) for i in range(1992, 2016)},
        min=1992,
        max=2015,
        value=[1992, 2015]
    ),
    html.Div(id='container', children=[]),

    dcc.Graph(id='graph')
])



def create_focused_graph(df, state):
    fig = px.choropleth(geoframe[geoframe['STATE'] == state], animation_frame='YEAR',
                    color='STATE',
                    locations='STATE', color_discrete_map={state: '#EEEEFF' for state in STATES},
                    locationmode="USA-states", scope="usa",
                    width=1000, height=700,)

    fig.update_layout(showlegend=False)
    fig.update_traces(
       hovertemplate=None,
       hoverinfo='skip'
    )

    fig_scatter = px.scatter_geo(df[df['STATE'] == state], lat='LATITUDE', lon='LONGITUDE',
                                 color="FIRE_SIZE", size='FIRE_SIZE', size_max=20, opacity=0.6,
                                 width=1000, height=700, animation_frame='YEAR')

    fig_scatter.update_traces(marker=dict(line=dict(width=0)),
                              selector=dict(mode='markers'))

    if fig_scatter.data:
        fig.add_trace(
            fig_scatter.data[0]
        )

    for i in range(len(fig_scatter.frames)):
        fig.frames[i].data += (fig_scatter.frames[i].data[0],)

    fig.update_geos(fitbounds='locations')

    return fig


@app.callback(
    [Output(component_id='graph', component_property='figure'),
     Output(component_id='container', component_property='children')],
    [Input(component_id='slct_state', component_property='value'),
     Input(component_id='year_range', component_property='value')]
)
def update_graph(state, years):
    df = frame.copy()
    container = f'Chosen state: {state}'
    min_year, max_year = years
    if state is not None:
        fig = create_focused_graph(df, state)
    else:
        fig = px.scatter_geo(frame, lat='LATITUDE', lon='LONGITUDE', scope='usa',
                             color="FIRE_SIZE", size='FIRE_SIZE', size_max=20, opacity=0.6,
                             width=1000, height=700, hover_data=['FIRE_NAME', 'FIRE_SIZE', 'STATE'],
                             animation_frame='YEAR')

        fig.update_traces(marker=dict(line=dict(width=0)),
                                  selector=dict(mode='markers'))
    return fig, container

if __name__ == '__main__':
    app.run_server(debug=True)
