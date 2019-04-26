# gender-guessing-service


## About

Using person name ontology (http://light.onki.fi/henkilonimisto/en/) the application calculates statistically most probable gender for a person name. It uses the first names to identify person name and therefore more than one first names are required currently to get accurate reading. It cannot be used yet to identify other than finnish and maybe swedish names and it only can identify 2 genders: male and female (because the ontology uses data from the Population Register Centre). 

## Dependencies

Python 3.5.2
SparqlWrapper

## Usage

To run:

```
python3 run.py -n "Minna Susanna Claire Tamper" -t 0.6 
``` 

params: 

-n or --name for names

-t or --threshold for setting probability threshold (optional, by default 0.8)

results are retuned in json format

```
{'name': 'Minna Susanna Claire Tamper', 'gender': 'Female'}
```
