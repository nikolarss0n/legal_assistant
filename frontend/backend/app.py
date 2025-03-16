from flask import Flask, request, jsonify
from flask_cors import CORS
from legal_query import answer_legal_query

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

@app.route('/api/query', methods=['POST'])
def query():
    """API endpoint for processing labor law queries."""
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    result = answer_legal_query(data['query'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)