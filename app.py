import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
app = Flask(__name__)

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

@app.route("/")
def home():
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate (in YYYY-MM-DD format)<br/>"
        f"/api/v1.0/startdate/enddate (in YYYY-MM-DD format)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()
    all_precepitation=[]
    for date,prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precepitation.append(precipitation_dict)
    return jsonify(all_precepitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()
    all_station=[]
    for id,station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict['elevation']=elevation
        all_station.append(station_dict)
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tempartureobs():
    session = Session(engine)
    results_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    str_date=list(np.ravel(results_date))[0]
    latest_date=dt.datetime.strptime(str_date,"%Y-%m-%d")
    year_back=latest_date-dt.timedelta(days=366)
    results=session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).\
            filter(Measurement.date>=year_back).all()
    session.close()
    all_temperature=[]
    for tobs,date in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        all_temperature.append(tobs_dict)
    return jsonify(all_temperature)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    session = Session(engine)
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    temp_obs={}
    temp_obs["min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    session = Session(engine)
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    temp_obs={}
    temp_obs["min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)


if __name__ == '__main__':
    app.run(debug=True)