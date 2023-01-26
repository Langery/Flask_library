from flask import Blueprint;

admin_blue = Blueprint('admin', __name__)

@admin_blue.route('/')
def adminTest():
  return 'This is the admin test'

@admin_blue.route('/hello')
def adminHello():
  return 'hello admin blueprint'
