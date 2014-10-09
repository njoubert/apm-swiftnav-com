import os
import time
import math
import urllib

from app import app
from flask import Flask, jsonify, request, url_for, redirect, render_template, abort
from werkzeug import secure_filename

import analysis

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
      email = ""
      comments = ""
      if 'email' in request.form and len(request.form['email']) < 60:
        email = request.form['email']
        
      if 'comments' in request.form and len(request.form['comments']) < 8192:
        comments = request.form['comments']

      if len(email) > 0 or len(comments) > 0:
        with open(logUUIDToFile(logUUID + ".txt"), 'w') as f:
          f.write(email)
          f.write("\n============\n")
          f.write(comments)

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

#Array of structs
@app.route('/apm/log_json/<logUUID>')
def log_json(logUUID=None):
  if logUUID is None:
    return jsonify([])
  filename = logUUIDToFile(logUUID)
  if not os.path.isfile(filename):
    abort(404);

  def message_to_dict(m):
    d = m._d.copy()
    d['fmt'] = m.fmt.name
    return d

  log = DFReader.DFReader_binary(filename, 0)
  grabThese = set(['SBPH', 'SBPB', 'SBPL', 'GPS', 'GPS2', ])
  messages = []
  while True:
    m = log.recv_msg()
    if m is None:
      break
    if m.get_type() in grabThese:
      messages.append(message_to_dict(m))

  return jsonify({
    'counts': log.counts,
    'params': log.params,
    'messages': messages,
  })

#Struct of Arrays
@app.route('/apm/log_jsonSoA/<logUUID>')
def log_jsonSoA(logUUID=None):
  start = time.time()*1000
  if logUUID is None:
    return jsonify([])
  filename = logUUIDToFile(logUUID)
  if not os.path.isfile(filename):
    abort(404);

  def message_to_dict(m):
    d = m._d.copy()
    d['fmt'] = m.fmt.name
    return d

  def message_get_keys(m):
    return m._d.keys()

  def append_message(d, m):
    for k, v in m._d.iteritems():
      d[k].append(v)

  log = DFReader.DFReader_binary(filename, 0)
  grabThese = set(['SBPH', 'SBPB', 'SBPL', 'GPS', 'GPS2', ])
  messages = dict.fromkeys(grabThese, None)
  while True:
    m = log.recv_msg()
    if m is None:
      break
    if m.get_type() in grabThese:
      if messages[m.get_type()] is None:
        messages[m.get_type()] = {}
        for k in message_get_keys(m):  
          messages[m.get_type()][k] = []
      append_message(messages[m.get_type()], m)

  print "dur (ms):", time.time()*1000 - start
  return jsonify({
    'counts': log.counts,
    'params': log.params,
    'messages': messages,
  })

