import logging
from waitress import serve
from flask import Flask, request, Response
from guided_agent.stream_agent import StreamingGuidedAgent
from stream_tools.duck_duck_go_stream_tool import DuckDuckGoSearch

logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/search', methods=['POST'])
def run_request():
    logger.info("Got search request")
    ddg_tool = DuckDuckGoSearch()
    agent = StreamingGuidedAgent([ddg_tool])
    user_request = request.get_json()['query']
    
    def generate():
        for i, item in enumerate(agent.run(user_request)):
            logger.info(f"Received Yield : {i}")
            if item[0] == 'display':
                yield f"Display: {item[1]}\n"
            elif item[0] == 'result':
                yield f"Result: {item[1]}\n"
        
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    logging.basicConfig(filename="/logs/tool_api.log", level=logging.INFO, format='%(asctime)s %(message)s')
    serve(app, host="0.0.0.0", port=8101)