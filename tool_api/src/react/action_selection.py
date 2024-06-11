from llm_utils import simple_model_call

ACTION_PROMPT = """Select an action based on the current context and thought.

Here's the current context
### Start Context
{context}
### End Context

Here's the thought
### Start Thought
{thought}
### End Thought

Here's the actions available to select
### Start Actions
{actions}
### End Actions

Respond with the name of the action to take.
"""


def select_action(context, thought, tool_names, tool_descriptions):
    prompt = ACTION_PROMPT.format(context=context, thought=thought, actions=tool_descriptions)
    selected_action = simple_model_call(prompt, extra_body={"guided_choice" : tool_names})
    return selected_action