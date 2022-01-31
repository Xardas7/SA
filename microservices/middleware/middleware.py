from flask import Flask
from flask import jsonify
from flask import request
import sqlite3

app = Flask(__name__)

""" 
@app.route("/")
def home():
    return render_template('demo.html')
"""   

# Endpoint to be used at a specific time of the day
# that deletes all the expired reservations and
# adds all the new reservations of the day received
# through a json list of ids
@app.route('/reservations/update', methods = ['POST'])
def updateReservations():
    #connection to db
    con = sqlite3.connect('reservations.db')
    try:
        with con:
        #delete all old reservations 
            con.execute("DELETE FROM reservations")
            #parse and insert new reservations
            for item in request.json["data"]:
                con.execute("INSERT INTO reservations VALUES ('%s', 0)" %item)
            #send successful response
            resp = jsonify(success=True)
            resp.status_code = 201
    #SQL exception handler
    except sqlite3.Error:
        resp = jsonify(success=False, error="/update went wrong")
        resp.status_code = 500

    con.close()
    return resp

#Endpoint to add a new reservation for the current day
@app.route('/reservations/add/<id>')
def addReservation(id):
    #connection to db
    con = sqlite3.connect('reservations.db')
    try:
        with con:
            #insert new reservation
            con.execute("INSERT INTO reservations VALUES ('%s', 0)" % id)
            #send successful response
            resp = jsonify(success=True)
            resp.status_code = 201
    #SQL exception handler
    except sqlite3.Error:
        resp = jsonify(success=False, error="/add went wrong")
        resp.status_code = 500

    con.close()
    return resp

# Endpoint that checks if the people inside the
# museum are less than 500, than checks if the 
# received id is available among the reservations
# for the day, and in that case updates the
# checkin value corresponding to the id to "true"
@app.route("/reservations/checkin/<id>")
def checkin(id):
    #connection to db
    con = sqlite3.connect('reservations.db')
    try:
        with con:
            #check if checked-in people are less than 500
            count = con.execute("SELECT COUNT(1) from reservations WHERE checkin = 1").fetchall()[0][0]
            if count>=500:
                resp = jsonify(error="limit reached")
                resp.status_code = 200
            
            #check if id is present in reservations of the day
            result = con.execute("SELECT * from reservations WHERE id = '%s'" %id).fetchall()
            
            if result :
                #check in successful
                con.execute("UPDATE reservations SET checkin = 1 WHERE id = '%s'" %id)
                resp = jsonify(success=True)
                resp.status_code = 200
            else:
                #check-in failed
                resp = jsonify(success=False, error="ID not found")
                resp.status_code = 200
    #SQL exception handler
    except sqlite3.Error:
            resp = jsonify(success=False, error="/checkin went wrong")
            resp.status_code = 500
    con.close()
    return resp

# Endpoint that, if the received id is inside the museum,
# completes the checkout by deleting the id from the database
@app.route("/reservations/checkout/<id>")
def checkout(id):
    #connection to db
    con = sqlite3.connect('reservations.db')
    try:
        with con:
            #check if id is present in reservations of the day and that it has checked-in
            result = con.execute("SELECT * from reservations WHERE id = '%s' AND checkin = 1" %id).fetchall()
            if result :
                #checkout successful
                con.execute("DELETE FROM reservations WHERE id = '%s'" %id)
                resp = jsonify(success=True)
                resp.status_code = 200
            else:
                #checkout failed
                resp = jsonify(success=False, error="ID not found")
                resp.status_code = 200
    #SQL exception handler
    except sqlite3.Error:
        resp = jsonify(success=False, error="/checkout went wrong")
        resp.status_code = 500
    
    con.close()
    return resp