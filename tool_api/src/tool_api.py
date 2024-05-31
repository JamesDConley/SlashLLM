from flask import Flask, request, jsonify
from guided_agent.agent import GuidedAgent
from tools.duck_duck_go_tool import DuckDuckGoSearch

app = Flask(__name__)


@app.route('/search', methods=['POST'])
def run_request():
    ddg_tool = DuckDuckGoSearch()
    agent = GuidedAgent([ddg_tool])
    user_request = request.get_json()['query']
    # This isn't used but leaving it here since this is also an example of how to set this up
    msg_history = request.get_json()['message_history']
    output = agent.run(user_request)
    print(f"Generated output : {output}")
    return jsonify({'result': output})

if __name__ == '__main__':
    app.run("0.0.0.0", port=8101)