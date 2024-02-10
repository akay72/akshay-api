from flask import Flask, request, jsonify
import threading
import main  # Import your scraping script
import uuid

app = Flask(__name__)

# Dictionary to store ongoing tasks and their results
ongoing_tasks = {}
task_results = {}

def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    result = []
    for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
        result.append(progress_update)
    task_results[task_id] = result
    print(f"Scraping task {task_id} completed.")
    print(f"Result: {result}")

def find_contacts_task(website_url, task_id):
    result = []
    for progress_update in main.find_contacts(website_url):
        result.append(progress_update)
    task_results[task_id] = result
    print(f"Contact finding task for {task_id} completed.")
    print(f"Result: {result}")

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 200

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Start the scraping task in a separate thread
    scraping_thread = threading.Thread(target=scrape_yellow_pages_task, args=(searchterm, location, leadid, task_id))
    scraping_thread.start()

    # Store the task ID and associated thread in a dictionary
    ongoing_tasks[task_id] = scraping_thread
    print(f"Started scraping task with ID: {task_id}")

    # Return the task ID as a response
    return jsonify({"task_id": task_id, "message": "Scraping task started."}), 200

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 200

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Start the contact finding task in a separate thread
    contacts_thread = threading.Thread(target=find_contacts_task, args=(website_url, task_id))
    contacts_thread.start()

    # Store the task ID and associated thread in a dictionary
    ongoing_tasks[task_id] = contacts_thread
    print(f"Started contact finding task with ID: {task_id}")

    # Return the task ID as a response
    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 200

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    if task_id not in task_results:
        return jsonify({"error": "Task not found."}), 200

    task_result = task_results[task_id]
    if isinstance(task_result, list):
        return jsonify({"status": "Task completed.", "result": task_result}), 200
    else:
        return jsonify({"status": "Task in progress..."}), 200

if __name__ == '__main__':
    app.run(debug=True)
