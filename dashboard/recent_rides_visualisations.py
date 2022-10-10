import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import plotly.graph_objs as go

load_dotenv()

pd.set_option('plotting.backend', 'plotly')