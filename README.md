# webhook-repo

This Flask application is designed to receive and process GitHub webhook events ("Push", "Pull Request", and "Merge") and store them in a MongoDB database. The project handles webhook events, processes them, and provides an API to view the stored events in real time.

## Features

- **Receive GitHub Events**: Automatically listens for GitHub events and processes "Push", "Pull Request", and "Merge" actions.
- **Store Data in MongoDB**: All webhook event data is stored in a MongoDB collection (`github_events`).
- **Serve Web UI**: Displays the latest GitHub events via a simple UI.
- **Polling**: The UI polls MongoDB every 15 seconds to display the most recent changes.

## Tech Stack

- **Backend**: Python Flask
- **Database**: MongoDB Atlas (or local MongoDB)
- **Frontend**: HTML, JavaScript (to poll for new events)
- **Web Server**: Gunicorn
- **Hosting**: AWS Elastic Beanstalk

## Setup Instructions

### 1. Prerequisites

- Python 3.8+ (I used Python 3.11.3)
- MongoDB Atlas or local MongoDB instance
- AWS Elastic Beanstalk (for production deployment)

### 2. Clone the Repository

```bash
git clone https://github.com/SreerajThamarappilly/webhook-repo.git
cd webhook-repo
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. MongoDB Setup

- **If using a local MongoDB instance**: Ensure MongoDB is running locally at mongodb://localhost:27017/.

- **If using MongoDB Atlas**: Create a database cluster in MongoDB Atlas. Whitelist the server's IP (or use 0.0.0.0/0 for open access). Replace the MongoDB connection string in the code: 

```bash
client = pymongo.MongoClient("mongodb+srv://<username>:<password>@<cluster>.mongodb.net/webhook_db?retryWrites=true&w=majority")
```

### 5. Run the Application Locally

```bash
flask run
```

The app will run locally on http://localhost:5000/. To test the /test_db route, you can open http://localhost:5000/test_db to ensure the database connection works.

### 6. Deploy to AWS Elastic Beanstalk

- Create an Elastic Beanstalk application from the AWS console.
- Upload the contents of the webhook-repo folder in a .zip format.
- Ensure the environment variables (MongoDB credentials) are set properly in the Beanstalk configuration.
- You can now access the live application using the Elastic Beanstalk URL.

### 7. Webhook Setup in [action-repo](https://github.com/SreerajThamarappilly/action-repo.git) GitHub repository 

- In action-repo GitHub repository, go to Settings > Webhooks > Add Webhook.
- Add the payload URL of Elastic Beanstalk (e.g. http://your-app-env.elasticbeanstalk.com/webhook).
- Choose application/json as the content type and select "Send me everything" as the event trigger.

### 8. Routes

- **/webhook**: Receives GitHub webhook events.
- **/events**: Retrieves the latest events from MongoDB.
- **/**: Displays the UI for tracking events.

### 9. License

This project is licensed under the MIT License.
