# Real-Time Tic Tac Toe

A browser-based, real-time Tic Tac Toe game built with **Django Channels** and **WebSockets**. Supports multiplayer gameplay and a single-player mode with minimax algorithm.

## Features

- Real-time **multiplayer mode** with synchronized gameplay across clients  
- **Server-side move validation**, turn enforcement, and win/tie detection  
- **In-room chat** and **move timers** for each player  
- **Mutual-consent game reset** mechanism  
- Single-player mode with **AI**:
  - Random moves
  - **Unbeatable minimax strategy**  
- Room verification with database-backed UUIDs  
- Clean separation of **game logic** and WebSocket consumers  

## Setup

1. Get the repository:
   Clone or download and extract the repo and cd into it

2. Create a virtual environment:
    ```python -m venv venv```
    On Windows: ```venv\Scripts\activate```
    On Linux source ```venv/bin/activate```

3. Install dependencies:
    ```pip install -r requirements.txt```

4. Add a secret key:
    - Create secrets.py file in TicTacToeMult folder (next the one containing settings.py)
    - Run ```python -c "from django.core.management.utils import get_random_secret_key; print(f\"my_secret_key = '{get_random_secret_key()}'\")" > TicTacToeMult/secrets.py``` in the terminal.

5. Run migrations:
    ```python manage.py migrate```

6. Start the server:
    ```python manage.py runserver```

7. Open your browser at http://127.0.0.1:8000 and enjoy the game!

## Usage
- Create or join a game room
- Play against another player or computer
- Use chat to talk to the opponent for interactive gameplay
- Reset game when both players agree