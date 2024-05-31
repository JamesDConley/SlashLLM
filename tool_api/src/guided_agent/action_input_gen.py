from llm_utils import simple_model_call
from pydantic import BaseModel, constr

ACTION_INPUT_PROMPT = """Generate an input for the selected action.

Here's the action description
### Start Action
{action_name} : {action_description}
### End Action

Here's the current context
### Start Context
{context}
### End Context


Here's the required output schema
### Start Output Schema
{output_schema}
### End Output Schema

Respond with a string that is an input for the action.
"""

def generate_action_input(tool, context):
    prompt = ACTION_INPUT_PROMPT.format(
        action_name = tool.name(), 
        action_description=tool.description(), 
        context=context, 
        output_schema=tool.get_input_json_schema()
    )
    
    tool_input = simple_model_call(prompt, extra_body={"guided_json" : tool.get_input_json_schema()})
    return tool_input
