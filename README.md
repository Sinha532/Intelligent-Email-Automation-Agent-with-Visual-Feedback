# AI Gmail Automation Agent

## Overview

The AI Gmail Automation Agent is a comprehensive web-based solution that combines artificial intelligence with browser automation to streamline email composition and sending processes. This application features an intelligent chat interface powered by Google's Gemini AI, real-time visual feedback through live screenshots, and robust email automation capabilities using Selenium WebDriver.

## Architecture

### System Design

The application follows a modern client-server architecture with real-time communication capabilities:

```
Frontend (HTML/CSS/JavaScript) 
    ↕ (HTTP/WebSocket)
Backend (Flask + SocketIO)
    ↕ (API Calls)
Gemini AI (Content Generation)
    ↕ (WebDriver)
Chrome Browser (Automation)
```

### Core Components

1. **Frontend Interface**: Interactive web application with dual-pane layout
   - Chat interface for natural language interaction
   - Real-time visual feedback panel displaying live screenshots
   - Progress tracking and status indicators

2. **Backend Server**: Flask-based API server with WebSocket support
   - RESTful endpoints for chat communication
   - Real-time screenshot broadcasting via SocketIO
   - Session management for multi-user scenarios

3. **AI Content Generator**: Gemini AI integration for professional email composition
   - Context-aware email subject and body generation
   - Personalised content based on user input and recipient details

4. **Browser Automation Engine**: Selenium WebDriver implementation
   - Chrome browser automation for Gmail interaction
   - Screenshot capture at each automation step
   - Robust error handling and recovery mechanisms

### Visual Proxy Implementation

The visual feedback system is implemented through a sophisticated screenshot capture and broadcasting mechanism:

1. **Screenshot Capture**: At each automation step, the system captures the current browser state
2. **Base64 Encoding**: Screenshots are converted to base64 format for efficient transmission
3. **Real-time Broadcasting**: Images are pushed to the frontend via WebSocket connections
4. **Progressive Display**: Frontend receives and displays screenshots with step descriptions and progress indicators

## Technologies Used

### Backend Technologies
- **Python 3.8+**: Core programming language
- **Flask**: Web framework for API endpoints
- **Flask-SocketIO**: Real-time bidirectional communication
- **Selenium WebDriver**: Browser automation
- **Google Generative AI (Gemini)**: Content generation
- **python-dotenv**: Environment variable management

### Frontend Technologies
- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with gradients and animations
- **Vanilla JavaScript**: Client-side logic and WebSocket handling
- **Socket.IO Client**: Real-time communication

### Additional Tools
- **Chrome WebDriver**: Browser automation driver
- **Base64 Encoding**: Image data transmission
- **Threading**: Asynchronous task execution

## Features

### Core Functionality
- **Natural Language Processing**: Chat-based email composition requests
- **AI-Powered Content Generation**: Professional email drafting using Gemini AI
- **Automated Gmail Login**: Secure credential handling and authentication
- **Email Composition**: Automated recipient, subject, and body population
- **One-Click Sending**: Complete email delivery automation

### Visual Feedback System
- **Live Screenshots**: Real-time browser state visualization
- **Progress Tracking**: Step-by-step automation progress with percentage completion
- **Status Updates**: Current operation and system state indicators
- **Error Visualization**: Screenshot-based error diagnosis

### User Experience
- **Conversational Interface**: Natural language interaction for email requests
- **Session Management**: Multi-user support with isolated sessions
- **Responsive Design**: Mobile-friendly interface design
- **Email Preview**: AI-generated content preview before sending

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser (latest version)
- Chrome WebDriver (compatible with your Chrome version)
- Gemini API key from Google AI Studio

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd gmail-automation-agent
   ```

2. **Install Python Dependencies**
   ```bash
   pip install flask flask-socketio selenium python-dotenv google-generativeai
   ```

3. **Download Chrome WebDriver**
   - Visit [ChromeDriver Downloads](https://chromedriver.chromium.org/)
   - Download the version matching your Chrome browser
   - Extract and place `chromedriver.exe` in your project directory
   - Update the path in `app.py` (line 144):
     ```python
     chrome_driver_path = r"path/to/your/chromedriver.exe"
     ```

4. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secure-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   ```

5. **Directory Structure Setup**
   Ensure the following structure exists:
   ```
   project-root/
   ├── app.py
   ├── templates/
   │   └── index.html
   ├── static/
   │   ├── css/
   │   │   └── style.css
   │   └── js/
   │       └── script.js
   ├── .env
   └── chromedriver.exe
   ```

### Running the Application

1. **Start the Server**
   ```bash
   python app.py
   ```

2. **Access the Application**
   Open your browser and navigate to: `http://localhost:5000`

3. **Initial Setup**
   - The application will prompt for your name for personalised emails
   - Follow the conversational flow to send emails

