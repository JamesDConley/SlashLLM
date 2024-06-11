import json
import logging

from pydantic import BaseModel, constr

from react.plan_gen import generate_plan
from react.thought_gen import generate_thought
from react.action_selection import select_action
from react.action_input_gen import generate_action_input

from guided_agent.tool import Tool


logger = logging.getLogger(__name__)

class SolveInput(BaseModel):
    answer: constr(max_length=250)

class StreamSolveTool(Tool):
    def run(self, tool_input):
        yield "result", json.loads(tool_input)["answer"]
    
    def name(self):
        return "solve"
    
    def description(self):
        return "Return this actions input to the user as the final result"
    
    def get_input_json_schema(self):
        return SolveInput.model_json_schema()

class StreamingGuidedAgent:
    def __init__(self, tools):
        tools.append(StreamSolveTool())
        self.tools = tools
        # TODO : More clearly draw out what context should be
        self.tool_names = [tool.name() for tool in tools]
        self.tools_dict = {tool.name() : tool for tool in tools}
        self.tool_descriptions = "\n".join([f"{tool.name()} : {tool.description()}" for tool in tools])
        
    
    def run(self, user_request, max_turns=10):
        
        context = generate_plan(self.tool_descriptions, user_request)
        yield "display", f"Generated plan\n```txt\n{context}\n```\n"
        context += f"OBSERVATION : {user_request}\n"
        for i in range(max_turns):
            logger.info(f"Generating thought...")
            thought = generate_thought(context, self.tool_descriptions)
            yield "display", f"Generated thought : \n```thought\n{thought}\n```\n"
            logger.info(f"Generated thought : {thought}")
            context += f"THOUGHT : {thought}\n"
            tool_name = select_action(context, thought, self.tool_names, self.tool_descriptions)
            tool = self.tools_dict[tool_name]
            tool_input = generate_action_input(tool, context)
            logger.info(f"Calling tool {tool_name} : {tool_input}")
            yield "display", f"Calling tool {tool_name} : \n```json\n{tool_input}\n```\n"
            context += f"ACTION : {tool_name} : {json.dumps(tool_input, indent=4)}\n"
            output = tool.run(tool_input)
            result = ""
            for output_type, val in output:
                if output_type == "display":
                    yield output_type, val
                elif output_type == "result":
                    result = val
                    del output

            logger.info(f"Got Output : {result}")
            context += f"OBSERVATION : {result}\n"
            
            if tool_name == "solve":
                yield "result", result
                return
        
        answer_prompt = RESPOND_TO_USER_PROMPT.format(context=context, user_request=user_request)
        reponse = simple_model_call(answer_prompt)
        yield "result", reponse