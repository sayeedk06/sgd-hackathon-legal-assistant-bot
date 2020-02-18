from flask import Flask, request, make_response, jsonify, render_template
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
    name = str(row["Name"])
    org = str(row["Organisation"])
    contact = str(row['Contact'])
    return str(name + '.' + org + '.' + contact)

def make_query(text):
    result = []
    for feature in selected_features:
        if feature.lower() in text:
            result.append(1)
        else:
            result.append(0)
    return result


Logo_folder = os.path.join('static', 'logo_folder')
# initialize the flask app
app = Flask(__name__)
knn = joblib.load("knn.pickle")
app.config['UPLOAD_FOLDER'] = Logo_folder
# default route
@app.route('/')
def index():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'hello.png')
    return render_template("home.html", user_image=full_filename)

@app.route('/registration')
def registration():
    return render_template("registration.html")

@app.route('/user-registration')
def Userregistration():
    return render_template("userRegistration.html")

@app.route('/review')
def review():
    return render_template('review.html')


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
    second = indices[0][1]
    third = indices[0][2]
    result = "1. "+ make_description(top_match) + "  2. " + make_description(second) +"  3. " + make_description(third)
    #result = "1. "+ result1 + "  2.  " + result2 + "  3.  " + result3
    result = result + "Would you like us to connect you to these lawyers?"
    return make_response(jsonify({'fulfillmentText': result }))
# run the app
if __name__ == '__main__':
   app.run(debug=True)
