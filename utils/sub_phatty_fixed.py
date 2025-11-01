#!/usr/bin/env python3
"""
Sub Phatty Controller - Korrekt version med rätta CC-nummer
Baserat på officiell MIDI-implementation
"""

import mido
import sys

def main():
    print("=== Sub Phatty Controller (Korrigerad version) ===\n")
    
    # Anslut till Sub Phatty
    try:
        output_ports = mido.get_output_names()
        sub_phatty_port = None
        
        for port in output_ports:
            if 'sub phatty' in port.lower() or 'moog' in port.lower():
                sub_phatty_port = port
                break
        
        if not sub_phatty_port:
            print("Ingen Sub Phatty hittad!")
            print("Tillgängliga portar:", output_ports)
            return
        
        midi_out = mido.open_output(sub_phatty_port)
        print(f"✅ Ansluten till: {sub_phatty_port}\n")
        
    except Exception as e:
        print(f"MIDI-fel: {e}")
        return
    
    # Korrekt CC-nummer från officiell dokumentation
    MODULATION_SOURCE_CC = 71  # "LFO Wave Shape"
    VCO1_OCTAVE_CC = 74        # VCO 1 Octave
    
    print("=== Kommandon (baserat på officiell MIDI-spec) ===")
    print("Modulation Source (påverkar LFO-typ som används för modulering):")
    print("  m0 = Triangle LFO")
    print("  m1 = Square LFO") 
    print("  m2 = Saw LFO")
    print("  m3 = Ramp LFO")
    print("  m4 = S&H (Sample & Hold)")
    print("  m5 = Filter Envelope")
    print("")
    print("VCO 1 Octave:")
    print("  v0 = 16' (lägst)")
    print("  v1 = 8' (normal)")
    print("  v2 = 4' (högre)")
    print("  v3 = 2' (högst)")
    print("  q = Avsluta")
    print()
    
    # Värden enligt MIDI-spec
    mod_source_values = [0, 16, 32, 48, 64, 80]
    mod_source_names = ["Triangle LFO", "Square LFO", "Saw LFO", "Ramp LFO", "S&H", "Filter Envelope"]
    
    vco_octave_values = [16, 32, 48, 64]
    vco_octave_names = ["16'", "8'", "4'", "2'"]
    
    while True:
        try:
            cmd = input("Sub Phatty> ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd.startswith('m') and len(cmd) == 2 and cmd[1].isdigit():
                # Modulation Source
                idx = int(cmd[1])
                if 0 <= idx <= 5:
                    value = mod_source_values[idx]
                    msg = mido.Message('control_change', channel=0, control=MODULATION_SOURCE_CC, value=value)
                    midi_out.send(msg)
                    print(f"✅ Modulation Source: {mod_source_names[idx]} (CC {MODULATION_SOURCE_CC} = {value})")
                else:
                    print("✗ Modulation Source: 0-5")
            elif cmd.startswith('v') and len(cmd) == 2 and cmd[1].isdigit():
                # VCO 1 Octave
                idx = int(cmd[1])
                if 0 <= idx <= 3:
                    value = vco_octave_values[idx]
                    msg = mido.Message('control_change', channel=0, control=VCO1_OCTAVE_CC, value=value)
                    midi_out.send(msg)
                    print(f"✅ VCO 1 Octave: {vco_octave_names[idx]} (CC {VCO1_OCTAVE_CC} = {value})")
                else:
                    print("✗ VCO 1 Octave: 0-3")
            else:
                print("✗ Okänt kommando. Använd m0-m5, v0-v3, eller q")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"✗ Fel: {e}")
    
    # Stäng anslutning
    midi_out.close()
    print("MIDI-anslutning stängd")

if __name__ == "__main__":
    main()