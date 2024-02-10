from flask import Flask, request, jsonify
import threading
import uuid

# Placeholder for your main module import
# Ensure main module has scrape_yellow_pages and find_contacts functions
import main  

app = Flask(__name__)

ongoing_tasks = {}
task_states = {}
state_lock = threading.Lock()

def update_task_state(task_id, status, result=None):
    with state_lock:
        task_states[task_id] = {"status": status, "result": result}

def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    try:
        result = []
        for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
            result.append(progress_update)
        final_status = "completed" if result else "completed, no result"
        update_task_state(task_id, final_status, result)
    except Exception as e:
        update_task_state(task_id, "failed", str(e))
    finally:
        print(f"Task {task_id} completed. Result: {result}")

def find_contacts_task(website_url, task_id):
    try:
        result = []
        for progress_update in main.find_contacts(website_url):
            result.append(progress_update)
        final_status = "completed" if result else "completed, no result"
        update_task_state(task_id, final_status, result)
    except Exception as e:
        update_task_state(task_id, "failed", str(e))
    finally:
        print(f"Task {task_id} completed. Result: {result}")

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 400

    task_id = str(uuid.uuid4())
    update_task_state(task_id, "processing")
    scraping_thread = threading.Thread(target=scrape_yellow_pages_task, args=(searchterm, location, leadid, task_id))
    scraping_thread.start()

    ongoing_tasks[task_id] = scraping_thread
    
    return jsonify({"task_id": task_id, "message": "Scraping task started."}), 202

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 400

    task_id = str(uuid.uuid4())
    update_task_state(task_id, "processing")
    contacts_thread = threading.Thread(target=find_contacts_task, args=(website_url, task_id))
    contacts_thread.start()

    ongoing_tasks[task_id] = contacts_thread
    
    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 202

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    with state_lock:
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
    elif task_state["status"] == "failed":
        return jsonify({"status": "error", "task": "failed", "message": task_state["result"]}), 500

if __name__ == '__main__':
    app.run(debug=True)
