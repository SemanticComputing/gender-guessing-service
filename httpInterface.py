#!nerdl/bin/python3
from flask import Flask, Response, jsonify
from flask import request, abort

from flask_cors import CORS, cross_origin
from src.genderIdentifier import GenderIdentifier
import traceback
import logging, os, sys
from datetime import datetime

import configparser
from configparser import Error, ParsingError, MissingSectionHeaderError, NoOptionError, DuplicateOptionError, DuplicateSectionError, NoSectionError
import traceback

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
    result = dict()
    result['service'] = "Gender guessing service"
    result['date'] = datetime.today().strftime('%Y-%m-%d')

    print("HEADERS:", request.headers)
    print("METHODS:", request.method)
    app.logger.info('METHODS: %s', request.method)
    app.logger.info('HEADERS: %s', request.headers)

    env = 'DEFAULT'

    # read environment from environment variable
    try:
        env = os.environ['GENDER_IDENTIFICATION_CONFIG_ENV']
    except KeyError as kerr:
        print("Environment variable GENDER_IDENTIFICATION_CONFIG_ENV not set:", sys.exc_info()[0])
        traceback.print_exc()
        env = None
        abort(500, 'Problem with setup: internal server error')
    except Exception as err:
        print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()
        env = None
        abort(500, 'Unexpected Internal Server Error')
    endpoint, threshold = read_configs(env)

    try:
        if request.method == "POST":
            print("Data (form):", request.form)
            print("Data (data):", request.data)
            if len(request.data) > 0 and len(request.headers['Content-Type'])>0:
                if request.headers['Content-Type'] == 'text/plain':

                    threshold = 0
                    name = str(request.data.decode('utf-8'))

                    result['results'] = quess(threshold=threshold, name=name, endpoint=endpoint)

                else:
                    print("Bad type", request.headers['Content-Type'])
                    return "415 Unsupported Media Type ;)"

            else:
                if 'name' in request.form and 'threshold' in request.form:
                    print("Parse from ARGS")
                    name = request.form['name']
                    threshold = request.form['threshold']
                    result['results'] = quess(threshold=threshold, name=name, endpoint=endpoint)
                elif 'name' in request.args and 'threshold' in request.args:
                    print("Parse from ARGS")
                    threshold = request.args.get('threshold')
                    name = request.args.get('name')
                    if 'name' in request.values:
                        name = request.values['name']
                    else:
                        app.logger.error("Cannot get value: %s ", request.values)
                    if name != None and threshold != None:
                        result['results'] = quess(threshold=threshold, name=name, endpoint=endpoint)
                elif 'Name' in request.headers and 'Threshold' in request.headers:
                    print("Parse from ARGS")
                    threshold = float(request.headers['Threshold'])
                    name = request.headers['Name']
                    if name != None and threshold != None:
                        result['results'] = quess(threshold=threshold, name=name, endpoint=endpoint)
                else:
                    print("Unable to find parameters.")
                    print("Form:", request.form)
                    print("Args:", request.args)
                    print("Head:", request.headers)
                message = "Unable to process the request: missing name or threshold: name=%s, threshold=%s" % (str(name), str(threshold))
                message +=  "<p>Please give parameters using GET or POST method. GET method example: <a href='http://nlp.ldf.fi/gender-identification?name=Minna Susanna Claire Tamper&threshold=0.8' target='_blank'>http://nlp.ldf.fi/gender-identification?name=Minna Susanna Claire Tamper&threshold=0.8</a></p>"+\
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
                app.logger.info("Gets value: %s %s", name, threshold)
                result['results'] = quess(threshold=threshold, name=name, endpoint=endpoint)
            else:

                message = "Parameters could not be identified: name=%s, threshold=%s" % (str(name), str(threshold))
                message += "<p>Please give parameters using GET or POST method. GET method example: <a href='http://nlp.ldf.fi/gender-identification?name=Minna Susanna Claire Tamper&threshold=0.8' target='_blank'>http://nlp.ldf.fi/gender-identification?name=Minna Susanna Claire Tamper&threshold=0.8</a></p>"+\
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
        result['results'] = {'error':str(e), "status":500, 'message':"Error happened during execution", 'params':request.values}
        app.logger.error('this is an ERROR message %s', result['results'])

    return jsonify(result)
        
@app.route('/guess/<name>')
def guess_gender_using_default_threshold(name):
    env = 'DEFAULT'

    # read environment from environment variable
    try:
        env = os.environ['GENDER_IDENTIFICATION_CONFIG_ENV']
    except KeyError as kerr:
        print("Environment variable GENDER_IDENTIFICATION_CONFIG_ENV not set:", sys.exc_info()[0])
        traceback.print_exc()
        env = None
        abort(500, 'Problem with setup: internal server error')
    except Exception as err:
        print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()
        env = None
        abort(500, 'Unexpected Internal Server Error')
    endpoint, threshold = read_configs(env)

    result = dict()
    result['service'] = "Gender guessing service"
    result['date'] = datetime.today().strftime('%Y-%m-%d')
    print("Using default threshold:", threshold)
    result['results'] = quess(threshold=threshold, name=name, endpoint=endpoint)
    return jsonify(result)
    
def quess(threshold, name, endpoint):
    try:
        json_response = dict()
        genId = GenderIdentifier(name=name, threshold=threshold, endpoint=endpoint)
        json_response['name']= genId.get_name()
        json_response['gender']= genId.get_gender()
        json_response['probabilities']= genId.get_gender_probabilities()
        return json_response
    except Exception as e:
        app.logger.error('Error happened!')
        app.logger.error('Something went wrong %s', str(e))

def read_configs(env):
    henko_endpoint=""
    gender_guess_threshold=0.8

    try:
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        if env in config:
            henko_endpoint, gender_guess_threshold = read_env_config(config, env)
        elif env == None or len(env) == 0:
            err_msg = 'The environment is not set: %s' % (env)
            raise Exception(err_msg)
        else:
            if 'DEFAULT' in config:
                henko_endpoint, gender_guess_threshold = read_env_config(config)
            else:
                err_msg = 'Cannot find section headers: %s, %s' % (env, 'DEFAULT')
                raise MissingSectionHeaderError(err_msg)
    except Error as e:
        print("[ERROR] ConfigParser error:", sys.exc_info()[0])
        traceback.print_exc()
        abort(500)
    except Exception as err:
        print("[ERROR] Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()
        abort(500)

    return henko_endpoint, gender_guess_threshold

def read_env_config(config, env='DEFAULT'):
    henko_endpoint=""
    gender_guess_threshold=0.8
    if 'henko_endpoint' in config[env]:
        henko_endpoint = config[env]['henko_endpoint']
    else:
        print("Unable to find: henko_endpoint in ", config[env])


    if 'gender_guess_threshold' in config[env]:
        gender_guess_threshold = float(config[env]['gender_guess_threshold'])
    else:
        print("Unable to find: gender_guess_threshold in ", config['DEFAULT'])

    return henko_endpoint, gender_guess_threshold

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
