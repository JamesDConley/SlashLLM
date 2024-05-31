curl -X POST \
  http://localhost:8101/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "Who is the US president?", "message_history": []}'
