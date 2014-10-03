import os
from app import app
from flask import Flask, jsonify, request, url_for, redirect, render_template
from werkzeug import secure_filename
import time

import math

import pymavlink.DFReader as DFReader

ALLOWED_EXTENTIONS = set(['bin', 'BIN'])

def allowed_file(filename):
  print filename
  print filename.rsplit('.', 1)[1]
  return '.' in filename and \
    filename.rsplit('.', 1)[1] in ALLOWED_EXTENTIONS

# Returns a tuple of the message counts, the log in an UNREAD state, and true/false
def validate_log(filename):
  log = DFReader.DFReader_binary(filename, 0)
  while True:
    m = log.recv_msg()
    if m is None:
      break
  counts = log.counts.copy()
  if len(counts.items()) == 0:
    return (False, None)
  log._rewind()
  return (True, counts)

def logUUIDToFile(logUUID):
  return os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(logUUID))

def genUUID(ext):
  return secure_filename(time.strftime("%Y_%m_%d_%H_%M_%S") \
    + "_" \
    + str(int(time.time()*1000 % 1000)) \
    + "." + str(ext))

# TEMPLATED HTML ROUTE
@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
  return render_template('error.html',reason="404: Not Found"), 404

@app.route('/apm/upload_log', methods=['GET', 'POST'])
def upload_log():
  if request.method == 'POST':
    file = request.files['file']
    if file and allowed_file(file.filename):
      logUUID = genUUID("BIN")
      filename = logUUIDToFile(logUUID)
      file.save(filename)
      valid, counts = validate_log(filename)
      if not valid:
        os.remove(filename)
        return render_template('error.html',reason="That doesn't appear to be a valid Dataflash logfile!")
      return redirect(url_for('analyze_log',logUUID=logUUID))
    else:
      return render_template('error.html', reason="That doesn't appear to be a valid Dataflash logfile!")
  else:
    return redirect(url_for('index'))

@app.route('/apm/analyze_log/<logUUID>')
def analyze_log(logUUID=None):
  if logUUID is None:
    return redirect(url_for('index'))
  filename = logUUIDToFile(logUUID)
  if not os.path.isfile(filename):
    abort(404);
  return render_template('analysis.html', logUUID=logUUID)

@app.route('/apm/log_json/<logUUID>')
def log_json(logUUID=None):
  if logUUID is None:
    return jsonify([])
  filename = logUUIDToFile(logUUID)
  if not os.path.isfile(filename):
    abort(404);

  log = DFReader.DFReader_binary(filename, 0)
  while True:
    m = log.recv_msg()
    if m is None:
      break  

  return jsonify({
    'counts': log.counts,
    'params': log.params
  })

from flask import send_from_directory

# Here is a way to download files we have on the server.
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.after_request
def add_header(response):
  """
  Add headers to both force latest IE rendering engine or Chrome Frame,
  and also to cache the rendered page for 10 minutes.
  """
  response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
  response.headers['Cache-Control'] = 'public, max-age=0'
  return response