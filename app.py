import logging
from flask import Flask, request, jsonify
import threading
import uuid
import main  # Ensure this is correctly pointing to your module

# Setup basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Stores task metadata including status
task_metadata = {}
lock = threading.Lock()

def update_task_state(task_id, status, result=None):
    """Safely update the task state."""
    with lock:
        task_metadata[task_id]['status'] = status
        if result is not None:
            task_metadata[task_id]['result'] = result

def run_task(func, *args, task_id):
    """Function to run the task in a new thread, handling updates."""
    try:
        # Assuming the task function returns an iterable for results
        result = list(func(*args))
        status = "completed" if result else "completed, no result"
        update_task_state(task_id, status, result=result)
    except Exception as e:
        logging.exception("Task execution failed.")
        update_task_state(task_id, "failed", str(e))
    finally:
        logging.info(f"Task {task_id} completed.")

@app.route('/start_task', methods=['POST'])
def start_task():
    data = request.json
    task_type = data.get('task_type')
    task_id = str(uuid.uuid4())

    # Initialize task state before starting the thread
    with lock:
        task_metadata[task_id] = {'status': 'processing', 'result': None}

    if task_type == 'scrape_yellow_pages':
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

    thread.start()

    return jsonify({"message": "Task started successfully", "task_id": task_id}), 202

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    with lock:
        if task_id not in task_metadata:
            return jsonify({"error": "Task not found."}), 404
        task_info = task_metadata[task_id]

    return jsonify({"task_id": task_id, "status": task_info["status"], "result": task_info.get("result", "N/A")}), 200

if __name__ == '__main__':
    app.run(debug=True)
