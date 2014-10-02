import flask
 
from app import app

#Set application.debug=true to enable tracebacks on Beanstalk log output. 
#Make sure to remove this line before deploying to production.
app.debug=True

UPLOAD_FOLDER = '/uploads/'

app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if __name__ == '__main__':
    app.run(host='0.0.0.0')