from llm_utils import simple_model_call
PLAN_GENERATION_PROMPT = """

Here's the actions available for the model to use
### Start Actions
{tool_descriptions}
### End Actions

Here's the user's request
### Start Request
{user_request}
### End Request

You may use actions multiple times if need be.

Generate a step by step plan to accomplish the given request using the available actions.
"""


def generate_plan(tool_descriptions, user_request):
    plan_prompt = PLAN_GENERATION_PROMPT.format(tool_descriptions=tool_descriptions, user_request=user_request)
    return simple_model_call(plan_prompt)