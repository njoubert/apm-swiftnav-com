from app import app
from flask import jsonify, request, url_for, redirect, render_template

import math

# TEMPLATED HTML ROUTE
@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')



