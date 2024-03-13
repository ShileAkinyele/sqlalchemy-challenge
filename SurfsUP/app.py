# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
from flask import Flask,jsonify

#################################################
# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################


# reflect an existing database into a new model
Base= automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
Base.classes.keys()


# Save references to each table
#Map measurement class
Measurement=Base.classes.measurement

#Map station class
Station=Base.classes.station


# Create our session (link) from Python to the DB
session= Session(engine)


#################################################
# Flask Setup
app=Flask (__name__)

#################################################
# Flask Routes
@app.route("/")
def welcome():
    
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date/start<br/>"
        f"/api/v1.0/date/start/end<br/>"
        
        
        )

#Defining the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)

#precipitation analysis
    months_ago=dt.date(2017,8,23)-dt.timedelta(days=365)
    prcp_scores=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=months_ago).all()

    session.close()

# Converting the results from the precipitation analysis to a list of dictionaries
    prcp_scores_list = []
    for date,prcp in prcp_scores:
        prcp_scores_dict={}
        prcp_scores_dict["date"]=date
        prcp_scores_dict["prcp"]=prcp
        prcp_scores_list.append(prcp_scores_dict)

# Returning the list as a JSON object
    return jsonify(prcp_scores_list)


#Defining the station route
@app.route("/api/v1.0/stations")
def station():
 
 #station analysis   
    session=Session(engine)
    station_list = session.query(Station.station).all()
    session.close()
    
#unpacking the result into a list
    all_stations=list(np.ravel(station_list))
 
#Returning the list as a JSON object   
    return jsonify(station = all_stations)


#Defining the tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)

#tobs analysis   
    previous_year = dt.date(2017,8,23)-dt.timedelta(days=365)

#getting the most active station
    sel=[Measurement.station,func.count(Measurement.station)]
    most_active=session.query(*sel).group_by(Measurement.station).order_by (func.count(Measurement.station).desc()).all()


#querrying the date and temperature observation for the most active station   
    date_temp_obs= session.query(Measurement.tobs,Measurement.date).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= previous_year).all()
    session.close()

#unpacking the result into a list
    all_date_temp_obs= list(np.ravel(date_temp_obs))
   
#Returning the list as a JSON object   
    return jsonify(temperatureanddate =all_date_temp_obs )


#Defining the start/start_end route
@app.route("/api/v1.0/date/<start>")
@app.route("/api/v1.0/date/<start>/<end>")
def stats(start=None,end=None):

    session=Session(engine)
    start_date = dt.datetime.strptime(start, "%m%d%Y")
    sel=[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    
    if not end:
     min_max_avg=session.query(*sel).filter(Measurement.date>=start_date).all()
    else:
       end_date = dt.datetime.strptime(end, "%m%d%Y") 
       min_max_avg=session.query(*sel).filter(Measurement.date>=start_date).filter(Measurement.date<=end_date).all()
    
    session.close()

#unpacking the result into a list
    min_max_avg_list= list(np.ravel(min_max_avg))
   
#Returning the list as a JSON object   
    return jsonify(min_max_avg_list)

   

   
    





                                                                                           
if __name__ == '__main__':
    app.run()
