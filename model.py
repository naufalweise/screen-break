import time

# ==========================================
# CONFIGURATION CONSTANTS
# ==========================================
WORK_DURATION_MIN = 1
BREAK_DURATION_SEC = 60
PASSWORD = "rest"

class BreakModel:
    """
    Handles the state of the application, timers, and password validation.
    """
    def __init__(self):
        self.work_duration_sec = WORK_DURATION_MIN * 60
        self.break_idle_duration_sec = BREAK_DURATION_SEC
        self.password = PASSWORD
        
        self.is_break_active = False
        self.is_waiting_for_return = False  # New state: wait for activity after break
        
        self.work_start_time = 0.0
        self.last_activity_time = 0.0

    def start_work(self):
        self.is_break_active = False
        self.is_waiting_for_return = False
        self.work_start_time = time.time()

    def start_break(self):
        self.is_break_active = True
        self.is_waiting_for_return = False
        self.reset_activity_timer()

    def set_waiting_for_return(self):
        """State after break finishes but before user returns."""
        self.is_break_active = False
        self.is_waiting_for_return = True

    def reset_activity_timer(self):
        self.last_activity_time = time.time()

    def get_remaining_work_time(self):
        if self.is_waiting_for_return:
            return self.work_duration_sec
        elapsed = time.time() - self.work_start_time
        return max(0, self.work_duration_sec - elapsed)

    def get_remaining_break_time(self):
        idle_time = time.time() - self.last_activity_time
        return max(0, self.break_idle_duration_sec - idle_time)

    def is_break_complete(self):
        return self.get_remaining_break_time() <= 0

    def validate_password(self, input_pwd):
        return input_pwd == self.password
