#Import dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import numpy as np

#Create engine to connect with database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database into a new model
Base = automap_base()

#Reflect the tables
Base.prepare(engine, reflect=True)

#Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session (link)  to the DB
session = Session(engine)

def calculate_temps(first_day, last_day):
    """Temp MIN, Temp AVG, and Temp MAX for a list of dates.
    """
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= first_day).filter(Measurement.date <= last_day).all()

# Flask
app = Flask(__name__)

# Create routes
@app.route("/")
def welcome():
    return """
    Hi, this is my climate flask app, hope you like it!<br>
    Routes you can take: <br>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/&lt;start&gt; Please use YYYY-MM-DD format for the date <br> 
    /api/v1.0/&lt;start&gt;/&lt;end&gt; Please use YYYY-MM-DD format for the first and last day
    """

@app.route("/api/v1.0/precipitation")
def precipitation():
    outcome = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= "2016-08-23").\
    filter(Measurement.date <= "2017-08-23").all()

    precip_dict = []
    for row in outcome:
        date_dict = {}
        date_dict[row.date] = row.prcp
        precip_dict.append(date_dict)

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    outcome = session.query(Station.station).all()
    station_list = list(np.ravel(outcome))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    outcome = session.query(Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23").\
        filter(Measurement.date <= "2017-08-23").all()

    tobs_list = list(np.ravel(outcome))

    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def first_day(start):
    last_day = session.query(func.max(Measurement.date)).all()[0][0]
    temps = calculate_temps(start, last_day)
    temps_list = list(np.ravel(temps))
    return jsonify(temps_list)



@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    temps = calculate_temps(start, end)
    temps_list = list(np.ravel(temps))
    return jsonify(temps_list)


if __name__ == '__main__':
    app.run(debug=True)