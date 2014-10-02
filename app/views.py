import os
from app import app
from flask import Flask, jsonify, request, url_for, redirect, render_template
from werkzeug import secure_filename

import math

import pymavlink.DFReader

ALLOWED_EXTENTIONS = set(['bin'])

def allowed_file(filename):
  print filename
  print filename.rsplit('.', 1)[1]
  return '.' in filename and \
    filename.rsplit('.', 1)[1] in ALLOWED_EXTENTIONS


# TEMPLATED HTML ROUTE
@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')


@app.route('/upload_log', methods=['GET','POST'])
def upload_log():
  if request.method == 'POST':
    print "HAAAA!"
    file = request.files['file']
    if file and allowed_file(file.filename):
      filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
      file.save(filename)

      log = pymavlink.DFReader.DFReader_binary(filename, 0)
      i = 0
      while True:
        m = log.recv_msg()
        if m is None:
          break
        i += 1

      return 'SUCCESS, contains %d messages' % i
#      return redirect(url_for('uploaded_file', filename=filename))
    else:
      return '''ILLEGALFILENAME'''
  return '''
  <!doctype html>
  <title>Upload new File</title>
  <h1>Upload new File</h1>
  <form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=file>
       <input type=submit value=Upload>
  </form>
  '''

from flask import send_from_directory


# Here is a way to download files we have on the server.
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
