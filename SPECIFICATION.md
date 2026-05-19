# Technical Specification: Screen Break Reminder (macOS)

## 1. Overview
Screen Break Reminder is a native macOS utility designed to mitigate digital eye strain by enforcing regular breaks. It follows the "20-20-20 rule" principle, requiring 60 seconds of inactivity every 15 minutes of usage.

## 2. System Requirements
- **Operating System**: macOS 10.13 or later (Verified on macOS 26.2).
- **Runtime**: Python 3.10+.
- **Dependencies**: `pyobjc-framework-Cocoa`.

## 3. Architecture (MVC)
The application is strictly decoupled into Model, View, and Controller components.

### 3.1 Model (`model.py`)
- **State Management**:
    - `is_break_active`: Boolean flag for the overlay state.
    - `is_waiting_for_return`: Boolean flag for the post-break/pre-work state.
- **Timing Logic**:
    - Calculates remaining work time based on `work_start_time`.
    - Calculates remaining break time based on `last_activity_time`.
- **Constants**:
    - `WORK_DURATION_MIN`: Duration of usage before break (default: 15).
    - `BREAK_DURATION_SEC`: Required idle time (default: 60).
    - `PASSWORD`: Bypass string (default: "rest").

### 3.2 View (`view.py`)
- **Native Windows**:
    - `BreakWindow`: A subclass of `NSWindow` with `NSWindowStyleMaskBorderless`.
    - `Overlay`: Fullscreen black window at level `1001` (above standard windows).
    - `Status HUD`: Small semi-transparent floating window (220x40) at the top right.
- **Sound Engine**:
    - Uses `NSSound` to play system sounds ("Glass" and "Hero").
- **UI Components**:
    - `NSTextField`: Displays countdowns and instructions.
    - `NSSecureTextField`: Secure input for the bypass password.

### 3.3 Controller (`controller.py`)
- **Main Loop**: Uses `NSTimer` at 1Hz to drive state transitions and UI updates.
- **Event Handling**: 
    - Employs `NSEvent.addLocalMonitorForEventsMatchingMask_handler_` to detect system-wide activity (within the app's scope) to reset the idle timer or start a work cycle.
- **Orchestration**: Manages the transitions between `Work` -> `Break` -> `Waiting` -> `Work`.

## 4. Functional Logic

### 4.1 Usage Cycle
1. **Waiting State**: The app starts here. The HUD shows "Waiting for Activity...".
2. **Work State**: Triggered by the first detected mouse/key event. The 15-minute countdown begins.
3. **Trigger**: When the work timer hits zero, the overlay is displayed and a start sound plays.

### 4.2 Break Cycle
1. **Overlay Active**: Fullscreen black screen covers all monitors. Standard closing shortcuts (Cmd+W, Cmd+Q) are ignored by the window level and delegate.
2. **Inactivity Requirement**: The 60-second timer only counts down if no events are detected. Any event (mouse wiggle, keypress) resets the timer to 60.
3. **Bypass**: Typing the correct password and pressing Enter terminates the break immediately.
4. **Completion**: Upon success, an end sound plays, the overlay hides, and the app returns to the **Waiting State**.

## 5. Security & Persistence
- **Window Level**: Set to `1001` to ensure it stays above the Dock, Menu Bar, and other applications.
- **Focus Management**: The overlay uses `activateIgnoringOtherApps_` and `makeKeyAndOrderFront_` to force focus to the password field.
- **Input Blocking**: While the overlay is active, the OS prevents interaction with background windows.

## 6. Directory Structure
```text
screen-break/
├── app.py           # Entry point / App Delegate
├── model.py         # Business logic & Constants
├── view.py          # Native Cocoa UI & Sounds
├── controller.py    # Logic orchestration
├── requirements.txt # Dependencies
└── README.md        # User Guide
```
