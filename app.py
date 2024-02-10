import logging
from flask import Flask, request, jsonify
import threading
import uuid
# Placeholder import for your actual main module
import main

# Setup basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Global dictionaries for managing tasks
ongoing_tasks = {}
task_states = {}
lock = threading.Lock()

def update_task_state(task_id, status, result=None):
    """Update the state of a task in a thread-safe manner."""
    with lock:
        task_states[task_id] = {"status": status, "result": result}

def run_task(func, *args, **kwargs):
    """Generic task runner that executes a given function and handles state updates."""
    task_id = kwargs.pop('task_id')
    try:
        # Execute the task function and collect results
        result = list(func(*args, **kwargs))
        status = "completed" if result else "completed, no result"
        update_task_state(task_id, status, result)
    except Exception as e:
        logging.exception("Task execution failed.")
        update_task_state(task_id, "failed", str(e))
    finally:
        logging.info(f"Task {task_id} completed.")

@app.route('/start_task', methods=['POST'])
def start_task():
    """Endpoint to start a new task based on the type specified in the request."""
    data = request.json
    task_type = data.get('task_type')
    task_id = str(uuid.uuid4())

    if task_type == 'scrape_yellow_pages':
        # Example args extraction, adjust according to your task function requirements
        searchterm = data.get('searchterm')
        location = data.get('location')
        leadid = data.get('leadid')
        if not all([searchterm, location, leadid]):
            return jsonify({"error": "Missing parameters for scraping task"}), 400
        thread = threading.Thread(target=run_task, args=(main.scrape_yellow_pages, searchterm, location, leadid), kwargs={"task_id": task_id})
    elif task_type == 'find_contacts':
        website_url = data.get('website_url')
        if not website_url:
            return jsonify({"error": "Missing website URL for contact finding task"}), 400
        thread = threading.Thread(target=run_task, args=(main.find_contacts, website_url), kwargs={"task_id": task_id})
    else:
        return jsonify({"error": "Invalid task type specified"}), 400

    update_task_state(task_id, "processing")
    thread.start()
    ongoing_tasks[task_id] = thread

    return jsonify({"message": "Task started successfully", "task_id": task_id}), 202

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    """Endpoint to check the status of a task."""
    with lock:
        if task_id not in task_states:
            return jsonify({"error": "Task not found."}), 404
        state = task_states[task_id]

    return jsonify({"task_id": task_id, "status": state["status"], "result": state.get("result", "N/A")}), 200

if __name__ == '__main__':
    app.run(debug=True)
