similar-nodes
=============

Identifies nodes similar to a subset of nodes (expressed as JSON) using a TFIDF-based approach. Implementation is specific to the given JSON format, but should be trivial to generalize.


How to use
==========
1. Export the instance details to instances.json
2. Enter the search term(s) in 'settings.py'
3. Run main.py to see instances that are similar to those matching the search terms.


Algorithm
=========

1. Generate separate Term Frequencies (TF) of corpus and search results
2. Use corpus TF to normalize (IDF)
3. Return instances from corpus having highest matches excluding search results


To Do
=====

- Allow specifying partial terms e.g. 'medium' instead of 'm1.medium'
- Clean up the code (apply map, filter and eliminate loops)
- Implement a statistical approach to grouping of device count and size values
- Identify a smarter way to determine similarity threshold (currently a setting)
- Expose a RESTful API
- Invoke an API to gather instance details
- Introduce logging