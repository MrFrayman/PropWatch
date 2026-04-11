# import each package in a Python shell to make sure the environment is healthy.
# pandas, pydantic, requests, python-dotenv, sqlalchemy, psycopg2-binary, rapidfuzz, reportlab, pytest
import pandas as pd
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
import psycopg2
from rapidfuzz import fuzz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pytest

print("Pandas version:", pd.__version__)
print("BaseModel:", BaseModel)
print("Requests version:", requests.__version__)
print("Load dotenv:", load_dotenv)
print("Create engine:", create_engine)
print("Psycopg2 version:", psycopg2.__version__)
print("Fuzz ratio:", fuzz.ratio)
print("Letter:", letter)
print("Canvas:", canvas)
print("Pytest version:", pytest.__version__)

print("All packages imported successfully!")
