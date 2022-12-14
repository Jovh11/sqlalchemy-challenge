from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
from datetime import datetime as dt

engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home_page():
    return (f'This is the homepage of the Hawaii precipitation API version 1<br/>'
            f'Here are the available routes<br/>'
            f'Shows all of the precipitaion in particular dates  /api/v1.0/precipitation<br/>'
            f'A list of all of the available stations  /api/v1.0/stations<br/>'
            f'This gives a list of all of the temperature observations in the most active station on Hawaii   /api/v1.0/tobs<br/>'
            f'This gives one week of temperature information from this date forward in YYYY-MM-DD format    /api/v1.0/<start><br/>'
            f'This gives all of the temperature information during this date range in YYYY-MM-DD format    /api/v1.0/<start>/<end>'
            )


@app.route('/api/v1.0/precipitation')
def ppt():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).group_by(measurement.date).all()
    rainfall = {}
    for value in results:
        rainfall[value.date] = value.prcp
    session.close()
    return jsonify(rainfall)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results = session.query(station.station, station.name).group_by(station.station).all()
    locations = {}
    for value in results:
        locations[value.station] = value.name
    session.close()
    return jsonify(locations)

@app.route('/api/v1.0/tobs')
def tobs():
    #find most active station
    session = Session(engine)
    activity = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active = activity[0][0]
    temps = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active).group_by(measurement.date).all()
    temp_data = {}
    for value in temps:
        temp_data[value.date] = value.tobs
    session.close()
    return(jsonify(temp_data))

@app.route('/api/v1.0/<start>')
def start(start:str):
    session = Session(engine)
    as_dt = dt.strptime(start, "%Y-%m-%d")
    temps = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= as_dt).group_by(measurement.date).all()
    temp_info = []
    session.close()
    for value in temps:
        temp = {}
        temp['date'] = value[0]
        temp['min'] = value[1]
        temp['max'] = value[2]
        temp['avg'] = value[3]
        temp_info.append(temp)
    return jsonify(temp_info)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)
    start_dt = dt.strptime(start, "%Y-%m-%d")
    end_dt = dt.strptime(end, "%Y-%m-%d")
    temps = session.query(measurement.date,func.min(measurement.tobs),func.max(measurement.tobs), func.avg(measurement.tobs)).filter(and_(measurement.date >= start_dt), (measurement.date <= end_dt)).group_by(measurement.date).all()
    temp_info = []
    session.close()
    for value in temps:
        temp = {}
        temp['date'] = value[0]
        temp['min'] = value[1]
        temp['max'] = value[2]
        temp['avg'] = value[3]
        temp_info.append(temp)
    return jsonify(temp_info)
    
if __name__ == "__main__":
    app.run(debug=True)

