# Utils Directory

This directory contains development tools, debug utilities, and test files used during the creation of the Sub Phatty Controller. These files are not needed for normal operation.

## Development Tools

- `midi_monitor.py` - MIDI traffic analyzer (key tool for discovering correct MIDI channel)
- `sysex_analyzer.py` - System Exclusive message analyzer
- `midi_debug.py` - General MIDI debugging utilities

## Test Files

- `test_channel2_simple.py` - Simple test for MIDI channel 2 (breakthrough discovery)
- `test_program_change.py` - Program change testing
- `sub_phatty_channel2_test.py` - Channel 2 specific testing

## Development Versions

- `sub_phatty_controller.py` - Original tkinter-based GUI (failed on macOS)
- `sub_phatty_gui.py` - Tkinter GUI attempt (compatibility issues)
- `sub_phatty_simple.py` - Early simple version
- `sub_phatty_fixed.py` - Intermediate version with fixes
- `sub_phatty_persistent.py` - Version testing persistence issues
- `sub_phatty_secure.py` - Security testing version
- `sub_phatty_sysex_controller.py` - SysEx-based approach (abandoned)


## Usage

These tools can be useful if you want to:
- Debug MIDI issues
- Analyze MIDI traffic from other applications
- Understand how the project evolved
- Extend functionality with additional MIDI controls

To run any of these files:
```bash
cd utils
python3 filename.py
```