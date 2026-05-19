import time
import threading
from Foundation import NSObject, NSTimer, NSRunLoop, NSDate
from AppKit import (
    NSApplication, NSApp, NSWindow, NSScreen, 
    NSColor, NSFont, NSTextField, NSSecureTextField,
    NSWindowStyleMaskBorderless, NSBackingStoreBuffered,
    NSCenterTextAlignment, NSFocusRingTypeNone
)
from PyObjCTools import AppHelper

# ==========================================
# CONFIGURATION CONSTANTS
# ==========================================
WORK_DURATION_MIN = 1
BREAK_DURATION_SEC = 60
PASSWORD = "sjflajfljajf;s-032rn"

# ==========================================
# MODEL: Data and Business Logic
# ==========================================
class BreakModel:
    def __init__(self):
        self.work_duration_sec = WORK_DURATION_MIN * 60
        self.break_idle_duration_sec = BREAK_DURATION_SEC
        self.password = PASSWORD
        
        self.is_break_active = False
        self.work_start_time = 0.0
        self.last_activity_time = 0.0

    def start_work(self):
        self.is_break_active = False
        self.work_start_time = time.time()

    def start_break(self):
        self.is_break_active = True
        self.reset_activity_timer()

    def reset_activity_timer(self):
        self.last_activity_time = time.time()

    def get_remaining_work_time(self):
        elapsed = time.time() - self.work_start_time
        return max(0, self.work_duration_sec - elapsed)

    def get_remaining_break_time(self):
        idle_time = time.time() - self.last_activity_time
        return max(0, self.break_idle_duration_sec - idle_time)

    def is_break_complete(self):
        return self.get_remaining_break_time() <= 0

    def validate_password(self, input_pwd):
        return input_pwd == self.password


# ==========================================
# VIEW: Cocoa Overlay & Status
# ==========================================
class BreakWindow(NSWindow):
    def canBecomeKeyWindow(self):
        return True
    
    def canBecomeMainWindow(self):
        return True

class BreakView(NSObject):
    def initWithController_(self, controller):
        self = super().init()
        if self:
            self.controller = controller
            self.overlay_window = None
            self.status_window = None
            self.password_field = None
            self.break_timer_label = None
            self.work_timer_label = None
        return self

    def showStatusWindow(self):
        """Shows a small floating window with the remaining screen time."""
        if self.status_window: return
        
        screen_frame = NSScreen.mainScreen().frame()
        # Position at top right
        width, height = 200, 40
        rect = ((screen_frame.size.width - width - 20, screen_frame.size.height - height - 40), (width, height))
        
        self.status_window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False
        )
        self.status_window.setBackgroundColor_(NSColor.blackColor())
        self.status_window.setAlphaValue_(0.7)
        self.status_window.setLevel_(1000)
        self.status_window.setCanHide_(False)
        
        self.work_timer_label = NSTextField.alloc().initWithFrame_(((0, 0), (width, height)))
        self.work_timer_label.setStringValue_("Screen Time: --:--")
        self.work_timer_label.setFont_(NSFont.systemFontOfSize_(14))
        self.work_timer_label.setTextColor_(NSColor.whiteColor())
        self.work_timer_label.setEditable_(False)
        self.work_timer_label.setBezeled_(False)
        self.work_timer_label.setDrawsBackground_(False)
        self.work_timer_label.setAlignment_(NSCenterTextAlignment)
        
        self.status_window.contentView().addSubview_(self.work_timer_label)
        self.status_window.makeKeyAndOrderFront_(None)

    def updateWorkTimer_(self, text):
        if self.work_timer_label:
            self.work_timer_label.setStringValue_(text)

    def showOverlay(self):
        """Shows the fullscreen break overlay."""
        if self.status_window:
            self.status_window.orderOut_(None)
            self.status_window = None

        screen_frame = NSScreen.mainScreen().frame()
        self.overlay_window = BreakWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            screen_frame, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False
        )
        
        self.overlay_window.setBackgroundColor_(NSColor.blackColor())
        self.overlay_window.setAlphaValue_(0.95)
        self.overlay_window.setLevel_(1001)
        self.overlay_window.setCanHide_(False)
        self.overlay_window.setHidesOnDeactivate_(False)
        
        content_view = self.overlay_window.contentView()
        
        # Title
        title = NSTextField.alloc().initWithFrame_(((0, screen_frame.size.height/2 + 100), (screen_frame.size.width, 100)))
        title.setStringValue_("TIME FOR A BREAK")
        title.setFont_(NSFont.boldSystemFontOfSize_(64))
        title.setTextColor_(NSColor.systemRedColor())
        title.setEditable_(False)
        title.setBezeled_(False)
        title.setDrawsBackground_(False)
        title.setAlignment_(NSCenterTextAlignment)
        content_view.addSubview_(title)

        # Break Timer Label
        self.break_timer_label = NSTextField.alloc().initWithFrame_(((0, screen_frame.size.height/2 + 40), (screen_frame.size.width, 40)))
        self.break_timer_label.setStringValue_("Required Inactivity: --s")
        self.break_timer_label.setFont_(NSFont.systemFontOfSize_(24))
        self.break_timer_label.setTextColor_(NSColor.systemOrangeColor())
        self.break_timer_label.setEditable_(False)
        self.break_timer_label.setBezeled_(False)
        self.break_timer_label.setDrawsBackground_(False)
        self.break_timer_label.setAlignment_(NSCenterTextAlignment)
        content_view.addSubview_(self.break_timer_label)

        # Instruction
        inst = NSTextField.alloc().initWithFrame_(((0, screen_frame.size.height/2 - 40), (screen_frame.size.width, 60)))
        inst.setStringValue_("Look away from the screen.\nAny movement will reset the timer.")
        inst.setFont_(NSFont.systemFontOfSize_(18))
        inst.setTextColor_(NSColor.whiteColor())
        inst.setEditable_(False)
        inst.setBezeled_(False)
        inst.setDrawsBackground_(False)
        inst.setAlignment_(NSCenterTextAlignment)
        content_view.addSubview_(inst)

        # Password Field
        field_width = 300
        self.password_field = NSSecureTextField.alloc().initWithFrame_(
            ((screen_frame.size.width/2 - field_width/2, screen_frame.size.height/2 - 150), (field_width, 40))
        )
        self.password_field.setBezeled_(True)
        self.password_field.setBezelStyle_(1)
        self.password_field.setFocusRingType_(NSFocusRingTypeNone)
        self.password_field.setAlignment_(NSCenterTextAlignment)
        self.password_field.setFont_(NSFont.systemFontOfSize_(20))
        self.password_field.setTarget_(self)
        self.password_field.setAction_("onPasswordSubmit:")
        content_view.addSubview_(self.password_field)

        self.overlay_window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def hideOverlay(self):
        if self.overlay_window:
            self.overlay_window.orderOut_(None)
            self.overlay_window = None

    def updateBreakTimer_(self, text):
        if self.break_timer_label:
            self.break_timer_label.setStringValue_(text)

    def onPasswordSubmit_(self, sender):
        password = sender.stringValue()
        self.controller.onPasswordSubmit_(password)

