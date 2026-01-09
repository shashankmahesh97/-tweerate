# All required packages are imported
import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, gridplot
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import TextInput, Div
from bokeh.plotting import figure
import random
from datetime import datetime

# ---------------------------
# Movie rating bar chart
# ---------------------------

# Rating metrics
movies = ['TEXT BLOB', 'NLTK', 'IMDB']

# Initial ratings
ratings = [0.0, 0.0, 0.0]

# Data source
source = ColumnDataSource(data=dict(movies=movies, rating=ratings))

# Figure for movie ratings
plot = figure(
    x_range=movies,
    height=250,
    title="Movie Rating",
    toolbar_location=None,
    tools=""
)

plot.vbar(x='movies', top='rating', source=source, width=0.5)
plot.xgrid.grid_line_color = '#e2e2e2'
plot.y_range.start = 0

# ---------------------------
# Positive / Negative tweets
# ---------------------------

xRange = ['NLTK', 'TEXT BLOB']
categories = ["Negative", "Positive"]
colors = ["#FF6B6B", "#4ECDC4"]  # Updated colors for better visibility

countSource = ColumnDataSource(data=dict(
    xRange=xRange,
    Negative=[0, 0],
    Positive=[0, 0]
))

p = figure(
    x_range=xRange,
    height=500,
    title="Positive and Negative Tweets",
    toolbar_location=None,
    tools=""
)

p.vbar_stack(
    categories,
    x='xRange',
    width=0.4,
    color=colors,
    source=countSource,
    legend_label=categories
)

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.location = "top_right"
p.legend.orientation = "horizontal"

# ---------------------------
# Text input widget
# ---------------------------

text = TextInput(
    title="Search Query:",
    placeholder="Enter Movie Name",
    width=300
)

# ---------------------------
# Movie database simulation (replaces proj module)
# ---------------------------

# Simulated movie database with pre-calculated values
movie_database = {
    "inception": {
        "name": "Inception",
        "ratings": {
            "text_blob": 8.5,
            "nltk": 8.3,
            "imdb": 8.8
        },
        "sentiments": {
            "nltk": {"positive": 75, "negative": 25},
            "text_blob": {"positive": 72, "negative": 28}
        }
    },
    "the dark knight": {
        "name": "The Dark Knight",
        "ratings": {
            "text_blob": 9.0,
            "nltk": 8.9,
            "imdb": 9.0
        },
        "sentiments": {
            "nltk": {"positive": 82, "negative": 18},
            "text_blob": {"positive": 85, "negative": 15}
        }
    },
    "parasite": {
        "name": "Parasite",
        "ratings": {
            "text_blob": 8.9,
            "nltk": 8.7,
            "imdb": 8.6
        },
        "sentiments": {
            "nltk": {"positive": 88, "negative": 12},
            "text_blob": {"positive": 86, "negative": 14}
        }
    },
    "pulp fiction": {
        "name": "Pulp Fiction",
        "ratings": {
            "text_blob": 8.7,
            "nltk": 8.6,
            "imdb": 8.9
        },
        "sentiments": {
            "nltk": {"positive": 79, "negative": 21},
            "text_blob": {"positive": 81, "negative": 19}
        }
    },
    "interstellar": {
        "name": "Interstellar",
        "ratings": {
            "text_blob": 8.4,
            "nltk": 8.2,
            "imdb": 8.6
        },
        "sentiments": {
            "nltk": {"positive": 77, "negative": 23},
            "text_blob": {"positive": 74, "negative": 26}
        }
    }
}

def get_movie_from_db(movie_name):
    """Simulate the proj.getMovieFromDB function"""
    movie_name_lower = movie_name.lower()
    
    if movie_name_lower in movie_database:
        movie = movie_database[movie_name_lower]
        # Format: [movie_name, text_blob_rating, nltk_rating, imdb_rating, 
        #          text_blob_positive, text_blob_negative, 
        #          nltk_positive, nltk_negative]
        return [[
            movie["name"],
            movie["ratings"]["text_blob"],
            movie["ratings"]["nltk"],
            movie["ratings"]["imdb"],
            movie["sentiments"]["text_blob"]["positive"],
            movie["sentiments"]["text_blob"]["negative"],
            movie["sentiments"]["nltk"]["positive"],
            movie["sentiments"]["nltk"]["negative"]
        ]]
    else:
        # Generate random data for new movies
        base_rating = random.uniform(6.0, 9.5)
        variance = random.uniform(-0.5, 0.5)
        
        text_blob_rating = round(base_rating + variance, 1)
        nltk_rating = round(base_rating + random.uniform(-0.3, 0.3), 1)
        imdb_rating = round(base_rating + random.uniform(-0.2, 0.4), 1)
        
        # Generate sentiment percentages
        text_blob_positive = random.randint(60, 90)
        text_blob_negative = 100 - text_blob_positive
        
        nltk_positive = random.randint(text_blob_positive - 10, text_blob_positive + 10)
        nltk_positive = max(50, min(95, nltk_positive))
        nltk_negative = 100 - nltk_positive
        
        return [[
            movie_name.title(),
            text_blob_rating,
            nltk_rating,
            imdb_rating,
            text_blob_positive,
            text_blob_negative,
            nltk_positive,
            nltk_negative
        ]]

# ---------------------------
# Callback function (updated)
# ---------------------------

def update_title(attr, old, new):
    movie_name = text.value.strip()
    if not movie_name:
        return

    # Simulate data retrieval (no Twitter API needed)
    val = get_movie_from_db(movie_name)

    # Update titles
    plot.title.text = f"{val[0][0]} Movie Rating"
    p.title.text = f"{val[0][0]} Positive and Negative Tweets"

    # Update ratings chart
    new_ratings = [val[0][1], val[0][2], val[0][3]]
    source.data = dict(movies=movies, rating=new_ratings)

    # Update sentiment chart
    countSource.data = dict(
        xRange=xRange,
        Negative=[val[0][6], val[0][5]],  # nltk_negative, text_blob_negative
        Positive=[val[0][7], val[0][4]]   # nltk_positive, text_blob_positive
    )

# Trigger update when text changes
text.on_change('value', update_title)

# ---------------------------
# Page layout
# ---------------------------

head = Div(
    text='<h1 align="center" style="color:#1DA1F2;">TweeRate Simulator</h1>',
    width=1500,
    height=40
)

info = Div(
    text='<div style="text-align: center;"><b>Simulated Movie Ratings Demo (No Twitter API Required)</b></div>',
    width=1500,
    height=40
)

example = Div(
    text='Try: Inception, The Dark Knight, Parasite, Pulp Fiction, Interstellar (or any movie name)',
    width=800,
    height=50
)

inputs = column(head, info, text, example)
grid = gridplot([plot, p], ncols=2, width=700, height=400)

curdoc().add_root(column(inputs, grid))
curdoc().title = "TweeRate Simulator"
