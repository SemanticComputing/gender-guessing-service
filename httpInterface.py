#!nerdl/bin/python3
from flask import Flask, Response, jsonify
from flask import request

import logging.config
from flask_cors import CORS, cross_origin

import urllib

import traceback
from src.genderIdentifier import GenderIdentifier


app = Flask(__name__)
cors = CORS(app)

#arpas
arpa_configurations = dict()
endpoint = ""
graph = ""
uri = ""
file_id = 0


from flask import json

@app.before_request
def before_request():
    if True:
        print("HEADERS, %s", request.headers)
        print("REQ_path, %s", request.path)
        print("ARGS, %s",request.args)
        print("DATA, %s",request.data)
        print("FORM, %s",request.form)
        
@app.route('/', methods = ['POST', 'GET', 'OPTIONS'])
@cross_origin()
def api_message():
    content_dict = None
    declaration = None

    print("HEADERS",request.headers)
    #print("Type:",request.headers['Content-Type'])
    print("Method:",request.method)
    
    if request.method == "POST":
        print("Data (form):", request.form)
        print("Data (data):", request.data)
        if len(request.data) > 0 and len(request.headers['Content-Type'])>0:
            if request.headers['Content-Type'] == 'text/plain':
                #try:
                #    doc.parse_text(urllib.parse.unquote(str(request.data,'utf-8')))
                #except Exception as err:
                #    print(err)
                #    print(traceback.format_exc())
                threshold = 0
                name = None
        
                return jsonify(results=quess(threshold=threshold, name=name))
            
            elif request.headers['Content-type'] == "application/octet-stream":
                threshold = 0
                name = None
    
                return jsonify(results=quess(threshold=threshold, name=name))
            else:
                print("Bad type", request.headers['Content-Type'])
                return "415 Unsupported Media Type ;)"

        else:
            if 'name' in request.form and 'threshold' in request.form:
                name = request.form['name']
                threshold = request.form['threshold']
                return jsonify(results=quess(threshold=threshold, name=name))
            elif 'name' in request.args and 'threshold' in request.args:
                threshold = request.args.get('threshold')
                name = request.args.get('name')
                if name != None and threshold != None:
                    return jsonify(results=quess(threshold=threshold, name=name))
            elif 'Name' in request.headers and 'Threshold' in request.headers:
                threshold = request.headers['Threshold']
                name = request.headers['name']
                if name != None and threshold != None:
                    return jsonify(results=quess(threshold=threshold, name=name))
            
            return "<strong>Unable to process the request: missing name or threshold.</strong> \n"+\
                   "<p>Please give parameters using GET or POST method. GET method example: <a href='http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8' target='_blank'>http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8</a></p>"+\
                    "POST method can be used by transmitting the parameters using url, header, or a form."
    elif request.method == "GET":
        threshold = request.args.get('threshold')
        name = request.args.get('name')
        if name != None and threshold != None:
            return jsonify(results=quess(threshold=threshold, name=name))
        else:
            message = "Parameters could not be identified: name=%s, threshold=%s" % (str(name), str(threshold))
            message += "<p>Please give parameters using GET or POST method. GET method example: <a href='http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8' target='_blank'>http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8</a></p>"+\
                    "POST method can be used by transmitting the parameters using url, header, or a form."
            return message
    else:
        print("Other request method:", request.method)
        print("This method is not yet supported")
        
    return "Something went wrong..."
        
@app.route('/guess/<name>')
def quess_gender_using_default_threshold(name):
    threshold = 0.8
    print("Using default threshold:", threshold)
    return quess(threshold=threshold, name=name)
    
def quess(threshold, name):
    json_response = dict()
    genId = GenderIdentifier(name=name, threshold=threshold)
    json_response['name']= genId.get_name()
    json_response['gender']= genId.get_gender()
    json_response['probabilities']= genId.get_gender_probabilities()
    return json_response

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    p = 5002
    h = '0.0.0.0'
    app.run(host=h, port=int(p), debug=True, threaded=True)