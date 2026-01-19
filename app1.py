"""
Digital Library PC Monitoring System
-------------------------------------
Homepage -> Two sections:
  - Login Page for Library
  - View Library Status
Now: Students only enter Roll No; Name is fetched automatically.
"""

from flask import Flask, jsonify, request, render_template_string
import sqlite3
from threading import Lock

app = Flask(__name__)
TOTAL_PCS = 25
active_users = []
lock = Lock()

# ---------- DATABASE ----------
def get_student_name(roll_no):
    """Return student name from roll number, or None if not found."""
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE roll_no = ?", (roll_no,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# ---------- API ----------
@app.route('/api/status', methods=['GET'])
def api_status():
    with lock:
        return jsonify({
            'total_pcs': TOTAL_PCS,
            'pcs_in_use': len(active_users),
            'pcs_available': TOTAL_PCS - len(active_users)
        })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    roll_no = str(data.get('roll_no', '')).strip()

    if not roll_no:
        return jsonify({'success': False, 'message': 'Roll Number is required.'}), 400

    name = get_student_name(roll_no)
    if not name:
        return jsonify({'success': False, 'message': 'Roll Number not found. Access denied.'}), 403

    with lock:
        if roll_no in active_users:
            return jsonify({'success': False, 'message': f'{name} is already logged in.'}), 400
        if len(active_users) >= TOTAL_PCS:
            return jsonify({'success': False, 'message': 'No PCs available.'}), 400

        active_users.append(roll_no)
        return jsonify({'success': True, 'message': f'{name} logged in successfully.'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    data = request.get_json() or {}
    roll_no = str(data.get('roll_no', '')).strip()

    if not roll_no:
        return jsonify({'success': False, 'message': 'Roll Number is required.'}), 400

    name = get_student_name(roll_no)
    if not name:
        return jsonify({'success': False, 'message': 'Roll Number not found.'}), 403

    with lock:
        if roll_no in active_users:
            active_users.remove(roll_no)
            return jsonify({'success': True, 'message': f'{name} logged out successfully.'})
        else:
            return jsonify({'success': False, 'message': f'{name} is not logged in.'}), 400

# ---------- FRONTEND ----------
HOME_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Digital Library PC System</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      background: linear-gradient(to right, #d9e8ff, #f0f7ff);
      margin: 0;
      padding: 50px;
    }
    h1 { color: #0d4c92; margin-bottom: 40px; }
    .container {
      display: flex;
      justify-content: center;
      gap: 40px;
      flex-wrap: wrap;
    }
    .card {
      background: white;
      width: 300px;
      height: 160px;
      box-shadow: 0 6px 15px rgba(0,0,0,0.1);
      border-radius: 12px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      transition: transform 0.3s, box-shadow 0.3s;
    }
    .card:hover {
      transform: translateY(-8px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .card h2 {
      color: #1f6feb;
    }
  </style>
</head>
<body>
  <h1>📚 Digital Library PC Monitoring System</h1>
  <div class="container">
    <div class="card" onclick="window.location='/login'">
      <h2>Login Page for Library</h2>
    </div>
    <div class="card" onclick="window.location='/status'">
      <h2>View Library Status</h2>
    </div>
  </div>
</body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Library Login Page</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f3f6fa; margin: 0; padding: 0; text-align: center; }
    h1 { color: #1e73be; margin: 30px; }
    .card { background: white; display: inline-block; padding: 25px; border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: left; width: 380px; }
    input { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 6px; }
    button { background: #1e73be; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; }
    button:hover { background: #155d93; }
    .msg { margin-top: 10px; font-weight: bold; }
    a { text-decoration: none; color: #1e73be; display: inline-block; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>🎓 Library Login / Logout</h1>
  <div class="card">
    <label>Enter Roll Number:</label><br>
    <input type="text" id="roll_no" placeholder="e.g., 1"><br>
    <button id="login_btn">Login</button>
    <button id="logout_btn" style="background:#b91c1c; margin-left:6px;">Logout</button>
    <div class="msg" id="msg"></div>
    <a href="/">⬅ Back to Home</a>
  </div>

  <script>
    async function postJSON(url, body) {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      return res.json().catch(() => ({ success: false, message: 'Error' }));
    }

    document.getElementById('login_btn').addEventListener('click', async () => {
      const roll_no = document.getElementById('roll_no').value.trim();
      const msg = document.getElementById('msg');
      msg.innerText = '';
      if (!roll_no) { msg.innerText = 'Please enter Roll Number.'; return; }
      const res = await postJSON('/api/login', { roll_no });
      msg.innerText = res.message;
    });

    document.getElementById('logout_btn').addEventListener('click', async () => {
      const roll_no = document.getElementById('roll_no').value.trim();
      const msg = document.getElementById('msg');
      msg.innerText = '';
      if (!roll_no) { msg.innerText = 'Enter Roll Number to logout.'; return; }
      const res = await postJSON('/api/logout', { roll_no });
      msg.innerText = res.message;
    });
  </script>
</body>
</html>
'''

STATUS_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Library PC Status</title>
  <style>
    body { font-family: Arial, sans-serif; background: #eef5ff; text-align: center; margin: 0; padding: 0; }
    h1 { color: #0d4c92; margin: 30px; }
    .card { background: white; display: inline-block; padding: 25px; border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: left; width: 400px; }
    .status-value { font-size: 22px; font-weight: bold; color: #333; }
    a { text-decoration: none; color: #1e73be; display: inline-block; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>💻 Library PC Availability</h1>
  <div class="card">
    <p><strong>Total PCs:</strong> <span id="total_pcs" class="status-value">-</span></p>
    <p><strong>PCs in Use:</strong> <span id="pcs_in_use" class="status-value">-</span></p>
    <p><strong>Available PCs:</strong> <span id="pcs_available" class="status-value">-</span></p>
    <a href="/">⬅ Back to Home</a>
  </div>

  <script>
    async function fetchStatus() {
      const res = await fetch('/api/status');
      const data = await res.json();
      document.getElementById('total_pcs').innerText = data.total_pcs;
      document.getElementById('pcs_in_use').innerText = data.pcs_in_use;
      document.getElementById('pcs_available').innerText = data.pcs_available;
    }
    fetchStatus();
    setInterval(fetchStatus, 5000);
  </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/login')
def login_page():
    return render_template_string(LOGIN_HTML)

@app.route('/status')
def status_page():
    return render_template_string(STATUS_HTML)

if __name__ == '__main__':
    app.run(debug=True)
