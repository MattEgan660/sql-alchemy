import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from Flask import Flask, jsonify

#Setup Database & Create Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

measurment = Base.classes.measurment
station = Base.classes.station

#Create Session
session = Session(engine)

#Flask Setup
app = Flask(__name__)


#Flask Routes 
@app.route("/")
def main():
    return(
        f"Available Routes For the Surfs UP API:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        )


@app.route("/api/v1.0/precipitation")
def percipitaiton():


    recent_date = (session.query(measurment.date).order_by(measurment.date.desc()).first())
    recent_date = list(np.ravel(recent_date))[0]
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')

    previous_year = recent_date - dt.timedelta(days=365)

    percip_data = (session.query(measurment.date, measurment.prcp)\
                          .filter(measurment.date > previous_year)\
                          .order_by(measurment.date).all())
    
    percip_results = []
    for result in percip_data:
        row = {}
        row[measurment.date] = row[measurment.prcp]
        percip_results.append(row)

    return jsonify(percip_results)


@app.route("/api/v1.0/stations")
def stations():
    Station_results = session.query(station.station, station.name).all()

    return jsonify(Station_results)


@app.route("/api/v1.0/tobs")
def temperature():
    recent_date = (session.query(measurment.date).order_by(measurment.date.desc()).first())
    recent_date = list(np.ravel(recent_date))[0]
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')

    previous_year = recent_date - dt.timedelta(days=365)

    most_active = session.query(measurment.station, func.count(measurment.Station))\
                   .filter(measurment.date >= previous_year)\
                   .group_by(measurment.station)\
                   .order_by(func.count(measurment.station)).desc().first()
    
    temps = session.query(measurment.tobs).filter(measurment.station == most_active[0]).filter(measurment.date >= previous_year)
 
    temp_results = [result[0] for result in temps]
    return jsonify(temp_results)

@app.route("/api/v1.0/<start>")
def start_day(start):
    start_results = session.query(func.min(measurment.tobs), func.avg(measurment.tobs), func.max(measurment.tobs))\
                      .filter(measurment.date >= start).all()
    
    return jsonify(start_results)



@app.route("/api/v1.0/<start>/<end>")
def date_range(start,end):
    range_results = session.query(func.min(measurment.tobs), func.avg(measurment.tobs),func.max(measurment.tobs))\
                             .filter(measurment.date >= start).filter(measurment.date <= end).all()
    
    return jsonify(range_results)

if __name__ == '__main__':
    app.run(debug=True)