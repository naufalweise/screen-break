import time
from Foundation import NSObject, NSTimer
from view import BreakView

class BreakController(NSObject):
    def initWithModel_(self, model):
        self = super().init()
        if self:
            self.model = model
            self.view = BreakView.alloc().initWithController_(self)
            self.main_tick_timer = None
        return self

    def start(self):
        # Initially wait for user return to start the first work cycle
        self.model.set_waiting_for_return()
        self.view.showStatusWindow()
        self.view.updateWorkTimer_("Waiting for Activity...")
        
        self.main_tick_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0, self, "tick:", None, True
        )

    def tick_(self, timer):
        if self.model.is_break_active:
            rem = int(self.model.get_remaining_break_time())
            self.view.updateBreakTimer_(f"Required Inactivity: {rem}s")
            if self.model.is_break_complete():
                self.endBreak()
        elif self.model.is_waiting_for_return:
            self.view.updateWorkTimer_("Waiting for Activity...")
        else:
            rem = int(self.model.get_remaining_work_time())
            mins, secs = divmod(rem, 60)
            self.view.updateWorkTimer_(f"Screen Time: {mins:02d}:{secs:02d}")
            if rem <= 0:
                self.triggerBreak()

    def triggerBreak(self):
        print(f"[{time.strftime('%H:%M:%S')}] Break triggered.")
        self.view.playStartSound()
        self.model.start_break()
        self.view.showOverlay()

    def onPasswordSubmit_(self, password):
        if self.model.validate_password(password):
            self.endBreak()
        else:
            self.view.password_field.setStringValue_("")

    def endBreak(self):
        print(f"[{time.strftime('%H:%M:%S')}] Break ended.")
        self.view.playEndSound()
        self.model.set_waiting_for_return()
        self.view.hideOverlay()
        self.view.showStatusWindow()

    def handleEvent_(self, event):
        if self.model.is_break_active:
            self.model.reset_activity_timer()
        elif self.model.is_waiting_for_return:
            # User has returned, start the work clock
            print(f"[{time.strftime('%H:%M:%S')}] User returned. Work cycle started.")
            self.model.start_work()
