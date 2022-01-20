#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 20:52:13 2021
@author: Victoria Zhao
"""
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import requests
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


def movie_data_load():
    
    # read movielens.org datasets
    tags = pd.read_csv("tags.csv")
    print('Loaded Movie Tags')
    ratings = pd.read_csv("ratings.csv")
    print('Loaded Movie Ratings')
    movies = pd.read_csv("movies.csv")
    print('Loaded Movies')
    
    
    print('Loading links.csv ... ')
    links = pd.read_csv("links.csv", dtype={'imdbId': str, 'tmdbId': str})
    links['imdbId'] = links['imdbId'].astype(str)
    links['tmdbId'] = links['tmdbId'].astype(str)
    print('Loaded Links')
    print("-"*11+'All files being loaded successfully.'+"-"*11)
    
    #start data aggregation 
    # compute some on-off data
    #

    AvgRate = ratings.groupby('movieId').mean().round(2)
    movies = pd.merge(movies, AvgRate, left_on='movieId', right_on='movieId')
    print('Aggregation has been done in rating level...')


    Movies_AvgRate_Link = pd.merge(movies, links, left_on='movieId', right_on='movieId')
    print('Linked with Links...')

    movie_full = pd.merge(Movies_AvgRate_Link, tags, left_on='movieId', right_on='movieId')
    print('Lnked with Tags...')
    print("Finished!! Thanks for using Movie-Recommendar web app. Wish to see you soon :-D")
    
    return movie_full 


api_key = 'Use your API'
movie_full = pd.DataFrame()
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])

app.layout = html.Div([
    html.Div([
        html.H3(children='MovieLens Database',
                style={'color': '#FEDAF6 ', 'textAlign': 'center'}),

        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div(children='Search movies by tag',
                                 style={'color': '#ADA568 ', 'textAlign': 'right', 'size': 36}),
                    ], width=6),
                    dbc.Col([
                        html.Div([
                            dcc.Input(id='filter_value', value=''),
                        ], ),
                    ], width=6, align='center'),
                ]),
            ]), ),

        html.Br(),

        dbc.Carousel(id='carousel_placeholder',
                     items=[],
                     controls=True,
                     indicators=True,
                     style={'width': 300, 'align': 'right'})
    ]), ])


@app.callback(
    Output('carousel_placeholder', 'items'),
    [Input('filter_value', 'value')]
)
def create_carousel_content(input_value):
    global movie_full
    if movie_full.empty:
        movie_full = movie_data_load()

    if input_value == '':
        dff = movie_full.sample(n=12)
    else:
        dff = movie_full[movie_full['tag'] == input_value]


    display_title = dff['title'].to_list()
    display_rating = dff['rating'].to_list()
    display_picture_id = dff['tmdbId'].to_list()#The id used for movie display is tmdId

    movies = []
    for movie_index in range(len(dff)):
        picture_id = str(display_picture_id[movie_index])
        url = f'https://api.themoviedb.org/3/movie/{picture_id}?api_key={api_key}&language'
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            poster_path = data['poster_path']
            full_path = 'https://via.placeholder.com/150' if not poster_path \
                else f'https://image.tmdb.org/t/p/w500/{poster_path}'
        else:
            full_path = "https://via.placeholder.com/150"
            continue

        movie_information = {
            'key': movie_index,
            'src': full_path,
            'header': str(display_title[movie_index]),
            'caption': str(display_rating[movie_index]),
        }
        movies.append(movie_information)

    return movies


if __name__ == '__main__':
    app.run_server(debug=True)
