from flask import Flask, request
from replit import db
import hashlib
import random
import string
from flask_cors import CORS
import traceback
import json


def checkToken(token):
  # check the token passed and return the username authenticated if the token is valid, otherwise return False
  for usr, tok in db["tokens"].value.items():
    # if the token is valid, return the username
    if tok == token:
      return usr
  return False


# checks if the user already has a token
def tokenAlreadyExists(user):
  # check if the user already has a token
  for usr, tok in db["tokens"].value.items():
    # if the user already has a token, return True
    if usr == user:
      return True
  return False


app = Flask('workshop')
CORS(app)


@app.route('/')
def status():
  return 'Clarity Workshop OK'


@app.route('/listall')
def list():
  lvls = []
  for lvl in db["lvls"]:
    obj = {
      "id": lvl["id"],
      "name": lvl["name"],
      "description": lvl["description"],
      "author": lvl["author"],
    }
    lvls.append(obj)
  return json.dumps(lvls)


@app.route('/list/<page>')
def listpage(page):
  lvls = []
  for lvl in db["lvls"]:
    obj = {
      "id": lvl["id"],
      "name": lvl["name"],
      "description": lvl["description"],
      "author": lvl["author"],
    }
    lvls.append(obj)

  stuff = []
  pagelength = 4

  for i in lvls[pagelength * (int(page) - 1):pagelength * (int(page))]:
    stuff.append(i)

  if stuff.__len__() == 0:
    return 'No results'
  else:
    return json.dumps(stuff)


@app.route('/lvl/<id>')
def getlvl(id):
  try:
    for i in db["lvls"].value:
      if int(i["id"]) == int(id):
        return str(i["lvl"])
    return "no such level"
  except:
    return "no such level"


@app.route('/lvlmeta/<id>')
def getlvlmeta(id):
  try:
    for i in db["lvls"].value:
      if int(i["id"]) == int(id):
        obj = {
          "id": i["id"],
          "name": i["name"],
          "description": i["description"],
          "author": i["author"],
        }
        return obj
    return "no such level"
  except:
    return "no such level"


@app.route('/add', methods=["POST"])
def addlvl():
  lvl = request.form.get("lvl")
  try:
    id = db["lvls"][-1]["id"] + 1
  except:
    id = 0
  name = request.form.get("name")
  description = request.form.get("description")
  token = request.form.get("token")
  author = checkToken(token)

  if not author:
    return "bad token"

  db["lvls"].append({
    "id": id,
    "lvl": lvl,
    "name": name,
    "description": description,
    "author": author
  })
  return "added level " + str(id)


@app.route('/signup', methods=["POST"])
def signup():
  username = request.form.get("username")
  password = request.form.get("password")
  try:
    db["users"][username]
    return "username taken"
  except:
    # hash password
    hashed = hashlib.sha224(bytes(password, "UTF-8")).hexdigest()
    db["users"][username] = hashed
    return "success"


@app.route('/login', methods=["POST"])
def login():
  username = request.form.get("username")
  password = request.form.get("password")
  # Check if username is valid, then if the password is valid, return the user's token
  try:
    if db["users"][username] == hashlib.sha224(bytes(password,
                                                     "UTF-8")).hexdigest():
      # check if a token for the user already exists
      if not tokenAlreadyExists(username):
        token = ''.join(
          random.choice(string.ascii_lowercase) for i in range(50))
        db["tokens"][username] = token
        return token
      else:
        # Return the token that already exists
        return db["tokens"][username]
    else:
      return "invalid"
  except Exception as e:
    print(traceback.format_exc())
    return "internal server error " + str(e)


@app.route('/logout', methods=["POST"])
def logout():
  try:
    del db["tokens"][request.form.get("username")]
    return "logged out"
  except:
    return "500 internal server error or whatever"


app.run(host='0.0.0.0', port=8080)
