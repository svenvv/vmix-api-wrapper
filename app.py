from flask import Flask, request, jsonify
import requests
import threading
import tkinter as tk
from tkinter import messagebox

app = Flask(__name__)
TARGET_URL = ''  # This will be set from the GUI

@app.route('/favicon.ico')
def favicon():
    return jsonify({"error": "Not Found"}), 404

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(path):
    global TARGET_URL

    # Get the method of the incoming request
    method = request.method

    # Forward the incoming request's query parameters, headers, and data
    params = request.args
    headers = {key: value for key, value in request.headers if key != 'Host'}
    data = request.get_json() if request.is_json else request.form

    # Construct the full URL to be proxied
    url = f"{TARGET_URL}/{path}"

    # Make the proxied request
    response = requests.request(method, url, params=params, headers=headers, json=data)

    # Process the response
    if response.status_code == 200:
        data = response.json()
        if not isinstance(data, list):
            data = [data]
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch data from {TARGET_URL}"}), response.status_code

def run_flask():
    app.run(host='0.0.0.0', port=5000)

def create_gui():
    def on_submit():
        global TARGET_URL
        url = url_entry.get()
        if url:
            TARGET_URL = url
            status_label.config(text=f"Target URL: {TARGET_URL}\
                \nListening on http://127.0.0.1:5000")
        else:
            messagebox.showerror("Input Error", "Please enter a valid URL")

    root = tk.Tk()
    root.title("json listifier")

    tk.Label(root, text="Enter Target URL:").pack(pady=10)
    
    url_entry = tk.Entry(root, width=50)
    url_entry.pack(pady=10)

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack(pady=10)

    status_label = tk.Label(root, text="Target URL: Not Set")
    status_label.pack(pady=10)

    threading.Thread(target=run_flask, daemon=True).start()

    root.mainloop()

if __name__ == '__main__':
    create_gui()
