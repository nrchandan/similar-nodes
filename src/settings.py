'''
Settings that drive the identification of similar nodes.

'''

# Comma-separated list of search terms
SEARCH_TERMS = ['java', 'm3.xlarge']

# Search type. Possible values: 'AND' 'OR'
SEARCH_TYPE = 'AND'

# This application returns instances that are similar along with
# the factors that were key to identifying similarity. This setting
# limits the number of factors that are returned in the result.
NUM_CAUSES = 5

# Terms that have less distinct values than this setting are ignored.
MIN_DISTINCT = 3

# Terms that have distinct values higher than this percentage are ignored.
MAX_DISTINCT_PCT = 50

# Results that score higher than this number are considered similar.
THRESHOLD_SIMILARITY_SCORE = 50

# The instance identifier attribute
INSTANCEID = 'instanceId'
