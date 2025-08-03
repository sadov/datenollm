import os
import dateno.core

DATENO_API_KEY = os.getenv('DATENO_API_KEY')

# Dateno search machinery
def index_search(query, filters, offset=0, page=1, limit=500):
    "Call Dateno API for search in index"
    print(f'index_search {query=} {filters=}')

    cmd=dateno.core.DatenoCmd(debug=True,
                              apikey=DATENO_API_KEY)

    results=cmd.index_search(query=query,
                             filters=filters,
                             offset=offset,
                             page=page,
                             limit=limit
                             )
    return results