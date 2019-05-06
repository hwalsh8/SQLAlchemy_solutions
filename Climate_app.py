#Import necessary libraries
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Set up database information
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Calculate the date 1 year ago from the last data point in the database
prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
print("Date from previous year: ", prev_year)

#Start the server-import flask
from flask import Flask, jsonify

#create an app - Flask setup
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/"
    )

#Return 1 years worth of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    print("Date from previous year: ", prev_year)

    # Perform a query to retrieve the data and precipitation scores
    prep_data = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= prev_year).\
                        all()
    date_list=list()
    prcp_list=list()
    count=0
    for row in prep_data:
        count+=1
        date_list.append(row.date)
        prcp_list.append(row.prcp)
        print(row.date, row.prcp)

    #Convert the query results into a dictionary using date and prcp values
    prep_data_dict={"Date":date_list,
                    "Precipitation":prcp_list}

    #Return a JSON respresentation of the dictionary above.
    return jsonify(prep_data_dict)

#Return a list of stations 
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Measurement.station).distinct().all()

    #Return a JSON list of stations
    return jsonify(stations)


#Query date and temps for the previous year
@app.route("/api/v1.0/tobs")
def tobs():

    tempjson_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= prev_year).\
                    all()
    temp_list=list()
    count=0
    for row in tempjson_data:
        count+=1
        temp_list.append(row.tobs)
        #print(row.tobs)

    tempjson_dict={"Temperature":temp_list}   

    #Return a JSON list of Temperature Observations for the previous year
    return jsonify(tempjson_dict)


@app.route("/api/v1.0/<start>")
def startonly(start=None):
    startjson_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()

    
    #trying to create a dictionary for json output
    min_list=[]
    avg_list=[]
    max_list=[]
    count=0
    for row in startjson_data:
        count+=1
        min_list.append(row[0])
        avg_list.append(row[1])
        max_list.append(row[2])
        #print(row)

    cts_dict={'Min':min_list, 
            'Avg':avg_list,
            'Max':max_list}
    #print(cts_dict)

    return jasonify(cts_dict)




@app.route("/api/v1.0/<start>/<end>")
def dates_temp(start=None,end=None):

    dates_json_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    
    #trying to create a dictionary for json output
    min_list=[]
    avg_list=[]
    max_list=[]
    count=0
    for row in dates_json_data:
        count+=1
        min_list.append(row[0])
        avg_list.append(row[1])
        max_list.append(row[2])
        #print(row)

    all_dates_dict={'Min':min_list, 
            'Avg':avg_list,
            'Max':max_list}
    #print(all_dates_dict)

    return jasonify(all_dates_dict)

if __name__ == "__main__":
    app.run(debug=True)
