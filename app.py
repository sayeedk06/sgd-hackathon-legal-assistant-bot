from flask import Flask, request, make_response, jsonify
import json
from sklearn.externals import joblib
import numpy as np
import pandas as pd
import os

data = pd.read_csv("helpers.csv")
data['Organisation'].fillna('',inplace=True)
data['Contact'].fillna('',inplace=True)

selected_features = ['Access to Information','Citizenship',
       'Corruption', 'Criminal Justice','Economic Empowerment',
       'Education', 'Environmental Justice','Family',
       'Gender-based violence', 'Generalist Legal Services', 'Governance',
       'Health',"Women's Rights"]


def make_description(lawyer_id):
    row = data.iloc[lawyer_id]
    name = row["Name"]
    org = str(row["Organisation"])
    contact = str(row['Contact'])
    return name + '\n' + org + '\n' + contact

def make_query(text):
    result = []
    for feature in selected_features:
        if feature.lower() in text:
            result.append(1)
        else:
            result.append(0)
    return result
    

    
# initialize the flask app
app = Flask(__name__)
knn = joblib.load("knn.pickle")

# default route
@app.route('/')
def index():
    return 'Hello World!'
# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    req = request.get_json(force=True)
    text = req.get("queryResult").get("queryText")
    print(text)
    query = make_query(text)
    query = np.array(query).reshape(1,-1)
    _ , indices = knn.kneighbors(query)
    top_match = indices[0][0]
    result = make_description(top_match)
    return make_response(jsonify({'fulfillmentText': result }))
# run the app
if __name__ == '__main__':
   app.run(debug=True)