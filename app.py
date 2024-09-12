import os
import urllib.parse
from flask import Flask, request, jsonify, render_template
import pymongo
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection
# mongo_uri = "mongodb://localhost:27017/"
username = urllib.parse.quote_plus(os.getenv('MONGO_USERNAME'))
password = urllib.parse.quote_plus(os.getenv('MONGO_PASSWORD'))
cluster = urllib.parse.quote_plus(os.getenv('MONGO_CLUSTER'))
mongo_uri = f"mongodb+srv://{username}:{password}@{cluster}.mongodb.net/webhook_db?retryWrites=true&w=majority"
client = pymongo.MongoClient(mongo_uri)

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

        # Handle GitHub Push event
        if 'commits' in data:  
            action_type = 'PUSH'
            author = data['pusher']['name']
            to_branch = data['ref'].split('/')[-1]
            request_id = data['commits'][0]['id']
            from_branch = None

        # Handle GitHub Pull Request event
        elif 'pull_request' in data:
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            request_id = data['pull_request']['id']
            
            # Process based on action type
            if data['action'] == 'opened':
                action_type = 'PULL_REQUEST_OPENED'
            elif data['action'] == 'review_requested':
                action_type = 'PULL_REQUEST_REVIEW_REQUESTED'
            elif data['action'] == 'closed':
                if data['pull_request']['merged']:  # Handle merged pull request
                    action_type = 'MERGE'
                else:
                    action_type = 'PULL_REQUEST_CLOSED'

        # Create event document for MongoDB
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
    app.run(host='0.0.0.0', port=8080, debug=True)
