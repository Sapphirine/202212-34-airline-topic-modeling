from dash import Dash, dcc, html, Input, Output
#import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# app = Dash(__name__)

# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]


app = Dash(__name__,
                #external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)


topic_nums_to_names = {
    "0": "Charitable work, raising awareness",
    "2": "Future-forward campaigns (i.e. aviation, sustainability)",
    "3": "Travel spots with the best views",
    "4": "Campaign with a contest",
    "5": "Non-stop flight service",
    "6": "Promotional campaign via travel suggestions",
    "8": "Best/lowest/discounted fares",
    "10": "Airline growth (i.e. new routes, aircraft, offerings)",
    "11": "Scenic/peaceful travel destinations",
    "12": "Flight seating (i.e. group seating, upgrades)",
    "13": "Travel alerts and advisories",
    "14": "Visit our website for more info",
    "16": "Tips for comfortable travel experience"
}

topic_names_to_nums = {v: k for k, v in topic_nums_to_names.items()}

default_topics = [
    "Best/lowest/discounted fares", 
    "Scenic/peaceful travel destinations",
    "Charitable work, raising awareness",
    #"Future-forward campaigns (i.e. aviation, sustainability)",
    #"Promotional campaign via travel suggestions"   
]

default_airlines = ['AeromexicoUSA', 'AirCanada', 'AlaskaAir', 
                        'AmericanAir', 'AviancaNAM', 
                        'CEAirglobal', 'CebuPacificAir', 'EGYPTAIR',
                        'FlyFrontier', 'GulfAir', 
                        'JetBlue', 'KuwaitAirways', 
                        'Qantas', 'RAM_Maroc', 
                        'Ryanair', 'SaudiAirlinesEn', 'SingaporeAir',
                        'SouthwestAir', 'SpiritAirlines', 'TurkishAirlines', 'airfrance',
                        'iflycaribbean', 'qatarairways', 'united']


def prep_airline_topic_heatmap_df():
    """
    Uses tweet-level data labeled with dominant 
    topics to find topic contributions to each 
    airline's tweet set.
    """
    merged_output_df = pd.read_csv('tweets_17_topics_all_info.csv.gz', low_memory=False)
    
    
    # Remove topics we want to exclude from analysis
    # 1, 7, 9, 15
    merged_output_df2 = merged_output_df[~merged_output_df.Dominant_Topic.isin([1, 7, 9, 15])]
    
    
    # Get pct of topic contribution from tweets to each airline
    user_tweet_counts = merged_output_df2.groupby(['user'])['Document_No'].count().reset_index().rename(columns={'Document_No': 'tweet_count'})
    
    user_topic_tweet_counts = merged_output_df2.groupby([
    'user', 'Dominant_Topic'])['Document_No'].count().reset_index().rename(columns={'Document_No': 'topic_tweet_count'})
    
    user_tweet_counts_ALL = pd.merge(user_tweet_counts, user_topic_tweet_counts, how='left', on='user')
    user_tweet_counts_ALL['topic_pct'] = user_tweet_counts_ALL['topic_tweet_count'] / user_tweet_counts_ALL['tweet_count']
    
    all_airlines = user_tweet_counts['user'].tolist()
    # all_columns = ['topic_num'] + all_airlines
    all_columns = all_airlines
    all_topic_nums = user_tweet_counts_ALL['Dominant_Topic'].unique()
    df_heatmap_topic_lvl_airline_scores = pd.DataFrame(columns=all_columns)

    for topic_num in all_topic_nums:
        topic_num_pcts = user_tweet_counts_ALL[user_tweet_counts_ALL['Dominant_Topic']==topic_num]['topic_pct'].tolist()

        new_row_dict = {airline: topic_pct for airline, topic_pct in zip(all_airlines, topic_num_pcts)}

        new_row_df = pd.DataFrame(new_row_dict, index=[topic_num])
        df_heatmap_topic_lvl_airline_scores = pd.concat([df_heatmap_topic_lvl_airline_scores, new_row_df], axis=0, ignore_index=False)

    df_heatmap_topic_lvl_airline_scores.fillna(0, inplace=True)
    return df_heatmap_topic_lvl_airline_scores, all_topic_nums




df_heatmap_topic_lvl_airline_scores, all_topic_nums = prep_airline_topic_heatmap_df()
# all_airlines = df_heatmap_topic_lvl_airline_scores.T.loc[::-1, :].columns.tolist()
all_airlines = df_heatmap_topic_lvl_airline_scores.columns.tolist()
# print(all_airlines)


all_dfs_topic_keywords = pd.read_csv('all_dfs_topic_keywords.csv')
#fig_bubble_chart = get_bubble_chart(all_dfs_topic_keywords)
    
    
app.layout = html.Div([
    
    # first row
    html.Div([
        html.H1('Topic Modeling on US Airline Tweets', style={'margin-left':'10px', "font-family": "'Open Sans', verdana, arial, sans-serif", 'text-align':'center'})
    ]),
    
    # second row
    html.Div([
        
        # first column of second row
        html.Div([
            html.P('Select up to 5 topics:'),
            dcc.Dropdown(list(topic_nums_to_names.values()), 
                 default_topics,  # select these topics by default
                 id='topic-dropdown', multi=True, maxHeight=200, optionHeight=20),
            dcc.Graph(id="bubble_chart"),
        ],  className='col',
            id='left', 
            style={#'backgroundColor':'darkslategray',
                    #'color':'lightsteelblue',
                    #'height':'100px',
                    #'margin-left':'15px',
                    #'text-align':'center',
                    'width':'45%',
                    'display':'inline-block',
                'vertical-align': 'top', 'margin-left': '1vw', 
                'margin-top': '3vw'
            }
        ),
        
        
        
        # second column of second row
        html.Div([
            #html.H4('Topic contributions to Airline tweets'),
            dcc.Graph(id="heatmap"),
            html.P("Select airlines here:"),
            dcc.Dropdown(sorted(all_airlines), 
                         default_airlines,  # select these airlines by default
                         id='airline-dropdown', multi=True, maxHeight=200, optionHeight=20)
        ], className='col',
            id='right', 
            style={#'backgroundColor':'darkslategray',
                    #'color':'lightsteelblue',
                    # 'height':'100px',
#                     'margin-right':'15px',
                    'width':'45%',
                    #'text-align':'center',
                    'display':'inline-block',
                'vertical-align': 'top', 
                'margin-left': '2vw', 
                'margin-right': '1vw',
                'margin-top': '3vw'
                    }
        ),
        
        
    ], className='row'),
    
    
], id='wrapper')


@app.callback(
    Output(component_id="topic-dropdown", component_property="value"),
    [
        Input(component_id="topic-dropdown", component_property="value"),
    ],
)
def update_topic_dropdown_options(values):
    if len(values) == 6:
        return values[:5]
    return values



@app.callback(
    Output(component_id="airline-dropdown", component_property="value"),
    [
        Input(component_id="airline-dropdown", component_property="value"),
    ],
)
def update_topic_dropdown_options(values):
    if len(values) == 31:
        return values[:30]
    return values



@app.callback(
    Output("bubble_chart", "figure"), 
    Input("topic-dropdown", "value")
)
def get_bubble_chart(values):
    scatter_list = []

    # for topic_num in all_dfs_topic_keywords['topic_id'].unique():
    for topic_num in [int(topic_names_to_nums[tpc_name]) for tpc_name in values]:

        df_topic_num = all_dfs_topic_keywords[all_dfs_topic_keywords['topic_id']==topic_num]

        scatter_obj = go.Scatter(
            x=df_topic_num['keyword_importance'].values.tolist(), 
            y=df_topic_num['keyword_tweet_count_in_topic'].values.tolist(),
            mode='markers+text',
            opacity=0.6,
            marker=dict(
                size=df_topic_num['share_of_topic_tweets'].values.tolist(),
                sizemode='area',
                sizeref=2.*max(df_topic_num['share_of_topic_tweets'].values.tolist())/(40.**2),
                sizemin=4
            ),
            text=df_topic_num['topic_keyword'].values.tolist(),
            textposition='bottom center',
            name=df_topic_num['topic_name'].values.tolist()[0]
        )

        scatter_list.append(scatter_obj)
        
    fig = go.Figure(data=scatter_list)

    fig.update_layout(
            margin=dict(t=15, 
                        b=0, 
                        l=20, 
                        r=0),
            yaxis=dict(title='Tweet Count'),
            xaxis=dict(title='Keyword Importance (to topic)'),
            legend=dict(itemsizing='constant',
                        title=dict(text='   <b>Topic</b>')),
        )  
    
    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=-0.65,
        #xanchor="left",
        x=0.2
    ))
    
    return fig



