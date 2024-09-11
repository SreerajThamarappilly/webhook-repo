import os
import urllib.parse
from flask import Flask, request, jsonify, render_template
import pymongo
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection
# client = pymongo.MongoClient("mongodb://localhost:27017/")
username = urllib.parse.quote_plus(os.getenv('MONGO_USERNAME'))
password = urllib.parse.quote_plus(os.getenv('MONGO_PASSWORD'))
mongo_uri = f"mongodb+srv://{username}:{password}@cluster.mongodb.net/webhook_db?retryWrites=true&w=majority"
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

@app.route('/test_db')
def test_db():
    try:
        # Test MongoDB connection
        client.admin.command('ping')
        return jsonify({"status": "MongoDB connected!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test_nginx')
def test_nginx():
    return jsonify({"status": "Nginx connected to Flask!"}), 200

@app.route('/test_insert')
def test_insert():
    try:
        # Insert a test event to MongoDB
        test_event = {
            "request_id": "test_id",
            "author": "Test Author",
            "action": "TEST",
            "from_branch": "test_branch",
            "to_branch": "main",
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        collection.insert_one(test_event)
        return jsonify({"status": "Test event inserted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test_webhook', methods=['POST'])
def test_webhook():
    try:
        # Example payload to simulate a webhook event
        data = {
            "commits": [{
                "id": "test_commit_id",
                "message": "Test commit",
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            }],
            "pusher": {"name": "test_pusher"},
            "ref": "refs/heads/test_branch"
        }

        # You can copy-paste the webhook processing logic here for testing
        action_type = 'PUSH'
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        request_id = data['commits'][0]['id']
        from_branch = None

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

        # Insert into MongoDB
        collection.insert_one(event)

        return jsonify({"status": "Webhook processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
