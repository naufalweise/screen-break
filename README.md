# Screen Break Reminder (macOS)

A professional eye-care utility that forces a 1-minute screen break every 15 minutes of usage. Built with a clean **MVC (Model-View-Controller)** architecture using **Native macOS Cocoa (PyObjC)**.

## Features

- **Native macOS Overlay**: Uses Cocoa `NSWindow` for a true, robust, and un-dismissible experience.
- **Automatic Trigger**: Activates every 15 minutes to prevent digital eye strain.
- **Inactivity dismissal**: The break ends only after **60 seconds of total inactivity** (no mouse/keyboard).
- **Password Bypass**: Enter `rest` in the overlay field to skip the break.
- **Visual Feedback**: Real-time inactivity countdown.

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
python3 screen_break.py
```

## Architecture
- **Model**: Logic for timers and activity states.
- **View**: Native Cocoa implementation using `AppKit`.
- **Controller**: Orchestration using `NSTimer` and `NSEvent` monitors.

## License
MIT
