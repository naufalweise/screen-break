from Foundation import NSObject
from AppKit import (
    NSWindow, NSScreen, NSColor, NSFont, NSTextField, 
    NSSecureTextField, NSWindowStyleMaskBorderless, 
    NSBackingStoreBuffered, NSCenterTextAlignment, 
    NSFocusRingTypeNone, NSApp, NSSound
)

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
            
            # Pre-load native sounds
            self.start_sound = NSSound.soundNamed_("Glass")
            self.end_sound = NSSound.soundNamed_("Hero")
            
        return self

    def playStartSound(self):
        if self.start_sound: self.start_sound.play()

    def playEndSound(self):
        if self.end_sound: self.end_sound.play()

    def showStatusWindow(self):
        if self.status_window: return
        
        screen_frame = NSScreen.mainScreen().frame()
        width, height = 220, 40
        rect = ((screen_frame.size.width - width - 20, screen_frame.size.height - height - 40), (width, height))
        
        self.status_window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False
        )
        self.status_window.setBackgroundColor_(NSColor.blackColor())
        self.status_window.setAlphaValue_(0.7)
        self.status_window.setLevel_(1000)
        self.status_window.setCanHide_(False)
        
        self.work_timer_label = NSTextField.alloc().initWithFrame_(((0, 0), (width, height)))
        self.work_timer_label.setStringValue_("Ready to Start")
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
        
        title = NSTextField.alloc().initWithFrame_(((0, screen_frame.size.height/2 + 100), (screen_frame.size.width, 100)))
        title.setStringValue_("TIME FOR A BREAK")
        title.setFont_(NSFont.boldSystemFontOfSize_(64))
        title.setTextColor_(NSColor.systemRedColor())
        title.setEditable_(False)
        title.setBezeled_(False)
        title.setDrawsBackground_(False)
        title.setAlignment_(NSCenterTextAlignment)
        content_view.addSubview_(title)

        self.break_timer_label = NSTextField.alloc().initWithFrame_(((0, screen_frame.size.height/2 + 40), (screen_frame.size.width, 40)))
        self.break_timer_label.setStringValue_("Required Inactivity: --s")
        self.break_timer_label.setFont_(NSFont.systemFontOfSize_(24))
        self.break_timer_label.setTextColor_(NSColor.systemOrangeColor())
        self.break_timer_label.setEditable_(False)
        self.break_timer_label.setBezeled_(False)
        self.break_timer_label.setDrawsBackground_(False)
        self.break_timer_label.setAlignment_(NSCenterTextAlignment)
        content_view.addSubview_(self.break_timer_label)

        inst = NSTextField.alloc().initWithFrame_(((0, screen_frame.size.height/2 - 40), (screen_frame.size.width, 60)))
        inst.setStringValue_("Look away from the screen.\nAny movement will reset the timer.")
        inst.setFont_(NSFont.systemFontOfSize_(18))
        inst.setTextColor_(NSColor.whiteColor())
        inst.setEditable_(False)
        inst.setBezeled_(False)
        inst.setDrawsBackground_(False)
        inst.setAlignment_(NSCenterTextAlignment)
        content_view.addSubview_(inst)

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
