#!nerdl/bin/python3
from flask import Flask, Response, jsonify
from flask import request

import logging.config
from flask_cors import CORS, cross_origin

import urllib

import traceback
from src.genderIdentifier import GenderIdentifier
import traceback
import logging

app = Flask(__name__)
cors = CORS(app)

#arpas
arpa_configurations = dict()
endpoint = ""
graph = ""
uri = ""
file_id = 0


from flask import json

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers

@app.before_request
def before_request():
    if True:
        print("HEADERS, %s", request.headers)
        print("REQ_path, %s", request.path)
        print("ARGS, %s",request.args)
        print("DATA, %s",request.data)
        print("FORM, %s",request.form)
        print("VALUES, %s", request.values)

    app.logger.info("LOG HEADERS, %s", request.headers)
    app.logger.info("LOG REQ_path, %s", request.path)
    app.logger.info("LOG ARGS, %s",request.args)
    app.logger.info("LOG DATA, %s",request.data)
    app.logger.info("LOG FORM, %s",request.form)

        
@app.route('/', methods = ['POST', 'GET', 'OPTIONS'])
@cross_origin()
def api_message():
    content_dict = None
    declaration = None
    name = ""
    threshold = 0.0

    print("HEADERS:", request.headers)
    print("METHODS:", request.method)
    app.logger.info('METHODS: %s', request.method)
    app.logger.info('HEADERS: %s', request.headers)

    try:
    
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
                    print("Parse from ARGS")
                    name = request.form['name']
                    threshold = request.form['threshold']
                    return jsonify(results=quess(threshold=threshold, name=name))
                elif 'name' in request.args and 'threshold' in request.args:
                    print("Parse from ARGS")
                    threshold = request.args.get('threshold')
                    name = request.args.get('name')
                    if 'name' in request.values:
                        name = request.values['name']
                    else:
                        app.logger.error("Cannot get value: %s ", request.values)
                    if name != None and threshold != None:
                        return jsonify(results=quess(threshold=threshold, name=name))
                elif 'Name' in request.headers and 'Threshold' in request.headers:
                    print("Parse from ARGS")
                    threshold = float(request.headers['Threshold'])
                    name = request.headers['Name']
                    if name != None and threshold != None:
                        return jsonify(results=quess(threshold=threshold, name=name))
                else:
                    print("Unable to find parameters.")
                    print("Form:", request.form)
                    print("Args:", request.args)
                    print("Head:", request.headers)
                message = "Unable to process the request: missing name or threshold: name=%s, threshold=%s" % (str(name), str(threshold))
                message +=  "<p>Please give parameters using GET or POST method. GET method example: <a href='http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8' target='_blank'>http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8</a></p>"+\
                        "POST method can be used by transmitting the parameters using url, header, or a form."
                app.logger.error('this is an ERROR message: %s', message)
                return message

        elif request.method == "GET":
            print("Parse from ARGS")
            threshold = request.args.get('threshold')
            name = request.args.get('name')
            if name == None:
                app.logger.error("Gets wrong value: %s %s", request.args.get('name'), request.args)
                if 'name' in request.values:
                    name = request.values['name']
                else:
                    app.logger.error("Cannot get value: %s ", request.values)
            if name != None and threshold != None:
                return jsonify(results=quess(threshold=threshold, name=name))
            else:

                message = "Parameters could not be identified: name=%s, threshold=%s" % (str(name), str(threshold))
                message += "<p>Please give parameters using GET or POST method. GET method example: <a href='http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8' target='_blank'>http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8</a></p>"+\
                        "POST method can be used by transmitting the parameters using url, header, or a form."
                app.logger.error('this is an ERROR message: %s', message)
                return message
        else:
            app.logger.error("Other request method: %s", request.method)
            app.logger.error('This method is not yet supported')
            print("Other request method:", request.method)
            print("This method is not yet supported")
    except Exception as e:
        print("Error happened during execution", e)
        traceback.print_exc()
        returning = {'results':str(e), "status":500, 'message':"Error happened during execution", 'params':request.values}
        app.logger.error('this is an ERROR message %s', returning)
        return returning

    return "Something went wrong..."
        
@app.route('/guess/<name>')
def guess_gender_using_default_threshold(name):
    threshold = 0.8
    print("Using default threshold:", threshold)
    return jsonify(results=quess(threshold=threshold, name=name))
    
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

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.info('this is an TEST message')
    #app.run()

#if __name__ == '__main__':
    #    p = 5002
    #    h = '0.0.0.0'
#    app.logger.debug('this is an DEBUG message')
#    app.logger.info('this is an INFO message')
#    app.logger.warning('this is a WARNING message')
#    app.logger.error('this is an ERROR message')
#    app.logger.critical('this is a CRITICAL message')
#    app.run(debug=True)