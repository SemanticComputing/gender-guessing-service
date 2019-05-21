'''
Created on 26 Apr 2019

@author: tamperm1
'''

import re
from src.sparqlQueries import SparqlQueries

class GenderIdentifier(object):
    '''
    classdocs
    '''


    def __init__(self, name="", threshold=0.8):
        '''
        Constructor
        '''
        print("Params", name, threshold)
        if threshold == None:
            self._probability_threshold = 0.8
        else:
            self._probability_threshold = float(threshold)
        self.females = dict()
        self.males = dict()
        self.other = dict()
        self.archive = set()
        self._probabilities = dict()
                
        self._name = name
        if len(name) > 0:
            self._gender, self._probabilities = self.identify_gender(name)
        else:
            self.gender = None   
            
                 
    # getters
        
    def get_name(self):
        return self._name
    
    def get_gender(self):
        return self._gender
    
    def get_probability_threshold(self):
        return self._probability_threshold
    
    def get_gender_probabilities(self):
        return self._probabilities
    
    # setters
    
    def set_name(self, name):
        self._name = name
    
    def set_gender(self, gender):
        self._gender = gender
    
    def set_probability_threshold(self, threshold):
        self._probability_threshold = threshold
        
    def identify_gender(self, name):
        sparql = SparqlQueries()
        females, males, familyname = sparql.get_name_data(name)
        
        self.females = females
        self.males = males
        self.other = familyname
        
        return self.approx_gender(name)
        
    def do_split(self, txt):
        #delimiters = " ", "...", "(", ")", "/", ",", "."
        delimiters = [" ", "...", "(", ")", "/", ",", "."]
        regexPattern = '|'.join(map(re.escape, delimiters))
        return re.split(regexPattern, txt)
    
    '''
    @author: ptleskinen
    '''
    def approx_gender(self, txt):
        
        #print("Input", txt)
        
        if len(txt)<2: return "Unknown", {}
        if re.match(r'^[^A-ZÖÄÅ]+$',txt): return "Unknown", {}
        if re.match(r'.+?(poika|veli|kuningas|herttua|ruhtinas|isä|keisari|metropoliitta|piispa|prinssi)$', txt): return "Male", {"Female": 0, "Male":1}
        if re.match(r'.+?(tytär|prinsessa|herttuatar|kuningatar|äiti|keisarinna|sisko|papitar)$', txt): return "Female", {"Female": 1, "Male":0}
                
        probs = [0.5,0.5]
        for t in self.do_split(txt):
            if re.match(r'[a-zöäå]+$',t): continue
            
            pM = self.males[t] if t in self.males else (10 if re.match(r'.+?poika$', t) else 1)
            pF = self.females[t] if t in self.females else (10 if re.match(r'.+?tytär$', t) else 1)
            
            if pM==1 and pF==1 and re.match(r'.+?a$', t):
                self.archive.add(t)
            if pM+pF>0:
                probs[0] *= pM/(pM+pF)
                probs[1] *= pF/(pM+pF)
            
        
        tot = probs[0]+probs[1]
        if tot==0:
            print("Unambiguous {}: {}/{}".format(txt, probs[0], probs[1]))
            return "Unknown", {}
        
        probs[0] /= tot
        probs[1] /= tot
        
        if probs[0]>self._probability_threshold:
            return "Male",{"Female": probs[1], "Male":probs[0]}
        elif probs[1]>self._probability_threshold:
            return "Female",{"Female": probs[1], "Male":probs[0]}
        else:
            print("Unambiguous {}: {}/{}".format(txt, probs[0], probs[1]))
        
        return "Unknown", {"Female": probs[1], "Male":probs[0]}