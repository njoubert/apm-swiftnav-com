from flask import Flask

# Global server variable 
app = Flask(__name__)

from app import views
