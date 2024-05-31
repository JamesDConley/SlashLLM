import json
from llm_utils import simple_model_call
from pydantic import BaseModel, constr

# Constants
MAX_CHARS = 250

THOUGHT_PROMPT = """Generate a thought based on the current context.
The thought should be no more than a few sentences and should focus on the task to be done.

Here's the current context
### Start Context
{context}
### End Context

You have access to the following tools only
### Start Tools
{tool_descriptions}
### End Tools

Respond with a json object containing a single "thought" entry.
Please keep your response within {max_chars} characters.
"""

# Define the required output format
class ThoughtOutput(BaseModel):
    thought: constr(max_length=MAX_CHARS)
THOUGHT_FORMAT = ThoughtOutput.model_json_schema()


def generate_thought(context, tool_descriptions):
    # Fill out the prompt template
    prompt = THOUGHT_PROMPT.format(context=context, tool_descriptions=tool_descriptions, max_chars=MAX_CHARS)
    # Generate the thought
    thought = simple_model_call(prompt, extra_body={"guided_json" : THOUGHT_FORMAT})
    # Return just the thought string itself
    return json.loads(thought)["thought"]