@app.callback(
    Output("heatmap", "figure"), 
    Input("airline-dropdown", "value"),
    Input("topic-dropdown", "value")
)
def filter_heatmap(airlines, topics):
#     df = px.data.medals_wide(indexed=True) # replace with your own data source
#     fig = px.imshow(df[cols])

    nums_selected_topics = [int(topic_names_to_nums[tpc]) for tpc in topics]

    airlines_y_topics_x = {
        'z': df_heatmap_topic_lvl_airline_scores.T.loc[::-1, :].loc[airlines].values.tolist(),
        'y': sorted(airlines, reverse=True),
        'x': [topic_nums_to_names[str(i)] for i in all_topic_nums]
    }
    
    airlines_x_topics_y = {
        'z': df_heatmap_topic_lvl_airline_scores.loc[::-1, :][sorted(airlines, reverse=True)].values.tolist(),
        'x': sorted(airlines, reverse=True),
        'y': [topic_nums_to_names[str(i)] for i in all_topic_nums][::-1]
    }
    
#     fig = go.Figure(data=go.Heatmap(
#         z=df_heatmap_topic_lvl_airline_scores.loc[::-1, :][sorted(airlines, reverse=True)].values.tolist(),
#         x=sorted(airlines, reverse=True),
#         y=[topic_nums_to_names[str(i)] for i in all_topic_nums][::-1],
#         colorscale='Viridis'))
    # print(df_heatmap_topic_lvl_airline_scores.T.loc[::-1, :].columns)

    fig = go.Figure(data=go.Heatmap(
            # z=df_heatmap_topic_lvl_airline_scores.T.loc[::-1, :].loc[airlines].values.tolist(),
            z=df_heatmap_topic_lvl_airline_scores.T.loc[::-1, :].loc[airlines].loc[::-1, :][nums_selected_topics].values.tolist(),
            y=sorted(airlines, reverse=True),
            # x=[topic_nums_to_names[str(i)] for i in all_topic_nums],
            x=topics,
            colorscale='Viridis'))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
    )

    fig.update_layout(
        #title='Topic contributions to Airline tweets',
        #xaxis_nticks=13
        yaxis_nticks=len(airlines)
    )

    #fig.update_layout(width=300)
    return fig
    


app.run_server(debug=True)
