'''
Created on 26 Apr 2019

@author: tamperm1
'''
from SPARQLWrapper import SPARQLWrapper, JSON, BASIC
import logging
import re, traceback, sys
import validators

class SparqlQueries(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def query_names(self, name, endpoint):

        query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label ?gender (sum(?lkm)as ?count) ?type WHERE {
          VALUES ?ngram {
            "$name"
          }
          BIND(STRLANG(?ngram,"fi") AS ?label)
          ?name a <http://ldf.fi/schema/henko/WrittenNameForm> .
          ?name skos:prefLabel ?label .
          ?nameUsage <http://ldf.fi/schema/henko/hasName> ?name .
          ?nameUsage <http://ldf.fi/schema/henko/count> ?lkm .
          ?used <http://ldf.fi/schema/henko/isUsed> ?nameUsage .
          ?used a ?typed .
          ?typed rdfs:label|skos:prefLabel ?type .
          OPTIONAL {?nameUsage <http://ldf.fi/schema/henko/gender> ?gender .
          }
          FILTER(lang(?type) = 'fi')
        } GROUP BY ?label ?gender ?type
        """
        query = query.replace('$name', name)
        
        #print("name=", name)
        #print("endpoint= %s", endpoint)
        #print("query= %s", query)

        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        return results
    
    def do_split(self, txt):
        delimiters = [" ", "...", "(", ")", "/", ",", "."]
        regexPattern = '|'.join(map(re.escape, delimiters))
        print(regexPattern)
        return re.split(regexPattern, txt)
        #return filter(None, re.split("[, /!?:()]+", txt))
    
    def get_name_data(self, person_name, endpoint):
        males = dict()
        females = dict()
        other = dict()

        try:
            if validators.url(endpoint):
                names = self.do_split(person_name)
                for name in names:
                    results = self.query_names(name, endpoint)

                    if len(results["results"]["bindings"]) > 0:
                        for result in results["results"]["bindings"]:
                            label = str(result["label"]["value"])
                            if 'gender' in result:
                                gender = str(result["gender"]["value"]).replace("http://schema.org/", "")
                            else:
                                gender = ""
                            count = int(result["count"]["value"])
                            type = str(result["type"]["value"])

                            print("gender:", gender)
                            print("count:", count)
                            print("label:", label)
                            print("type:", type)

                            if type == "Etunimi" and len(gender)>0:
                                if gender == "Female":
                                    females[name] = count
                                else:
                                    males[name] = count
                            elif type == "Sukunimi" and len(gender) == 0:
                                if name == names[-1]:
                                    other[name] = count
                            else:
                                print("Unable to identify name:", name)
        except ValueError as verr:
            print("Unable to query, url is not valid:", sys.exc_info()[0])
            traceback.print_exc()
        except Exception as err:
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
        finally:
            return females, males, other
                        
        return females, males, other
    