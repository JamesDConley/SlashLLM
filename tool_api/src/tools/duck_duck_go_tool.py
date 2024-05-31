import json

from pydantic import BaseModel, constr
import json
import multiprocessing
from duckduckgo_search import DDGS

from guided_agent.tool import Tool
from llm_utils import simple_model_call

IS_RELEVANT_PROMPT = """Determine if the candidate result contains information that answers the users request partially, fully, or not at all.

Here's the user's request
### Start Request
{user_request}
### End Request

Here's the candidate result
### Start Result
{result}
### End Result

Respond with one of "PARTIAL", "FULL", or "IRRELEVANT"
"""

def filter_result(item, user_query):
    result_str = json.dumps(item, indent=4)
    prompt = IS_RELEVANT_PROMPT.format(user_request=user_query, result=result_str)
    # TODO : I reworked this to only include full and irrelevant because I want binary and am too lazy to mess with the others
    result = simple_model_call(prompt, extra_body={"guided_choice" : ["FULL", "IRRELEVANT"]})
    return result, item

def mp_filter_results(user_query, results):
    with multiprocessing.Pool() as pool:
        results_with_labels = pool.starmap(filter_result, [(item, user_query) for item in results])
    
    relevant_results = []
    partial_results = []
    irrelevant_results = []
    
    for label, item in results_with_labels:
        if label == "PARTIAL":
            partial_results.append(item)
        elif label == "FULL":
            relevant_results.append(item)
        else:
            irrelevant_results.append(item)
    
    if len(relevant_results) > 0:
        return relevant_results
    elif len(partial_results) > 0:
        return partial_results
    else:
        return []

class SearchEngineInput(BaseModel):
    search_engine_input: constr(max_length=250)

class DuckDuckGoSearch(Tool):
    def run(self, tool_input, max_results=10):
        parsed_input = json.loads(tool_input)["search_engine_input"]
        results = DDGS().text(parsed_input, max_results=max_results)
        relevant_results = mp_filter_results(tool_input, results)
        return f"Results : {json.dumps(relevant_results, indent=4)}"
        
    def name(self):
        return "ddg_search"
    
    def description(self):
        return "Perform a web search using duck duck go."
    
    def get_input_json_schema(self):
        return SearchEngineInput.model_json_schema()