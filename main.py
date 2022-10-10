from flask import Flask
from replit import db

app = Flask('workshop')

@app.route('/')
def status():
  return 'Clarity Workshop OK'

@app.route('/list')
def list():
  return str(db["lvls"].value)

@app.route('/lvl/<id>')
def getlvl(id):
  return db["lvls"][id]

app.run(host='0.0.0.0', port=8080)
