from AppKit import NSApplication, NSEvent, NSEventMaskAny
from PyObjCTools import AppHelper
from Foundation import NSObject
from model import BreakModel
from controller import BreakController

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        self.model = BreakModel()
        self.controller = BreakController.alloc().initWithModel_(self.model)
        
        # Global local event monitor
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
