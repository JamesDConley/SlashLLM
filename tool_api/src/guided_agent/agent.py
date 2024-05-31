import json
from pydantic import BaseModel, constr

from guided_agent.plan_gen import generate_plan
from guided_agent.thought_gen import generate_thought
from guided_agent.action_selection import select_action
from guided_agent.action_input_gen import generate_action_input

from guided_agent.tool import Tool

class SolveInput(BaseModel):
    answer: constr(max_length=250)

class SolveTool(Tool):
    def run(self, tool_input):
        return json.loads(tool_input)["answer"]
    
    def name(self):
        return "solve"
    
    def description(self):
        return "Return this actions input to the user as the final result"
    
    def get_input_json_schema(self):
        return SolveInput.model_json_schema()

class GuidedAgent:
    def __init__(self, tools):
        tools.append(SolveTool())
        self.tools = tools
        # TODO : More clearly draw out what context should be
        self.tool_names = [tool.name() for tool in tools]
        self.tools_dict = {tool.name() : tool for tool in tools}
        self.tool_descriptions = "\n".join([f"{tool.name()} : {tool.description()}" for tool in tools])
        
    
    def run(self, user_request, max_turns=10):
        
        context = generate_plan(self.tool_descriptions, user_request)
        
        context += f"OBSERVATION : {user_request}\n"
        for i in range(max_turns):
            print(f"Generating thought...")
            thought = generate_thought(context, self.tool_descriptions)
            print(f"Generated thought : {thought}")
            context += f"THOUGHT : {thought}\n"
            tool_name = select_action(context, thought, self.tool_names, self.tool_descriptions)
            tool = self.tools_dict[tool_name]
            tool_input = generate_action_input(tool, context)
            print(f"Calling tool {tool_name} : {tool_input}")
            context += f"ACTION : {tool_name} : {json.dumps(tool_input, indent=4)}\n"
            output = tool.run(tool_input)
            print(f"Got Output : {output}")
            context += f"OBSERVATION : {output}\n"
            
            if tool_name == "solve":
                return output
        answer_prompt = RESPOND_TO_USER_PROMPT.format(context=context, user_request=user_request)
        reponse = simple_model_call(answer_prompt)
        return reponse