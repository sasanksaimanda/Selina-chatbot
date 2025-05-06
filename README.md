# Selina-chatbot

A Flask-based web application that provides a mental wellness chatbot using Cohere's AI API. The chatbot offers supportive and empathetic responses to users seeking emotional support and wellness advice.

## Features

- **User Authentication**: Secure signup, login, and session management
- **AI-Powered Chatbot**: Integration with Cohere's conversational AI for intelligent responses
- **Chat History**: Users can access their previous conversations
- **Admin Dashboard**: Administrative control panel for user management
- **Responsive Design**: Mobile-friendly user interface

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **AI Integration**: Cohere API
- **Authentication**: Werkzeug Security
- **Deployment**: Vercel

## Local Development Setup

### Prerequisites

- Python 3.9+
- MongoDB database
- Cohere API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mental-wellness-chatbot.git
   cd mental-wellness-chatbot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your_secret_key
   MONGO_URI=your_mongodb_connection_string
   COHERE_API_KEY=your_cohere_api_key
   ADMIN_PASSWORD=desired_admin_password
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application at `http://localhost:5000`

## Project Structure

```
├── app.py                  # Main application file
├── templates/              # HTML templates
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── signup.html         # Signup page
│   ├── chat.html           # Chat interface
│   ├── history.html        # Chat history page
│   └── admin.html          # Admin dashboard
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript files
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment configuration
└── .env                    # Environment variables (not tracked by git)
```

## Deploying to Vercel

### Prerequisites

- [Vercel account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/download) (optional)

### Deployment Steps

1. **Set up MongoDB Atlas**:
   - Create a MongoDB Atlas account if you don't have one
   - Set up a new cluster
   - Create a database user
   - Whitelist all IP addresses (0.0.0.0/0) for development
   - Get your MongoDB connection string

2. **Prepare your project**:
   - Ensure your project includes:
     - `requirements.txt`
     - `vercel.json`
     - `.env` (for local development only)

3. **Deploy using Vercel Dashboard**:
   - Log in to your Vercel account
   - Click "Import Project"
   - Select "Import Git Repository" and provide your repository URL or "Upload" for direct upload
   - Configure your project:
     - Framework Preset: Other
     - Build Command: Leave blank (defined in vercel.json)
     - Output Directory: Leave blank
     - Install Command: `pip install -r requirements.txt`
   - Add environment variables (same as in your .env file)
   - Click "Deploy"

4. **Deploy using Vercel CLI** (alternative):
   - Install Vercel CLI: `npm i -g vercel`
   - Login to Vercel: `vercel login`
   - Deploy: `vercel`
   - Follow the prompts to configure your project
   - Add environment variables using the Vercel dashboard

### Important Notes

- Your MongoDB database must be accessible from Vercel's servers (use MongoDB Atlas with network access from anywhere)
- Never commit your `.env` file to Git
- Use Vercel's environment variables interface to securely store API keys and credentials
- The provided `vercel.json` configures Vercel to treat your app as a Python application and routes all traffic to your Flask app

## API Routes

- `/`: Landing page
- `/signup`: User registration
- `/login`: User authentication
- `/logout`: User logout
- `/chat`: Chat interface
- `/send_message`: API endpoint to send messages to the chatbot
- `/history`: User's chat history
- `/admin`: Admin dashboard (restricted access)

## Customization

### Chatbot Behavior

The chatbot's behavior is defined in the `send_message` route in `app.py`. You can modify the system prompt and Cohere API parameters to change how the chatbot responds:

```python
# System prompt for mental wellness assistant
system_prompt = """You are a mental wellness assistant that provides supportive, empathetic responses. 
Focus on emotional support, wellness tips, and positive encouragement. 
If you detect concerning content about self-harm or harm to others, suggest professional help resources. 
Do not make medical diagnoses or prescribe treatments."""

# Cohere API parameters
response = co.chat(
    message=message,
    chat_history=chat_history,
    model="command",  # You can change the model
    temperature=0.7,  # Adjust for more/less creative responses
    preamble=system_prompt,
    max_tokens=300    # Adjust response length
)
```

### UI Customization

You can customize the UI by modifying the HTML templates in the `templates` directory and adding CSS in the `static/css` directory.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
