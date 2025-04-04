# ChatApp Backend

### Description: 
A robust backend solution built with Django designed to power real-time chat applications, enabling efficient communication between users.

---

## Features:

-  **Real-Time Communication**: Enable instant messaging between users.
-  **User Authentication**: Secure login and registration mechanisms.
-  **Message History**: Store and retrieve past conversations efficiently.
-  **Scalable Architecture**: Designed for high traffic and concurrent users.

---

## Installation:

### Prerequisites:
- Python 3.8 or higher
- pip (Python package installer)

### Steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/geeksloths/Chat-App.git
   cd Chat-App
   cd Backend
   ```
2. Make an environment:
  
   ```bash
   py -m venv .venv
   ```
3. Activate Environemnt:
  
   ```bash
   cd .venv/scripts && activate #For windows
   cd .venv/bin && source activate #For linux
   ```
4. Install dependencies:
  
   ```bash
   pip install -r requirements.txt
   ```
5. Run Server:
   Just Open Runner.exe or
   ```bash
   py runner.py
   ```
## Usage:

### API Endpoints
For HTTP Server there are:

   ```bash
      GET  http://your_server/api/messages/main_room #Gets all old messages of the room
      POST http://your_server/api/messages/main_room/file #Uploads files on server
   ```
And For WS Server
   ```bash
   ws://your_server/ws/messages/main_room/ #Accesses ws server for a real-time connection
   ```
Thank you for choosing ChatApp Backend! 🚀