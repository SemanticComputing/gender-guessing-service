# gender-guessing-service


## About

Using person name ontology (http://light.onki.fi/henkilonimisto/en/) the application calculates statistically most probable gender for a person name. It uses the first names to identify person's gender and therefore using more than one first names is recommended to get accurate reading. It cannot be used yet to identify other than finnish and maybe swedish names and it only can identify 2 genders: male and female (because the ontology uses data from the Population Register Centre).

## Dependencies

* Python 3.5.2
* SparqlWrapper
* flask
* flask_cors

For more information, check requirements.txt

## Usage

### Command line usage

To run:

```
python3 run.py -n "Minna Susanna Claire Tamper" -t 0.6
```

#### Parameters

params:

-n or --name for names

-t or --threshold for setting probability threshold (optional, by default 0.8)

#### Results

Results are retuned in json format:

```
{"results":{"gender":"Female","name":"Minna Susanna Claire Tamper","probabilities":{"Female":0.9999999999946162,"Male":5.383809595933431e-12}}}
```
### Http Interface

To run use flask as follows:

1. export FLASK_APP=httpInterface.py
2. flask run
3. open browser and go to http://localhost:5000/ optionally there is the interface http://localhost:5000/quess/<name> that can be used with the threshold of 0.8.

#### Parameters

The http interface supports GET and POST methods for the users. Therefore users can give the parameters for GET method in the url:

```
http://127.0.0.1:5000/?name=Minna Susanna Claire Tamper&threshold=0.8
```
Post requests support parameters in the url, header, and from a form.


#### Results

Results are retuned in json format:

```
{"results":{"gender":"Female","name":"Minna Susanna Claire Tamper","probabilities":{"Female":0.9999999999946162,"Male":5.383809595933431e-12}}}
```

## Running in Docker

`./docker-build.sh`: builds the service

`./docker-run.sh`: runs the service