## Usage Guide

### Basic Email Sending

1. **Start Conversation**: Enter your full name when prompted
2. **Request Email**: Use natural language like:
   - "Send an email to hr@company.com about internship opportunity"
   - "Email john@example.com about project collaboration"
   - "Send a follow-up email to recruiter@startup.com"

3. **Provide Credentials**: When prompted, enter:
   - Your Gmail address
   - Your Gmail password (consider using App Password for security)

4. **Monitor Progress**: Watch the live visual feedback as the automation proceeds
5. **Confirmation**: Receive confirmation once the email is sent successfully

### Advanced Features

- **Email Preview**: Review AI-generated content before sending
- **Session Continuity**: Multiple email requests in the same session
- **Error Recovery**: Detailed error messages with visual context
- **Progress Tracking**: Real-time progress with screenshot updates

## Implementation Details

### Key Design Decisions

1. **Conversational Interface**: Chose natural language processing over form-based input to improve user experience and reduce friction

2. **Real-time Visual Feedback**: Implemented live screenshot streaming to provide transparency and debugging capabilities during automation

3. **AI Content Generation**: Integrated Gemini AI to ensure professional, context-aware email composition

4. **Session Management**: Implemented stateful sessions to handle multi-step conversations and multiple users

### Challenges Overcome

1. **Screenshot Transmission**: Solved large image data transfer by implementing base64 encoding and WebSocket streaming

2. **Gmail Authentication**: Handled dynamic element selectors and authentication flows with robust waiting strategies

3. **Error Handling**: Implemented comprehensive error catching with visual feedback for debugging

4. **Concurrent Users**: Used threading for background automation while maintaining responsive chat interface

### Security Considerations

1. **Credential Handling**: Credentials are only stored temporarily in memory during active sessions
2. **Session Isolation**: Each user session is completely isolated from others
3. **Environment Variables**: Sensitive API keys stored in environment files
4. **Error Logging**: Detailed logging for debugging without exposing sensitive information

## Browser Automation Flow

The automation process follows this sequence:

1. **Initialisation**: Setup Chrome WebDriver with optimised options
2. **Gmail Navigation**: Navigate to Google account login page
3. **Authentication**: 
   - Enter email address
   - Navigate to password page
   - Enter password and submit
4. **Gmail Interface**: Wait for Gmail interface to load completely
5. **Compose Email**:
   - Click compose button
   - Fill recipient field
   - Add subject line
   - Compose email body
6. **Send Email**: Click send button and confirm delivery
7. **Cleanup**: Close browser and cleanup resources

Each step includes screenshot capture and progress updates sent to the frontend.

## Error Handling

The application implements multiple layers of error handling:

- **Network Errors**: Retry mechanisms for network-related failures
- **Element Not Found**: Multiple selector strategies and waiting mechanisms
- **Authentication Failures**: Clear error messages with troubleshooting steps
- **API Failures**: Fallback content generation when AI services are unavailable
- **Browser Crashes**: Automatic browser restart and state recovery

## API Endpoints

### REST Endpoints
- `GET /`: Serve main application interface
- `POST /chat`: Handle chat messages and return AI responses
- `GET /status`: Return current automation status

### WebSocket Events
- `connect`: Client connection establishment
- `disconnect`: Client disconnection handling
- `status_update`: Real-time automation progress updates
- `automation_complete`: Successful completion notification
- `chat_message`: Server-initiated chat messages

## Contributing

We welcome contributions to improve the Gmail Automation Agent. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## Troubleshooting

### Common Issues

1. **ChromeDriver Version Mismatch**
   - Ensure ChromeDriver version matches your Chrome browser version
   - Download the correct version from ChromeDriver website

2. **Gmail Authentication Issues**
   - Consider using App Passwords instead of account passwords
   - Ensure 2-factor authentication is properly configured

3. **WebSocket Connection Failures**
   - Check firewall settings
   - Verify port 5000 is available

4. **AI Content Generation Failures**
   - Verify Gemini API key is correctly configured
   - Check API quota and billing status

## Future Enhancements

- **Multi-Platform Support**: Extend automation to other email providers
- **Scheduled Emails**: Add capability to schedule emails for future delivery
- **Template Management**: Create and manage email templates
- **Advanced Analytics**: Email delivery and engagement tracking
- **Enhanced Security**: OAuth2 integration for better security
- **Mobile App**: Native mobile application development

## Licence

This project is developed for educational and demonstration purposes. Please ensure compliance with Gmail's Terms of Service and applicable data protection regulations when using this application.

## Support

For technical support, bug reports, or feature requests, please create an issue in the project repository or contact the development team.

---

**Note**: This application is designed for legitimate email automation purposes. Please use responsibly and in accordance with Gmail's Terms of Service and applicable laws regarding automated access to online services.
