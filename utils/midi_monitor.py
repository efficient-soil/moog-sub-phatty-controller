#!/usr/bin/env python3
"""
MIDI Monitor för Sub Phatty
Lyssnar på MIDI-trafik för att se vad Sub Phatty Editor skickar
"""

import mido
import time
from threading import Thread

class MIDIMonitor:
    def __init__(self):
        self.monitoring = False
        self.midi_in = None
        self.midi_out = None
        
    def list_ports(self):
        """Lista alla MIDI-portar"""
        print("=== MIDI-portar ===")
        
        input_ports = mido.get_input_names()
        output_ports = mido.get_output_names()
        
        print("Ingångar:")
        for i, port in enumerate(input_ports):
            print(f"  {i}: {port}")
        
        print("\nUtgångar:")
        for i, port in enumerate(output_ports):
            print(f"  {i}: {port}")
        
        return input_ports, output_ports
    
    def start_monitoring(self, input_port_name):
        """Starta MIDI-monitoring"""
        try:
            self.midi_in = mido.open_input(input_port_name)
            self.monitoring = True
            print(f"🎧 Lyssnar på MIDI från: {input_port_name}")
            print("Starta Sub Phatty Editor och ändra parametrar...")
            print("Tryck Ctrl+C för att stoppa\n")
            
            # Lyssna på meddelanden
            for message in self.midi_in:
                if not self.monitoring:
                    break
                    
                # Formatera meddelandet för läsbarhet
                self.format_message(message)
                
        except Exception as e:
            print(f"Fel vid monitoring: {e}")
        finally:
            if self.midi_in:
                self.midi_in.close()
    
    def format_message(self, msg):
        """Formatera MIDI-meddelande för läsbarhet"""
        timestamp = time.strftime("%H:%M:%S")
        
        if msg.type == 'control_change':
            print(f"[{timestamp}] CC: Kanal {msg.channel + 1}, CC #{msg.control}, Värde {msg.value}")
            
            # Specialformat för kända Sub Phatty CC:s
            if msg.control == 71:
                mod_names = {0: "Triangle LFO", 16: "Square LFO", 32: "Saw LFO", 
                           48: "Ramp LFO", 64: "S&H", 80: "Filter Envelope"}
                if msg.value in mod_names:
                    print(f"    → Modulation Source: {mod_names[msg.value]}")
                    
            elif msg.control == 74:
                oct_names = {16: "16'", 32: "8'", 48: "4'", 64: "2'"}
                if msg.value in oct_names:
                    print(f"    → VCO 1 Octave: {oct_names[msg.value]}")
                    
        elif msg.type == 'program_change':
            print(f"[{timestamp}] Program Change: Kanal {msg.channel + 1}, Preset {msg.program}")
            
        elif msg.type == 'sysex':
            hex_data = ' '.join([f'{b:02X}' for b in msg.data])
            print(f"[{timestamp}] SysEx: {hex_data}")
            
            # Försök tolka Moog SysEx
            if len(msg.data) >= 3 and msg.data[0] == 0x04:  # Moog manufacturer ID
                print(f"    → Moog SysEx detected!")
                
        elif msg.type in ['note_on', 'note_off']:
            print(f"[{timestamp}] {msg.type}: Kanal {msg.channel + 1}, Not {msg.note}, Velocity {msg.velocity}")
            
        else:
            print(f"[{timestamp}] {msg.type}: {msg}")
    
    def stop_monitoring(self):
        """Stoppa monitoring"""
        self.monitoring = False

def send_test_messages():
    """Skicka test-meddelanden till Sub Phatty"""
    try:
        output_ports = mido.get_output_names()
        sub_phatty_port = None
        
        for port in output_ports:
            if 'sub phatty' in port.lower() or 'moog' in port.lower():
                sub_phatty_port = port
                break
        
        if not sub_phatty_port:
            print("Ingen Sub Phatty utgång hittad för test")
            return
        
        midi_out = mido.open_output(sub_phatty_port)
        
        print("\n=== Skickar testmeddelanden ===")
        
        # Test CC-meddelanden
        test_messages = [
            ("VCO 1 Octave 16'", 'control_change', {'channel': 0, 'control': 74, 'value': 16}),
            ("VCO 1 Octave 8'", 'control_change', {'channel': 0, 'control': 74, 'value': 32}),
            ("Modulation Source Triangle", 'control_change', {'channel': 0, 'control': 71, 'value': 0}),
            ("Modulation Source Square", 'control_change', {'channel': 0, 'control': 71, 'value': 16}),
        ]
        
        for desc, msg_type, kwargs in test_messages:
            print(f"Skickar: {desc}")
            msg = mido.Message(msg_type, **kwargs)
            midi_out.send(msg)
            time.sleep(1)
        
        midi_out.close()
        print("Test slutfört")
        
    except Exception as e:
        print(f"Fel vid test: {e}")

def main():
    monitor = MIDIMonitor()
    
    print("=== Sub Phatty MIDI Monitor ===")
    print("Detta verktyg hjälper oss förstå hur Sub Phatty Editor kommunicerar\n")
    
    input_ports, output_ports = monitor.list_ports()
    
    # Leta efter Sub Phatty input port
    sub_phatty_input = None
    for port in input_ports:
        if 'sub phatty' in port.lower() or 'moog' in port.lower():
            sub_phatty_input = port
            break
    
    if not sub_phatty_input:
        print("\n❌ Ingen Sub Phatty input-port hittad!")
        print("Kontrollera att Sub Phatty är ansluten och påslagen.")
        return
    
    print(f"\n✅ Hittade Sub Phatty input: {sub_phatty_input}")
    
    print("\n=== Instruktioner ===")
    print("1. Starta detta program")
    print("2. Öppna Sub Phatty Editor i ett annat fönster") 
    print("3. Ändra LFO Wave och VCO 1 Octave i editorn")
    print("4. Se vilka MIDI-meddelanden som skickas här")
    print("5. Tryck Ctrl+C för att stoppa")
    
    input("\nTryck Enter för att börja lyssna...")
    
    try:
        # Starta test-sändning i bakgrunden efter en stund
        test_thread = Thread(target=lambda: (time.sleep(3), send_test_messages()), daemon=True)
        test_thread.start()
        
        # Starta monitoring
        monitor.start_monitoring(sub_phatty_input)
        
    except KeyboardInterrupt:
        print("\n\nMonitoring stoppad")
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()