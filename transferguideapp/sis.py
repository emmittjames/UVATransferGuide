import json
import requests
from enum import Enum


BASEURL = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01'

class Term(Enum):
    FALL = 8
    SPRING = 2 


def format_term(term, year):
    """
    Parameters
    ----------
    term : Term
        takes in a term enum with FALL or SPRING
    year: string
        takes in a string representing a year
    Returns
    -------
    request
        returns the result of the http request
    """
    return "1" + year[-2:] + str(term.value)



def call_api(paramList):
    """
    Parameters
    ----------
    paramList: dict
        A dictonary mapping strings of arguments names to values
    Returns
    -------
    request
        returns the result of the http request
    """
    queryString = BASEURL
    for (arg, val) in paramList.items():
        queryString += '&' + arg + '=' + val
    return requests.get(queryString)


def request_data(paramList):
    """
    Parameters
    ----------
    paramList: dict
        A dictonary mapping strings of arguments names to values
    Raises
    ------
    Exception
        If the status code is not 200 (succesful)
    Returns
    -------
    request
        returns the result of the http request converted into a python dictonary
    """
    r = call_api(paramList)
    if(r.status_code == 200):
        return r.json()
    else:
        raise Exception('Api call failed with ' + str(r.status_code))

def unique_id(r):
    used_ids = []
    sanitized = []
    for c in r:
        if not c['crse_id'] in used_ids:
            used_ids.append(c['crse_id'])
            sanitized.append(c)
    return sanitized

