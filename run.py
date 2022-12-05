#!/usr/local/bin/python2.7
# encoding: utf-8
'''
src.run -- shortdesc

src.run is a description

It defines classes_and_methods

@author:     tamperm1

@copyright:  2019 organization_name. All rights reserved.

@license:    license

@contact:    minna.tamper@aalto.fi
@deffield    updated: Updated
'''

import sys
import os
from src.genderIdentifier import GenderIdentifier

import configparser
from configparser import Error, ParsingError, MissingSectionHeaderError, NoOptionError, DuplicateOptionError, DuplicateSectionError, NoSectionError
import traceback
from datetime import datetime as dt


from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2019-04-26'
__updated__ = '2019-04-26'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
def help():
    print("Help!")

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    json_response = dict()
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2019 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-n", "--name", dest="name", help="Give the name you want to use to identify gender.")
        parser.add_argument("-t", "--threshold",type=float, nargs='?', const=0.8, help="set probability threshold [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        #parser.add_argument('-h', '--help', action='help', help="Print help!")
        #parser.add_argument('-v', '--verbose', help="set verbosity level [default: %(default)s]")
        #parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')

        env = 'DEFAULT'

        # read environment from environment variable
        try:
            env = os.environ['GENDER_IDENTIFICATION_CONFIG_ENV']
        except KeyError as kerr:
            print("Environment variable GENDER_IDENTIFICATION_CONFIG_ENV not set:", sys.exc_info()[0])
            traceback.print_exc()
            env = None
            sys.exit('Problem with setup: internal server error')
        except Exception as err:
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
            env = None
            sys.exit('Unexpected Internal Server Error')
        endpoint, threshold = read_configs(env)

        # Process arguments
        args = parser.parse_args()

        #paths = args.paths
        #verbose = int(args.verbose)
        name = args.name
        threshold = args.threshold
        
        genId = GenderIdentifier(name=name, threshold=threshold, endpoint=endpoint)

        #if verbose > 0:
        #    print("Verbose mode on")

        #for inpath in paths:
            ### do something with inpath ###
        #    print(inpath)
        json_response['name']= genId.get_name()
        json_response['gender']= genId.get_gender()
        json_response['probabilities']= genId.get_gender_probabilities()
        return json_response
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")

        message = "<h3>Unable to process request</h3><p>Unable to retrieve results for text (%s).</p>" % str(
            request.args.get('text'))
        message += "<p>Please give parameters using GET or POST method. GET method example: <a href='http://127.0.0.1:5000/?text=Minna Susanna Claire Tamper' target='_blank'>http://127.0.0.1:5000/?text=Minna Susanna Claire Tamper</a></p>" + \
                   "POST method can be used by transmitting the parameters using url, header, or a form."
        data = {"status": -1, "error": str(message), "service": "Gender Identification Service",
                "timestamp": dt.today().strftime('%Y-%m-%d %H:%M:%S'), "version": "version 1.1-beta"}
        return data

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
        sys.exit("Internal Server Error (500)")
    except Exception as err:
        print("[ERROR] Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit("Internal Server Error (500)")

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

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'src.run_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())