from functions import sme_pinecone_query_tool

query = {
  "query": "Caffeine"
}

result = sme_pinecone_query_tool(query)
print(result)