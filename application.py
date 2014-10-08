import flask
 
from app import app

#Set application.debug=true to enable tracebacks on Beanstalk log output. 
#Make sure to remove this line before deploying to production.
app.debug=True

UPLOAD_FOLDER = '/uploads/'

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from flask import Flask
# from flask_debugtoolbar import DebugToolbarExtension

# # set a 'SECRET_KEY' to enable the Flask session cookies
# app.config['SECRET_KEY'] = 'nielssecret'

# toolbar = DebugToolbarExtension(app)

@app.after_request
def add_header(response):
  """
  Add headers to both force latest IE rendering engine or Chrome Frame,
  and also to cache the rendered page for 10 minutes.
  """
  response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
  response.headers['Cache-Control'] = 'public, max-age=0'
  return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')