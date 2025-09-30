from flask import Flask, request, render_template_string, redirect, url_for, session, flash, jsonify
import sqlite3
import requests
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'admin-secret-key-approval-system'

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'lucifer2025'

# Database URL for the main application (update this with your main app's database URL)
MAIN_APP_DB_URL = 'https://your-main-app-url.com/api/users'  # This would be an API endpoint

# Admin login page
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Approval System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(45deg, #1a1a1a, #000000);
            color: white;
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            max-width: 400px;
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.3);
            border: 1px solid rgba(255, 0, 0, 0.2);
            backdrop-filter: blur(10px);
        }
        
        .admin-logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .admin-logo i {
            font-size: 4rem;
            color: #ff0000;
            margin-bottom: 15px;
        }
        
        .form-control {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 0, 0, 0.3);
            color: white;
            border-radius: 10px;
            padding: 12px;
        }
        
        .form-control:focus {
            background: rgba(255, 255, 255, 0.15);
            border-color: #ff0000;
            color: white;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.3);
        }
        
        .form-control::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        .btn-admin {
            background: linear-gradient(45deg, #ff0000, #ff6600);
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-weight: bold;
            width: 100%;
            color: white;
            transition: all 0.3s ease;
        }
        
        .btn-admin:hover {
            background: linear-gradient(45deg, #ff6600, #ff0000);
            transform: translateY(-2px);
            color: white;
        }
        
        .alert {
            border-radius: 10px;
            border: none;
        }
        
        h2 {
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(45deg, #ff0000, #ff6600);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="login-container">
        <div class="admin-logo">
            <i class="fas fa-shield-alt"></i>
            <h2>ADMIN PANEL</h2>
            <p class="text-center">Approval System</p>
        </div>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-warning">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="mb-3">
                <input type="text" class="form-control" name="username" placeholder="Admin Username" required>
            </div>
            <div class="mb-3">
                <input type="password" class="form-control" name="password" placeholder="Admin Password" required>
            </div>
            <button type="submit" class="btn-admin">LOGIN TO ADMIN PANEL</button>
        </form>
    </div>
</body>
</html>
"""

# Admin dashboard
ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Approval System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background: linear-gradient(45deg, #1a1a1a, #000000);
            color: white;
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 0, 0, 0.3);
        }
        
        .navbar-brand {
            color: white !important;
            font-weight: bold;
        }
        
        .nav-link {
            color: white !important;
        }
        
        .container {
            margin-top: 30px;
        }
        
        .stats-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 0, 0, 0.3);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .stats-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #ff0000;
        }
        
        .user-table {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 0, 0, 0.3);
        }
        
        .table-dark {
            background: transparent;
        }
        
        .table-dark th {
            border-color: rgba(255, 0, 0, 0.3);
            background: rgba(255, 0, 0, 0.1);
        }
        
        .table-dark td {
            border-color: rgba(255, 255, 255, 0.1);
        }
        
        .btn-approve {
            background: linear-gradient(45deg, #00ff00, #00aa00);
            border: none;
            border-radius: 5px;
            color: white;
            padding: 5px 15px;
            font-size: 0.9rem;
        }
        
        .btn-reject {
            background: linear-gradient(45deg, #ff0000, #aa0000);
            border: none;
            border-radius: 5px;
            color: white;
            padding: 5px 15px;
            font-size: 0.9rem;
        }
        
        .btn-approve:hover, .btn-reject:hover {
            transform: translateY(-1px);
            color: white;
        }
        
        .status-pending {
            color: #ffaa00;
        }
        
        .status-approved {
            color: #00ff00;
        }
        
        .status-rejected {
            color: #ff0000;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(45deg, #ff0000, #ff6600);
            border: none;
            border-radius: 50px;
            color: white;
            padding: 15px 20px;
            font-size: 1.1rem;
            box-shadow: 0 5px 15px rgba(255, 0, 0, 0.3);
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            color: white;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-shield-alt me-2"></i>
                ADMIN APPROVAL SYSTEM
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/logout">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <!-- Statistics -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">{{ stats.total }}</div>
                    <div>Total Users</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">{{ stats.pending }}</div>
                    <div>Pending Approval</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">{{ stats.approved }}</div>
                    <div>Approved</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number">{{ stats.rejected }}</div>
                    <div>Rejected</div>
                </div>
            </div>
        </div>
        
        <!-- User Management Table -->
        <div class="user-table">
            <h3 class="mb-4">
                <i class="fas fa-users me-2"></i>
                User Management
            </h3>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-success">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Access Key</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td>{{ user[0] }}</td>
                            <td>{{ user[1] }}</td>
                            <td>{{ user[2] }}</td>
                            <td><code>{{ user[3][:20] }}...</code></td>
                            <td>
                                {% if user[4] == 0 %}
                                    <span class="status-pending">
                                        <i class="fas fa-clock"></i> Pending
                                    </span>
                                {% elif user[4] == 1 %}
                                    <span class="status-approved">
                                        <i class="fas fa-check-circle"></i> Approved
                                    </span>
                                {% else %}
                                    <span class="status-rejected">
                                        <i class="fas fa-times-circle"></i> Rejected
                                    </span>
                                {% endif %}
                            </td>
                            <td>{{ user[5] }}</td>
                            <td>
                                {% if user[4] == 0 %}
                                    <form method="POST" action="/approve/{{ user[0] }}" style="display: inline;">
                                        <button type="submit" class="btn-approve">
                                            <i class="fas fa-check"></i> Approve
                                        </button>
                                    </form>
                                    <form method="POST" action="/reject/{{ user[0] }}" style="display: inline;">
                                        <button type="submit" class="btn-reject">
                                            <i class="fas fa-times"></i> Reject
                                        </button>
                                    </form>
                                {% else %}
                                    <small class="text-muted">No actions available</small>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if not users %}
            <div class="text-center py-5">
                <i class="fas fa-users fa-3x text-muted mb-3"></i>
                <p class="text-muted">No users found in the system.</p>
            </div>
            {% endif %}
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">
        <i class="fas fa-sync-alt"></i> Refresh
    </button>
    
    <script>
        // Auto refresh every 30 seconds
        setInterval(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

def get_users_from_db():
    """Get users from the main application database"""
    try:
        # In a real scenario, this would connect to the main app's database
        # For demo purposes, we'll create a local database with sample data
        conn = sqlite3.connect('approval_users.db')
        c = conn.cursor()
        
        # Create table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      email TEXT UNIQUE NOT NULL,
                      access_key TEXT UNIQUE NOT NULL,
                      approved INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Add sample data if table is empty
        c.execute('SELECT COUNT(*) FROM users')
        if c.fetchone()[0] == 0:
            sample_users = [
                ('john_doe', 'john@example.com', 'key-123-456-789', 0),
                ('jane_smith', 'jane@example.com', 'key-987-654-321', 0),
                ('admin_user', 'admin@example.com', 'key-admin-123', 1),
            ]
            c.executemany('INSERT INTO users (username, email, access_key, approved) VALUES (?, ?, ?, ?)', sample_users)
            conn.commit()
        
        c.execute('SELECT * FROM users ORDER BY created_at DESC')
        users = c.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_user_stats():
    """Get user statistics"""
    users = get_users_from_db()
    total = len(users)
    pending = len([u for u in users if u[4] == 0])
    approved = len([u for u in users if u[4] == 1])
    rejected = len([u for u in users if u[4] == -1])
    
    return {
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected
    }

@app.route('/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid admin credentials!')
    
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    users = get_users_from_db()
    stats = get_user_stats()
    
    return render_template_string(ADMIN_DASHBOARD_HTML, users=users, stats=stats)

@app.route('/approve/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = sqlite3.connect('approval_users.db')
        c = conn.cursor()
        c.execute('UPDATE users SET approved = 1 WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        flash(f'User ID {user_id} has been approved!')
    except Exception as e:
        flash(f'Error approving user: {e}')
    
    return redirect(url_for('dashboard'))

@app.route('/reject/<int:user_id>', methods=['POST'])
def reject_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = sqlite3.connect('approval_users.db')
        c = conn.cursor()
        c.execute('UPDATE users SET approved = -1 WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        flash(f'User ID {user_id} has been rejected!')
    except Exception as e:
        flash(f'Error rejecting user: {e}')
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

# API endpoint to sync with main application
@app.route('/api/sync-users', methods=['POST'])
def sync_users():
    """API endpoint to receive user data from main application"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('approval_users.db')
        c = conn.cursor()
        
        # Update or insert user data
        c.execute('''INSERT OR REPLACE INTO users (id, username, email, access_key, approved, created_at) 
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (data['id'], data['username'], data['email'], data['access_key'], 
                   data['approved'], data['created_at']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'User data synced'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
