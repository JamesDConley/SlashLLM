# SlashLLM

## About
Slash LLM is chat interface that makes it easy to add slash commands of your own.

The UI provides barebones features users expect from chat and makes it easy to add your own.


## How to Add a Slash Command

### Creating your api endpoint
Create an API endpoint that handles the processing for your command.
This endpoint will receive a POST containing JSON with two entries
- query : The users message that triggered the slash command
- message_history : The full conversation that the query was made in

It must return a json containing a `result` entry with a string output.
This output will be directly displayed in the app- and is also included in the context of the conversation.
Currently streaming tool outputs isn't supported (they are returned all at once), but it's a priority item.

You can see an example of an API endpoint for a tool in the file `tool_api/src/tool_api.py`.

### Linking the endpoint to backend
There is a `TOOL_MAPPINGS` variable in `api/src/config.py`.
Add an entry to this dictionary for your API.
Here is an example of the format with one search tool.
```
TOOL_MAPPINGS = {
    "search": {"url": "http://tool-api:8101/search"},
}
```


