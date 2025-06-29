from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import base64
import threading
from datetime import datetime
import os
from google import genai
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gmail-automation-flask-app-2024-secure-key-a1b2c3d4e5f6'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Global variables
driver = None
automation_status = {
    'running': False,
    'current_step': '',
    'progress': 0,
    'error': None
}

# Session storage for chat context
user_sessions = {}

def generate_email_content(user_message, username):
    """Generate email subject and body using Gemini based on user's request"""
    try:
        prompt = f"""You are a professional email writing assistant. Generate a professional email with subject and body (4-5 lines) based on user's request.

User Request: {user_message}
Sender Name: {username}

Format your response exactly as:
SUBJECT: [subject line]
BODY: [email body in 4-5 lines]

Make it professional, concise, and include the sender's name at the end. Use proper email etiquette."""

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", 
            contents=prompt
        )
        
        content = response.text.strip()
        print(f"DEBUG - Raw Gemini response: {content}")  # Debug line
        
        # Initialize variables
        subject = ""
        body = ""
        
        # Split content into lines
        lines = content.split('\n')
        
        # Find SUBJECT line
        subject_found = False
        body_found = False
        body_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
                subject_found = True
                print(f"DEBUG - Found subject: {subject}")  # Debug line
                
            elif line.startswith("BODY:"):
                body_found = True
                # Get the rest of the line after "BODY:"
                body_start = line.replace("BODY:", "").strip()
                if body_start:
                    body_lines.append(body_start)
                
                # Get remaining lines for body
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith("SUBJECT:"):
                        body_lines.append(next_line)
                
                break
        
        # Join body lines
        if body_lines:
            body = '\n'.join(body_lines)
            print(f"DEBUG - Found body: {body}")  # Debug line
        
        # Fallback parsing if the above doesn't work
        if not subject_found or not body_found:
            print("DEBUG - Primary parsing failed, trying fallback")
            
            # Try to find content after SUBJECT: and BODY: markers
            content_upper = content.upper()
            
            if "SUBJECT:" in content_upper:
                subject_start = content_upper.find("SUBJECT:") + 8
                subject_end = content_upper.find("BODY:", subject_start)
                
                if subject_end == -1:
                    subject_end = content_upper.find("\n", subject_start)
                    if subject_end == -1:
                        subject_end = len(content)
                
                subject = content[subject_start:subject_end].strip()
                print(f"DEBUG - Fallback subject: {subject}")
            
            if "BODY:" in content_upper:
                body_start = content_upper.find("BODY:") + 5
                body = content[body_start:].strip()
                print(f"DEBUG - Fallback body: {body}")
        
        # Final fallback if parsing completely fails
        if not subject or not body:
            print("DEBUG - All parsing failed, using final fallback")
            subject = "Professional Inquiry"
            body = f"Dear Recipient,\n\nI hope this email finds you well.\n\n{user_message}\n\nThank you for your consideration.\n\nBest regards,\n{username}"
        
        # Ensure username is included if not already present
        if username.lower() not in body.lower():
            body = body.rstrip() + f"\n\nBest regards,\n{username}"
            
        print(f"DEBUG - Final subject: {subject}")  # Debug line
        print(f"DEBUG - Final body: {body}")  # Debug line
            
        return {
            "subject": subject,
            "body": body
        }
            
    except Exception as e:
        print(f"Error generating email content: {e}")
        # Fallback email generation
        return {
            "subject": "Professional Communication",
            "body": f"Dear Recipient,\n\nI hope this email finds you well.\n\n{user_message}\n\nThank you for your time and consideration.\n\nBest regards,\n{username}"
        }

