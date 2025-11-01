# Sub Phatty Controller

A simple Python application to control LFO Wave Shape and VCO 1 Octave on your Moog Sub Phatty via MIDI when physical switches are broken.

## Features

- **6 LFO Wave Forms**: Triangle, Square, Saw, Ramp, Sample & Hold, Filter Envelope
- **4 VCO Octaves**: 16', 8', 4', 2' (correctly mapped according to MIDI spec)
- **LFO Rate Control**: Real-time slider control (CC #3, values 0-127)
- **Web-based GUI**: Works on Mac, iPhone, iPad - any device with a browser
- **Command-line Interface**: Quick commands for fast adjustments
- **Mobile Optimized**: Touch-friendly interface for live performance

## Installation

### 1. Install Python Dependencies
Open Terminal and navigate to this folder, then run:

```bash
pip3 install -r requirements.txt
```

### 2. Connect Sub Phatty
- Connect your Sub Phatty to the computer via USB
- Make sure it's powered on and recognized as a MIDI device

### 3. Run the Application

**Web Interface (Recommended):**
```bash
python3 sub_phatty_web.py
```
Then open: http://localhost:8080 (or the IP address shown for mobile access)

**Command Line Interface:**
```bash
python3 sub_phatty_final.py
```

## Usage

### Web Interface
The web application provides:

#### LFO Wave Shape Buttons
- **Triangle**: Triangle wave
- **Square**: Square wave  
- **Saw**: Sawtooth wave
- **Ramp**: Ramp wave (reverse sawtooth)
- **Sample & Hold**: Random stepped values
- **Filter Envelope**: Uses filter envelope as LFO source

#### LFO Rate Slider
- **Range**: 0-127 (Slow → Fast)
- **Real-time**: Immediate response and value display
- **Touch-friendly**: Optimized for mobile devices

#### VCO 1 Octave Buttons
- **16'**: One octave lower
- **8'**: Normal pitch
- **4'**: One octave higher  
- **2'**: Two octaves higher

### Command Line Interface

**Quick Commands:**
```bash
python3 sub_phatty_final.py lfo triangle    # Set LFO to triangle wave
python3 sub_phatty_final.py lfo square      # Set LFO to square wave
python3 sub_phatty_final.py lfo ramp        # Set LFO to ramp wave
python3 sub_phatty_final.py lfo filter_env  # Set LFO to filter envelope
python3 sub_phatty_final.py vco 16          # Set VCO to 16' octave
python3 sub_phatty_final.py vco 2           # Set VCO to 2' octave
python3 sub_phatty_final.py help            # Show help
```

**Interactive Mode:**
```bash
python3 sub_phatty_final.py
```

### Mobile Access
1. Start the web server on your Mac
2. Note the IP address shown (e.g., http://192.168.68.81:8080)
3. Open that address on your iPhone/iPad browser
4. Control your Sub Phatty remotely!

## Troubleshooting

### "No MIDI ports found"

- Check that Sub Phatty is connected and powered on
- Try unplugging and reconnecting the USB cable
- Restart the application

### "MIDI connection error"

- Close Moog Sub Phatty Editor if running (only one application can use the MIDI port at a time)
- Click "Reconnect MIDI" in the web interface
- Check that the Sub Phatty is recognized by your system

### Settings don't change on the synthesizer

- Verify that Sub Phatty is set to MIDI channel 2 (this app uses channel 2, same as Sub Phatty Editor)
- Ensure MIDI over USB is enabled on the synthesizer
- Try power cycling the Sub Phatty

### Web interface won't load

- Make sure no other application is using port 8080
- Check your firewall settings
- For mobile access, ensure both devices are on the same WiFi network

## Technical MIDI Details

This application uses the following MIDI Control Change (CC) messages according to the official Moog Sub Phatty MIDI Implementation:

- **LFO Wave Shape**: CC #71
  - Triangle: 0, Square: 16, Saw: 32, Ramp: 48, Sample & Hold: 64, Filter Envelope: 80
- **LFO Rate**: CC #3 (values 0-127)
- **VCO 1 Octave**: CC #74
  - 16': 16, 8': 32, 4': 48, 2': 64

All messages are sent on **MIDI channel 2** (same as Sub Phatty Editor).

## Why This Project Exists

Physical switches on analog synthesizers can break over time. Rather than expensive repairs, this software solution provides:

- **Better functionality** than original switches (LFO rate control, more wave shapes)
- **Remote control** capability (perfect for live performance)
- **Reliability** - software doesn't wear out like mechanical switches
- **Mobile access** - control from phone/tablet while playing

## Project Structure

### Main Files (Required for Operation)

- `sub_phatty_web.py` - Web-based GUI controller (recommended)
- `sub_phatty_final.py` - Command-line interface
- `midi-implementation.csv` - Official Moog MIDI specification
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

### Utils Directory

The `utils/` directory contains development tools, debug utilities, and test files used during project development. These are not needed for normal operation but can be useful for debugging or extending functionality.

See `utils/README.md` for detailed information about these tools.