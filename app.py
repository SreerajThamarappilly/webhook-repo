from flask import Flask, request, jsonify, render_template
import pymongo
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['webhook_db']
collection = db['github_events']

# Route to serve the HTML UI
@app.route('/')
def index():
    return render_template('index.html')  # Render the index.html file

# Webhook endpoint to receive GitHub events
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json

        # Process GitHub event types
        if 'commits' in data:  # Handling Push Event
            action_type = 'PUSH'
            author = data['pusher']['name']
            to_branch = data['ref'].split('/')[-1]
            request_id = data['commits'][0]['id']
            from_branch = None
        elif 'pull_request' in data:  # Handling Pull Request Event
            action_type = 'PULL_REQUEST'
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            request_id = data['pull_request']['id']
        elif 'merged' in data['pull_request'] and data['pull_request']['merged']:  # Handling Merge Event
            action_type = 'MERGE'
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            request_id = data['pull_request']['id']

        # Create event document
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        event = {
            "request_id": request_id,
            "author": author,
            "action": action_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        # Insert event into MongoDB
        collection.insert_one(event)

        return jsonify({"status": "Event received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to return the latest GitHub events
@app.route('/events', methods=['GET'])
def get_events():
    try:
        # Get the latest 10 events from MongoDB, sorted by timestamp
        events = collection.find().sort("timestamp", -1).limit(10)
        event_list = []
        for event in events:
            event_list.append({
                "author": event['author'],
                "action": event['action'],
                "from_branch": event['from_branch'],
                "to_branch": event['to_branch'],
                "timestamp": event['timestamp']
            })

        return jsonify(event_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