def parse_email_command(message):
    """Parse user message to extract email addresses"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, message)
    
    return {
        "emails": emails,
        "original_message": message
    }

def chat_response(user_message, session_id):
    """Generate chat response based on user message"""
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "state": "need_username",
            "context": {}
        }
    
    session = user_sessions[session_id]
    message_lower = user_message.lower()
    
    # Handle username collection first
    if session["state"] == "need_username":
        # Extract name from message
        username = user_message.strip()
        if len(username) > 1 and not any(char in username for char in ['@', 'http', 'www']):
            session["context"]["username"] = username
            session["state"] = "idle"
            return {
                "response": f"Nice to meet you, {username}! I'm your AI email automation assistant. I can help you send professional emails automatically.\n\nTry saying something like:\n• 'Send an email to hr@company.com about internship opportunity'\n• 'Email john@example.com about project collaboration'\n• 'Send a follow-up email to recruiter@startup.com'",
                "type": "general",
                "needs_input": False
            }
        else:
            return {
                "response": "Please provide your full name (e.g., 'John Smith'):",
                "type": "username_request",
                "needs_input": True
            }
    
    # Check if user wants to send an email
    if any(phrase in message_lower for phrase in ["send email", "send mail", "email to", "mail to", "compose email"]):
        parsed = parse_email_command(user_message)
        
        if parsed["emails"]:
            # Email found in message
            session["context"]["recipient"] = parsed["emails"][0]
            session["context"]["original_message"] = user_message
            session["state"] = "need_gmail"
            
            return {
                "response": f"I'll help you send an email to {parsed['emails'][0]}. What's your Gmail address?",
                "type": "gmail_request",
                "needs_input": True
            }
        else:
            # No email found, ask for recipient
            session["state"] = "need_recipient"
            session["context"]["original_message"] = user_message
            
            return {
                "response": "I'd be happy to help you send an email! What's the recipient's email address?",
                "type": "recipient_request",
                "needs_input": True
            }
    
    # Handle different states
    if session["state"] == "need_recipient":
        parsed = parse_email_command(user_message)
        
        if parsed["emails"]:
            session["context"]["recipient"] = parsed["emails"][0]
            session["state"] = "need_gmail"
            return {
                "response": f"Great! I'll send the email to {parsed['emails'][0]}. Now, what's your Gmail address?",
                "type": "gmail_request",
                "needs_input": True
            }
        else:
            return {
                "response": "Please provide a valid email address (e.g., example@company.com).",
                "type": "recipient_request",
                "needs_input": True
            }
    
    elif session["state"] == "need_gmail":
        # Extract Gmail address
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, user_message)
        
        if emails:
            session["context"]["gmail"] = emails[0]
            session["state"] = "need_password"
            return {
                "response": f"Got it! Using {emails[0]} to send the email. Now please provide your Gmail password:",
                "type": "password_request",
                "needs_input": True
            }
        else:
            return {
                "response": "Please provide a valid Gmail address (e.g., yourname@gmail.com):",
                "type": "gmail_request",
                "needs_input": True
            }
    
    elif session["state"] == "need_password":
        # Store password
        session["context"]["password"] = user_message.strip()
        session["state"] = "ready_to_send"
        
        return {
            "response": f"Perfect! Generating professional email content and sending to {session['context']['recipient']}...",
            "type": "ready_to_send",
            "context": session["context"]
        }
    
    # General conversation
    return {
        "response": "Hi! I'm your email automation assistant. To get started, please tell me your name:",
        "type": "username_request",
        "needs_input": True
    }

def setup_chrome_driver():
    """Setup Chrome driver with optimized options"""
    chrome_driver_path = r"C:\Users\lokeshsinha\OneDrive\Desktop\chromedriver-win64\chromedriver.exe"
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def take_screenshot_and_emit(step_name, progress):
    """Take screenshot and emit to frontend"""
    global driver
    if driver:
        try:
            screenshot_png = driver.get_screenshot_as_png()
            img_base64 = base64.b64encode(screenshot_png).decode('utf-8')
            
            automation_status['current_step'] = step_name
            automation_status['progress'] = progress
            
            socketio.emit('status_update', {
                'step': step_name,
                'progress': progress,
                'screenshot': f"data:image/png;base64,{img_base64}",
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")

def wait_and_find_element(driver, selectors, timeout=10):
    """Find element with multiple selectors"""
    wait = WebDriverWait(driver, timeout)
    
    for selector_type, selector_value in selectors:
        try:
            element = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
            return element
        except TimeoutException:
            continue
    
    raise TimeoutException(f"Could not find element")

def email_automation_task(gmail_id, password, recipient, email_content):
    """Email automation task"""
    global driver, automation_status
    
    try:
        automation_status['running'] = True
        automation_status['error'] = None
        
        socketio.emit('chat_message', {
            'type': 'system',
            'message': 'Starting email automation...',
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
        driver = setup_chrome_driver()
        
        # Navigate to Gmail
        driver.get("https://accounts.google.com/signin/v2/identifier?service=mail&continue=https://mail.google.com")
        time.sleep(2)
        take_screenshot_and_emit("Gmail login page loaded", 20)
        
        # Enter email
        email_input = wait_and_find_element(driver, [
            (By.ID, "identifierId"),
            (By.XPATH, "//input[@type='email']")
        ])
        email_input.send_keys(gmail_id)
        
        # Click Next
        next_btn = wait_and_find_element(driver, [
            (By.ID, "identifierNext"),
            (By.XPATH, "//div[@id='identifierNext']")
        ])
        next_btn.click()
        time.sleep(3)
        take_screenshot_and_emit("Email entered", 40)
        
        # Enter password
        password_input = wait_and_find_element(driver, [
            (By.NAME, "password"),
            (By.XPATH, "//input[@type='password']")
        ])
        password_input.send_keys(password)
        
        # Submit password
        password_next = wait_and_find_element(driver, [
            (By.ID, "passwordNext"),
            (By.XPATH, "//div[@id='passwordNext']")
        ])
        password_next.click()
        time.sleep(5)
        take_screenshot_and_emit("Logged in", 60)
        
        # Wait for Gmail to load
        WebDriverWait(driver, 20).until(
            lambda d: "mail.google.com" in d.current_url
        )
        time.sleep(3)
        take_screenshot_and_emit("Gmail loaded", 70)
        
        # Click Compose
        compose_btn = wait_and_find_element(driver, [
            (By.XPATH, "//div[contains(@class, 'T-I-KE') and contains(text(), 'Compose')]")
        ])
        compose_btn.click()
        time.sleep(2)
        take_screenshot_and_emit("Compose opened", 80)
        
        # Fill email form
        # Recipient
        recipient_field = wait_and_find_element(driver, [
            (By.XPATH, "//input[@aria-label='To recipients']")
        ])
        recipient_field.send_keys(recipient)
        recipient_field.send_keys(Keys.TAB)
        
        # Subject
        subject_field = wait_and_find_element(driver, [
            (By.NAME, "subjectbox")
        ])
        subject_field.send_keys(email_content["subject"])
        
        # Body
        body_field = wait_and_find_element(driver, [
            (By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
        ])
        body_field.send_keys(email_content["body"])
        
        take_screenshot_and_emit("Email composed", 90)
        
        # Send email
        send_btn = wait_and_find_element(driver, [
            (By.XPATH, "//div[@role='button' and contains(@aria-label, 'Send')]")
        ])
        send_btn.click()
        time.sleep(2)
        take_screenshot_and_emit("Email sent!", 100)
        
        socketio.emit('automation_complete', {
            'success': True,
            'message': f'Email sent successfully to {recipient}!',
            'email_content': email_content
        })
        
        socketio.emit('chat_message', {
            'type': 'success',
            'message': f'✅ Email sent to {recipient}!\n\nSubject: {email_content["subject"]}',
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        automation_status['error'] = error_msg
        
        socketio.emit('chat_message', {
            'type': 'error',
            'message': f'❌ Error: {error_msg}',
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
    finally:
        automation_status['running'] = False
        if driver:
            driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    response = chat_response(user_message, session_id)
    
    # If ready to send, start automation
    if response.get('type') == 'ready_to_send':
        context = response['context']
        
        # Generate email content using Gemini with username
        username = context.get('username', 'Professional User')
        email_content = generate_email_content(context.get('original_message', user_message), username)
        
        # Start automation in background
        thread = threading.Thread(
            target=email_automation_task,
            args=(context['gmail'], context['password'], context['recipient'], email_content)
        )
        thread.daemon = True
        thread.start()
    
    return jsonify(response)

@app.route('/status')
def get_status():
    return jsonify(automation_status)

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to Gmail Automation Agent'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("Starting Gmail Automation Agent...")
    print("Access: http://localhost:5000")
    
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)