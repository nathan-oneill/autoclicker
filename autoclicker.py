#################################### MODULES ##################################
from pynput import keyboard, mouse
import time

kbController = keyboard.Controller()
mController = mouse.Controller()

# Old Programs in windows: 
import ctypes
import sys
PROCESS_PER_MONITOR_DPI_AWARE = 2



################################### SUPPORT ###################################
def mouseNameToButton(name):
    """Return the appropriate button object for `name`"""
    if name == 'left': return mouse.Button.left
    if name == 'right': return mouse.Button.right
    if name == 'middle': return mouse.Button.middle
    raise NotImplementedError('unkown name')

def waitUntilKeyPressed(key):
    """Pause execution until `key` is pressed."""
    print('Waiting until key pressed: {}'.format(key))
    def _waitUntilKeyPressed(eventKey):
        if eventKey == key:
            print('Finished waiting')
            return False

    with keyboard.Listener(on_press=_waitUntilKeyPressed) as kbListener:
        kbListener.join()
    return

def supportOldWindowsPrograms(process_per_monitor_dpi_aware = PROCESS_PER_MONITOR_DPI_AWARE):
    """https://pynput.readthedocs.io/en/latest/mouse.html#ensuring-consistent-coordinates-between-listener-and-controller-on-windows"""
    ctypes.windll.shcore.SetProcessDpiAwareness(process_per_monitor_dpi_aware)
    return



################################## RECORDING ##################################
class Record:
    events  = None
    stopKey = None
    keyboardListener = None
    mouseListener = None

    @classmethod
    def start(cls, waitForKey: keyboard.Key | None = keyboard.Key.esc, stopKey = keyboard.Key.esc):
        """Start recording a sequence."""
        print('Recording initiated')
        # Stop and start conditions
        cls.stopKey = stopKey
        if waitForKey is not None:
            waitUntilKeyPressed(waitForKey)
        
        # Event recording
        cls.events = [
            {'currentTime': time.time()} # Initialised with dummy event
        ]
        # no good way to lint the following statement?
        with keyboard.Listener(on_press=cls._keyPress) as kbListener, mouse.Listener(on_click=cls._mouseClick, on_scroll=cls._mouseScroll) as mListener:
            cls.keyboardListener = kbListener
            cls.mouseListener = mListener
            kbListener.join()
            mListener.join()
        return

    @classmethod
    def stop(cls):
        """Stop recording the sequence, and print to it to console."""
        # Clean class memory
        cls.keyboardListener.stop()
        cls.mouseListener.stop()
        cls.keyboardListener = None
        cls.mouseListener = None
        events = cls.events
        cls.events = None
        cls.stopKey = None

        # Clean event data
        events.pop(0) # Remove dummy event
        for e in events: 
            del e['currentTime']
            if e['type'] == 'mouseClick': e['button'] = e['button'].name
        print('\nrecorded events:')
        print(events)
        print()
        return events

    @classmethod
    def _keyPress(cls, key):
        currentTime = time.time()
        if key == cls.stopKey:
            cls.stop()
            return

        cls.events.append({
            'type': 'keyPress', 
            'key': key, 
            'delay': currentTime - cls.events[-1]['currentTime'],
            'currentTime': currentTime
        })
        return
    
    @classmethod
    def _mouseClick(cls, x, y, button, pressed):
        currentTime = time.time()
        cls.events.append({
            'type': 'mouseClick',
            'x': x,
            'y': y,
            'button': button,
            'pressed': pressed,
            'delay': currentTime - cls.events[-1]['currentTime'],
            'currentTime': currentTime
        })
        return
    
    @classmethod
    def _mouseScroll(cls, x, y, dx, dy):
        currentTime = time.time()
        cls.events.append({
            'type': 'mouseClick',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'delay': currentTime - cls.events[-1]['currentTime'],
            'currentTime': currentTime
        })
        return



################################### PLAYBACK ##################################
class EmergencyExit:
    _listener = None

    @classmethod
    def listen(cls, callback, stopKey = keyboard.Key.esc):
        """Start listening for an emergency exit on any key pressed."""
        if not isinstance(stopKey, keyboard.Key):
            print('ERR: stopKey must be a valid key')
            return

        if cls._listener is not None:
            # Ensure only 1 listener is ever present.
            cls._listener.stop()
        cls._listener = keyboard.Listener(on_press=cls._trigger(callback, stopKey))
        cls._listener.start()
        return
        
    @staticmethod
    def _trigger(callback, stopKey):
        """Returns an appropriate listener function."""
        def _onPress(key):
            if key == stopKey:
                print('Emergency Exit triggered')
                callback()
                return False # Turn off listener
        return _onPress


class Playback:
    # If I encounter difficulties: https://pynput.readthedocs.io/en/latest/mouse.html#ensuring-consistent-coordinates-between-listener-and-controller-on-windows
    _stopPlayback = False


    @classmethod
    def start(cls, events, N: int = None, timeLength: float = None, 
              waitForKey: keyboard.Key | None = keyboard.Key.esc, stopKey = keyboard.Key.esc):
        """Start macro playback, until `N` repeats or `timeLength` seconds
        passed."""
        if not isinstance(stopKey, keyboard.Key):
            print('ERR: stopKey must be a valid key')
            return

        print('Macro playback initiated')
        if waitForKey is not None:
            waitUntilKeyPressed(waitForKey)
        
        print('Starting macro playback')
        cls._stopPlayback = False
        EmergencyExit.listen(cls._emergencyExit, stopKey)

        repeats = 0
        initialTime = time.time()
        while True:
            if N is not None and repeats >= N: 
                break
            if timeLength is not None and time.time()-initialTime > timeLength:
                break
            for event in events:
                time.sleep(event['delay'])
                if cls._stopPlayback: return
                if event['type'] == 'keyPress': cls._keyPress(event)
                if event['type'] == 'mouseClick': cls._mouseClick(event)
                if event['type'] == 'mouseScroll': cls._mouseScroll(event)
            repeats += 1
        print('Finished macro playback')
        return

    @classmethod
    def _emergencyExit(cls): 
        cls._stopPlayback = True
        return
        
    @staticmethod
    def _keyPress(event): 
        kbController.press(event['key'])
        return
    
    @staticmethod
    def _mouseClick(event):
        mController.position = (event['x'], event['y'])
        button = mouseNameToButton(event['button'])
        if event['pressed']:
            mController.press(button)
        else:
            mController.release(button)
        return

    @staticmethod
    def _mouseScroll(event):
        mController.scroll(event['dx'], event['dy'])
        


###############################################################################
if __name__ == '__main__':
    if sys.argv[1] == 'supportOldWindows':
        supportOldWindowsPrograms()

    Record.start()
    # data = <COPY HERE>
    # Playback.start(data)