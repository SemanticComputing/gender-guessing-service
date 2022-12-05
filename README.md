# gender-guessing-service


## About

Using person name ontology (http://light.onki.fi/henkilonimisto/en/) the application calculates statistically most probable gender for a person name. It uses the first names to identify person's gender and therefore using more than one first names is recommended to get accurate reading. It cannot be used yet to identify other than finnish and maybe swedish names and it only can identify 2 genders: male and female (because the ontology uses data from the Population Register Centre). However, using the threshold parameter the certainty of the gender of a name can be tuned. If the name's gender probability is lesser than the given threshold, the service returns unknown.

### API

The service API description can be found from [Swagger](https://app.swaggerhub.com/apis-docs/SeCo/nlp.ldf.fi/1.0.0#/gender-identification).

### Publications

* Minna Tamper, Petri Leskinen, Jouni Tuominen and Eero Hyvönen: Modeling and Publishing Finnish Person Names as a Linked Open Data Ontology. 3rd Workshop on Humanities in the Semantic Web (WHiSe 2020), pp. 3-14, CEUR Workshop Proceedings, vol. 2695, June, 2020.

## Dependencies

* Python 3.5.2
* SparqlWrapper
* flask
* flask_cors
* validators

For more information, check requirements.txt

## Usage

## Configurations

The configurations for the service can be found from the config/config.ini file and configured based on service usage.

List of configurations available:

* henko_endpoint (default: http://ldf.fi/henko/sparql): sparql endpoint for quering person names
* gender_guess_threshold (default: 0.8): gender identification accuracy threshold that is given to the gender guessing service

In order to use these configurations, set the environment variable GENDER_IDENTIFICATION_CONFIG_ENV to 'DEFAULT' or to you personal setting. The value is the section name in the config.ini file where the personal settings can be set for the attributes (configurations) defined above.


### Command line usage

First set environment variable GENDER_IDENTIFICATION_CONFIG_ENV.

Setting it up in Ubuntu (example):
```
export GENDER_IDENTIFICATION_CONFIG_ENV='DEFAULT'

```

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

`docker-compose up`: builds and runs Gender guessing service and the needed HENKO Fuseki service

The following configuration parameter must be passed as environment variable to the container:

* HENKO_ENDPOINT_URL

Other configuration parameters should be set by using a config.ini (see section Configurations above) which can be e.g. bind mounted to container's path `/app/conf/config.ini`.
