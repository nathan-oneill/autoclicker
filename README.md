# `autoclicker`
Python autoclicker using [`pynput`](https://pypi.org/project/pynput/).


# Instructions
(See each function's documentation for options on the playback.)
1. `Record.start()` to record a macro. It will print the recorded events to the console.
2. Copy & paste the data into the python script
3. Use `Playback.start(data)` to replay the macro.

## Old Windows Programs
Some old windows programs get scaled and behaviour isn't (by default) consistent. See [here](https://pynput.readthedocs.io/en/latest/mouse.html#ensuring-consistent-coordinates-between-listener-and-controller-on-windows). To make it consistent, add the CLI argument `supportOldWindows`:

```python autoclicker.py supportOldWindows```