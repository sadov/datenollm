import os
import logging
import dateno.core

DATENO_API_KEY = os.getenv('DATENO_API_KEY')

# Dateno search machinery
def dateno_index_search(query, filters, offset=0, page=1, limit=500):
    "Call Dateno API for search in index"
    logging.debug(f'index_search {query=} {filters=}')

    cmd=dateno.core.DatenoCmd(debug=True,
                              apikey=DATENO_API_KEY)

    results=cmd.index_search(query=query,
                             filters=filters,
                             offset=offset,
                             page=page,
                             limit=limit
                             )
    return results

def llm_index_search(llm_response):
    queries = []
    for query in llm_response['queries']:
      if query['filters']:
        qfilters = [f'{f["name"]}={f["value"]}' for f in query['filters']]
      else:
        qfilters = []
      logging.debug(f'{query=} {qfilters=}')
      results = dateno_index_search(query['query'], qfilters)#, offset, page, limit)
      queries.append({'query': query,
                      'results': results})

    return queries