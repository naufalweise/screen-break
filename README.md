# Screen Break Reminder (macOS)

A professional eye-care utility that forces a 1-minute screen break every 15 minutes of usage. Built with a clean **MVC (Model-View-Controller)** architecture using **Native macOS Cocoa (PyObjC)**.

## Features

- **Native macOS Overlay**: Uses Cocoa `NSWindow` for a true, robust, and un-dismissible experience.
- **Dual Countdowns**: Persistent HUD for "Screen Time" and an overlay countdown for "Break Time".
- **Activity-Based Start**: Screen time countdown only begins after the system detects user activity.
- **Sound Notifications**: Plays native macOS sounds when breaks start and end.
- **Inactivity dismissal**: The break ends only after **60 seconds of total inactivity**.
- **Password Bypass**: Enter `rest` in the overlay field to skip the break.

## Installation & Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python3 app.py
```

## Architecture (Multi-file MVC)
The code is split into logical components for maintainability:
- **`model.py`**: Business logic, timers, and state management.
- **`view.py`**: Native Cocoa GUI implementation and sound effects.
- **`controller.py`**: Orchestration and event handling.
- **`app.py`**: Entry point and Application Delegate.

## Configuration
Constants like `WORK_DURATION_MIN` and `BREAK_DURATION_SEC` can be adjusted at the top of `model.py`.

## License
MIT
