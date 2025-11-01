#!/usr/bin/env python3
"""
Sub Phatty - Program Change Test
Testar om Program Change fungerar bättre än Control Change
"""

import mido
import time

def main():
    print("=== Sub Phatty Program Change Test ===")
    print("Testar om preset-byte fungerar bättre än CC-meddelanden\n")
    
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
    
    print("=== Kommandon ===")
    print("p0-p127 = Byt till preset 0-127")
    print("cc      = Testa CC-meddelanden (som tidigare)")  
    print("q       = Avsluta")
    print()
    
    while True:
        try:
            cmd = input("Sub Phatty> ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd.startswith('p') and cmd[1:].isdigit():
                preset_num = int(cmd[1:])
                if 0 <= preset_num <= 127:
                    print(f"🔄 Byter till preset {preset_num}...")
                    msg = mido.Message('program_change', channel=0, program=preset_num)
                    midi_out.send(msg)
                    print(f"✅ Program Change skickat: Preset {preset_num}")
                else:
                    print("✗ Preset måste vara 0-127")
            elif cmd == 'cc':
                print("Testar CC-meddelanden...")
                print("VCO 1 Octave CC 74: 16 -> 32 -> 48 -> 64")
                for value in [16, 32, 48, 64]:
                    msg = mido.Message('control_change', channel=0, control=74, value=value)
                    midi_out.send(msg)
                    print(f"  Skickade CC 74 = {value}")
                    time.sleep(1)
            else:
                print("✗ Okänt kommando")
                
        except KeyboardInterrupt:
            break
        except ValueError:
            print("✗ Använd siffror för preset-nummer")
        except Exception as e:
            print(f"✗ Fel: {e}")
    
    midi_out.close()
    print("\nMIDI-anslutning stängd")

if __name__ == "__main__":
    main()