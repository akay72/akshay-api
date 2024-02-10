from flask import Flask, request, jsonify
import threading
import main  # Make sure this script includes scrape_yellow_pages and find_contacts functions
import uuid

app = Flask(__name__)

# Updated dictionaries for task management and states
ongoing_tasks = {}
task_states = {}

def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    try:
        # Initialize task state
        task_states[task_id] = {"status": "processing", "result": None}
        result = []
        for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
            result.append(progress_update)
        if result:
            task_states[task_id] = {"status": "completed", "result": result}
        else:
            task_states[task_id] = {"status": "completed", "result": "no result"}
    finally:
        print(f"Scraping task {task_id} completed. Result: {result}")

def find_contacts_task(website_url, task_id):
    try:
        # Initialize task state
        task_states[task_id] = {"status": "processing", "result": None}
        result = []
        for progress_update in main.find_contacts(website_url):
            result.append(progress_update)
        if result:
            task_states[task_id] = {"status": "completed", "result": result}
        else:
            task_states[task_id] = {"status": "completed", "result": "no result"}
    finally:
        print(f"Contact finding task for {task_id} completed. Result: {result}")

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 400

    task_id = str(uuid.uuid4())
    scraping_thread = threading.Thread(target=scrape_yellow_pages_task, args=(searchterm, location, leadid, task_id))
    scraping_thread.start()

    ongoing_tasks[task_id] = scraping_thread
    task_states[task_id] = {"status": "processing", "result": None}
    
    return jsonify({"task_id": task_id, "message": "Scraping task started."}), 202

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 400

    task_id = str(uuid.uuid4())
    contacts_thread = threading.Thread(target=find_contacts_task, args=(website_url, task_id))
    contacts_thread.start()

    ongoing_tasks[task_id] = contacts_thread
    task_states[task_id] = {"status": "processing", "result": None}
    
    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 202

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    if task_id not in task_states:
        return jsonify({"status": "error", "message": "Task not found."}), 404

    task_state = task_states[task_id]
    if task_state["status"] == "processing":
        return jsonify({"status": "success", "task": "processing"}), 200
    elif task_state["status"] == "completed":
        if task_state["result"] == "no result":
            return jsonify({"status": "success", "task": "completed", "message": "No result"}), 200
        else:
            return jsonify({"status": "success", "task": "completed", "result": task_state["result"]}), 200

if __name__ == '__main__':
    app.run(debug=True)
