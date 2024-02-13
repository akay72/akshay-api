from flask import Flask, request, jsonify
import threading
import uuid
import main  # Ensure your scraping script is correctly referenced
from email_content import generate_outreach_email
app = Flask(__name__)

# Dictionaries to store ongoing tasks and their results
ongoing_tasks = {}
task_results = {}

@app.route('/generate_email', methods=['POST'])
def generate_email():
    data = request.json
    lead_name = data.get('lead_name')
    lead_website = data.get('lead_website')

    if not lead_name or not lead_website:
        return jsonify({"error": "Missing lead_name or lead_website parameters"}), 400

    try:
        # Generate the email content directly without using a separate thread
        email_content = generate_outreach_email(lead_name, lead_website)
        return jsonify({"email_content": email_content, "message": "Email generation task completed."}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during email generation: {str(e)}"}), 500



def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    try:
        result = []
        for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
            if progress_update is not None:
                result.append(progress_update)
        if not result:  # No data was found
            task_results[task_id] = "No data found."
        else:
            task_results[task_id] = result
    except Exception as e:
        task_results[task_id] = f"Error: {str(e)}"
    print(f"Scraping task {task_id} completed. Result: {task_results[task_id]}")

def find_contacts_task(website_url, task_id):
    try:
        result = []
        for progress_update in main.find_contacts(website_url):
            if progress_update is not None:
                result.append(progress_update)
        if not result:  # No data was found
            task_results[task_id] = "No data found."
        else:
            task_results[task_id] = result
    except Exception as e:
        task_results[task_id] = f"Error: {str(e)}"
    print(f"Contact finding task for {task_id} completed. Result: {task_results[task_id]}")

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
    print(f"Started scraping task with ID: {task_id}")

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
    print(f"Started contact finding task with ID: {task_id}")

    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 202

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    # Check if task ID is not found in both task_results and ongoing_tasks
    if task_id not in task_results and task_id not in ongoing_tasks:
        return jsonify({"status": "Task not found."}), 404
    # Check if task is still in ongoing_tasks but not yet in task_results
    elif task_id in ongoing_tasks and task_id not in task_results:
        return jsonify({"status": "Task still in progress..."}), 202

    # Ensure task_result is available before accessing it
    task_result = task_results.get(task_id, None)
    if task_result is None:
        # This block should theoretically never be reached due to the above checks
        # But it's here as a safeguard
        return jsonify({"status": "Task still in progress or not found."}), 202
    elif isinstance(task_result, list):
        return jsonify({"status": "Task completed successfully.", "result": task_result}), 200
    elif "No data found" in task_result:
        return jsonify({"status": "Task completed with no data."}), 404
    elif "Error" in task_result:
        return jsonify({"status": "Task completed with error.", "error": task_result}), 500
    else:
        # A catch-all return statement as a last resort, should not be reached
        return jsonify({"status": "Unknown task status.", "result": task_result}), 500



if __name__ == '__main__':
    app.run(debug=True)
