RESPOND_TO_USER_PROMPT = """
### Begin Context
{context}
### End Context

### Begin User Request
{user_request}
### End User Request

Based on the above context, create a concise response to the users request.
"""


def gen_user_response(context, user_request, ):
    answer_prompt = RESPOND_TO_USER_PROMPT.format(context=context, user_request=user_request)
    return simple_model_call(answer_prompt)