#!/usr/bin/env python3
"""
Sub Phatty Controller - Förbättrad sändningsmetod
Skickar meddelanden flera gånger för att säkerställa att de fastnar
"""

import mido
import time

def send_parameter_secure(midi_out, cc_number, value, repetitions=3, delay=0.1):
    """Skicka MIDI-parameter flera gånger för säkerhet"""
    for i in range(repetitions):
        msg = mido.Message('control_change', channel=0, control=cc_number, value=value)
        midi_out.send(msg)
        if i < repetitions - 1:  # Ingen delay efter sista meddelandet
            time.sleep(delay)
    return True

def main():
    print("=== Sub Phatty Controller (Säker sändning) ===\n")
    
    # Anslut
    try:
        output_ports = mido.get_output_names()
        sub_phatty_port = None
        
        for port in output_ports:
            if 'sub phatty' in port.lower() or 'moog' in port.lower():
                sub_phatty_port = port
                break
        
        if not sub_phatty_port:
            print("Ingen Sub Phatty hittad!")
            return
        
        midi_out = mido.open_output(sub_phatty_port)
        print(f"✅ Ansluten till: {sub_phatty_port}\n")
        
    except Exception as e:
        print(f"MIDI-fel: {e}")
        return
    
    # MIDI CC-nummer
    MODULATION_SOURCE_CC = 71
    VCO1_OCTAVE_CC = 74
    
    # Värden
    mod_source_values = [0, 16, 32, 48, 64, 80]
    mod_source_names = ["Triangle LFO", "Square LFO", "Saw LFO", "Ramp LFO", "S&H", "Filter Envelope"]
    
    vco_octave_values = [16, 32, 48, 64]
    vco_octave_names = ["16'", "8'", "4'", "2'"]
    
    print("=== Kommandon (säker sändning - 3x repetition) ===")
    print("Modulation Source:")
    for i, name in enumerate(mod_source_names):
        print(f"  m{i} = {name}")
    print("\nVCO 1 Octave:")
    for i, name in enumerate(vco_octave_names):
        print(f"  v{i} = {name}")
    print("  q = Avsluta")
    print()
    
    while True:
        try:
            cmd = input("Sub Phatty> ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd.startswith('m') and len(cmd) == 2 and cmd[1].isdigit():
                idx = int(cmd[1])
                if 0 <= idx <= 5:
                    value = mod_source_values[idx]
                    print(f"🔄 Skickar Modulation Source: {mod_source_names[idx]} (3x repetition)...")
                    send_parameter_secure(midi_out, MODULATION_SOURCE_CC, value)
                    print(f"✅ Klart! CC {MODULATION_SOURCE_CC} = {value}")
                else:
                    print("✗ Modulation Source: 0-5")
            elif cmd.startswith('v') and len(cmd) == 2 and cmd[1].isdigit():
                idx = int(cmd[1])
                if 0 <= idx <= 3:
                    value = vco_octave_values[idx]
                    print(f"🔄 Skickar VCO 1 Octave: {vco_octave_names[idx]} (3x repetition)...")
                    send_parameter_secure(midi_out, VCO1_OCTAVE_CC, value)
                    print(f"✅ Klart! CC {VCO1_OCTAVE_CC} = {value}")
                else:
                    print("✗ VCO 1 Octave: 0-3")
            else:
                print("✗ Okänt kommando")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"✗ Fel: {e}")
    
    midi_out.close()
    print("\nMIDI-anslutning stängd")

if __name__ == "__main__":
    main()