import json

from ModelGenerationApi import ModelGenerationApi
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

OPTION_USER_STORIES = 'user-stories'
OPTION_ONTOLOGY = 'ontology'
OPTION_PROLOG = 'prolog'


@app.route('/')
def index():
    return 'Hello =]. Use the endpoint: user-stories please.'


@app.route('/user-stories', methods=['POST'])
def api_user_stories():
    if not request.files or not request.files['stories']:
        return Response(json.dumps({'error': 'Upload a user story.'}), status=409, mimetype='application/json')

    stream = request.files['stories'].stream
    if request.files['stories'].content_type == 'text/csv':
        messages = stream.read().decode("UTF8").split('\r\n')
    else:
        messages = stream.read().decode('UTF-8').split('\n')

    weights = [1, 1, 1, 0.7, 0.5, 0.66]

    conceptual_model = ModelGenerationApi('system-name', 1, 1, weights, messages)
    result = conceptual_model.gen_concept_model()

    option = None
    if request.args.get('option'):
        option = request.args.get('option')

    if option is None or option == OPTION_USER_STORIES:
        user_stories_json = [str(us.toJSON()) for us in result['stories']]
        return "\n".join(user_stories_json)
    elif option == OPTION_ONTOLOGY:
        return result['ontology']
    elif option == OPTION_PROLOG:
        return result['prolog']
    else:
        return Response(json.dumps({'error': 'Invalid option.'}), status=409, mimetype='application/json')


if __name__ == '__main__':
    app.run()
