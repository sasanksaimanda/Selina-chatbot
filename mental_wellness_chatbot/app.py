from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import cohere  # Import Cohere library
import uuid

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure MongoDB
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

# Configure Cohere API
cohere_api_key = os.getenv('COHERE_API_KEY')
co = cohere.Client(cohere_api_key)  # Initialize Cohere client

# Helper function to format the current date/time
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate data
        if not username or not email or not password:
            flash('Please fill all required fields', 'error')
            return redirect(url_for('signup'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        
        # Check if username or email already exists
        if mongo.db.users.find_one({'username': username}):
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))
            
        if mongo.db.users.find_one({'email': email}):
            flash('Email already exists', 'error')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': get_current_time(),
            'role': 'user'  # Default role
        }
        
        user_id = mongo.db.users.insert_one(new_user).inserted_id
        
        # Create session
        session['user_id'] = str(user_id)
        session['username'] = username
        session['role'] = 'user'
        
        flash('Registration successful!', 'success')
        return redirect(url_for('chat'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user
        user = mongo.db.users.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            # Create session
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            
            flash('Login successful!', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    return render_template('chat.html', username=session['username'])

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    message = request.form.get('message')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Save user message
    chat_id = str(uuid.uuid4())
    user_message = {
        'chat_id': chat_id,
        'user_id': session['user_id'],
        'sender': 'user',
        'content': message,
        'timestamp': get_current_time()
    }
    mongo.db.messages.insert_one(user_message)
    
    # Get user's chat history for context
    user_history = list(mongo.db.messages.find(
        {'user_id': session['user_id']}
    ).sort('timestamp', -1).limit(10))  # Get recent messages
    
    # Format chat history for Cohere
    chat_history = []
    for msg in reversed(user_history):
        role = "USER" if msg['sender'] == 'user' else "CHATBOT"
        chat_history.append({"role": role, "message": msg['content']})
    
    # System prompt for mental wellness assistant
    system_prompt = """You are a mental wellness assistant that provides supportive, empathetic responses. 
    Focus on emotional support, wellness tips, and positive encouragement. 
    If you detect concerning content about self-harm or harm to others, suggest professional help resources. 
    Do not make medical diagnoses or prescribe treatments."""
    
    try:
        # Use Cohere's chat endpoint
        response = co.chat(
            message=message,
            chat_history=chat_history,
            model="command",  # Use appropriate Cohere model
            temperature=0.7,
            preamble=system_prompt,
            max_tokens=300
        )
        ai_response = response.text
    except Exception as e:
        app.logger.error(f"Cohere API error: {str(e)}")
        ai_response = "I'm having trouble connecting right now. Please try again in a moment."
    
    # Save AI response
    bot_message = {
        'chat_id': chat_id,
        'user_id': session['user_id'],
        'sender': 'assistant',
        'content': ai_response,
        'timestamp': get_current_time()
    }
    mongo.db.messages.insert_one(bot_message)
    
    return jsonify({
        'message': ai_response,
        'timestamp': get_current_time()
    })

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    # Get all messages for the current user
    messages = list(mongo.db.messages.find(
        {'user_id': session['user_id']}
    ).sort('timestamp', 1))
    
    # Group messages by chat_id
    chats = {}
    for message in messages:
        chat_id = message['chat_id']
        if chat_id not in chats:
            chats[chat_id] = []
        chats[chat_id].append(message)
    
    return render_template('history.html', chats=chats)

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    users = list(mongo.db.users.find())
    
    # Count messages for each user
    for user in users:
        user['message_count'] = mongo.db.messages.count_documents({'user_id': str(user['_id'])})
    
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    # Create admin user if not exists
    admin = mongo.db.users.find_one({'role': 'admin'})
    if not admin:
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin_user = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': generate_password_hash(admin_password),
            'created_at': get_current_time(),
            'role': 'admin'
        }
        mongo.db.users.insert_one(admin_user)
        print("Admin user created!")
    
    app.run(debug=True)