# ==========================================
# CONTROLLER: Orchestration
# ==========================================
class BreakController(NSObject):
    def initWithModel_(self, model):
        self = super().init()
        if self:
            self.model = model
            self.view = BreakView.alloc().initWithController_(self)
            self.main_tick_timer = None
        return self

    def start(self):
        self.model.start_work()
        self.view.showStatusWindow()
        # Single timer to handle all updates (1Hz)
        self.main_tick_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0, self, "tick:", None, True
        )

    def tick_(self, timer):
        if self.model.is_break_active:
            # Handle Break Logic
            rem = int(self.model.get_remaining_break_time())
            self.view.updateBreakTimer_(f"Required Inactivity: {rem}s")
            
            if self.model.is_break_complete():
                print(f"[{time.strftime('%H:%M:%S')}] Break complete.")
                self.endBreak()
        else:
            # Handle Work Logic
            rem = int(self.model.get_remaining_work_time())
            mins, secs = divmod(rem, 60)
            self.view.updateWorkTimer_(f"Screen Time: {mins:02d}:{secs:02d}")
            
            if rem <= 0:
                self.triggerBreak()

    def triggerBreak(self):
        print(f"[{time.strftime('%H:%M:%S')}] Break time triggered!")
        self.model.start_break()
        self.view.showOverlay()

    def onPasswordSubmit_(self, password):
        if self.model.validate_password(password):
            print(f"[{time.strftime('%H:%M:%S')}] Password bypass used.")
            self.endBreak()
        else:
            self.view.password_field.setStringValue_("")

    def endBreak(self):
        self.model.start_work()
        self.view.hideOverlay()
        self.view.showStatusWindow()

    def handleEvent_(self, event):
        if self.model.is_break_active:
            self.model.reset_activity_timer()

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        self.model = BreakModel()
        self.controller = BreakController.alloc().initWithModel_(self.model)
        
        from AppKit import NSEvent, NSEventMaskAny
        self.monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            NSEventMaskAny, self.handleEvent_
        )
        
        self.controller.start()

    def handleEvent_(self, event):
        self.controller.handleEvent_(event)
        return event

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
