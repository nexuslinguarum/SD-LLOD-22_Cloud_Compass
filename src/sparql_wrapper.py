import rdflib
from rdflib import Graph
from rdflib.namespace import DC, RDF, FOAF, RDFS
from rdflib import URIRef, BNode, Literal
import networkx as nx
import io
import pydotplus
from IPython.display import display, Image
from rdflib.tools.rdf2dot import rdf2dot

# Helper function for vizualizing RDF graph
def visualize(g):
    stream = io.StringIO()
    rdf2dot(g, stream, opts = {display})
    dg = pydotplus.graph_from_dot_data(stream.getvalue())
    png = dg.create_png()
    display(Image(png)) 

# CLASS SPARQLEndpoint that ease the use of SPARQL queries in python
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET, POSTDIRECTLY, CSV, TURTLE
import requests
import pandas as pd
pd.set_option('display.max_colwidth', None)

import functools

def withReturnFormat(result_format):
    def decorator_withReturnFormat(func):
        @functools.wraps(func)
        def wrapper_withReturnFormat(self, *args, **kwargs):
          previous_format = self.wrapper.returnFormat
          self.wrapper.setReturnFormat(result_format)
          value = func(self, *args, **kwargs)
          self.wrapper.setReturnFormat(previous_format)
          return value
        return wrapper_withReturnFormat
    return decorator_withReturnFormat

class SPARQLEndpoint:
  
  def __init__(self, sparql_endpoint, http_query_method=POST, result_format=JSON, token=None):
    self.wrapper = SPARQLWrapper(sparql_endpoint)

    #sparql_client.addCustomHttpHeader("Content-Type", "application/sparql-query")
    if token:
        self.wrapper.addCustomHttpHeader("Authorization","Bearer {}".format(token))
    self.wrapper.setMethod(http_query_method)
    self.wrapper.setReturnFormat(result_format)
    if http_query_method == POST:
        self.wrapper.setRequestMethod(POSTDIRECTLY)
    
  def query(self, query):
    self.wrapper.setQuery(query)
    return self.wrapper.queryAndConvert()

  # Convert SPARQL results into a Pandas data frame
  def sparql2dataframe(self, json_sparql_results):
    cols = json_sparql_results['head']['vars']
    out = []
    for row in json_sparql_results['results']['bindings']:
        item = []
        for c in cols:
            item.append(row.get(c, {}).get('value'))
        out.append(item)
    return pd.DataFrame(out, columns=cols)
  
  def query_as_dataframe(self, query):
    return self.sparql2dataframe(self.query(query))
    
  @withReturnFormat(TURTLE)
  def construct(self, query):
    self.wrapper.setQuery(query)
    g = Graph()
    g.parse(self.wrapper.query().convert())
    return g