#!/usr/bin/env python3
"""
Sub Phatty Simple Controller - Final Version

En enkel MIDI-kontroller för de trasiga switcharna på Moog Sub Phatty.
Använder korrekt MIDI-kanal (kanal 2) baserat på analys av Sub Phatty Editor.
"""

import mido
import sys
import time

class SubPhattySimpleController:
    def __init__(self):
        self.outport = None
        self.midi_channel = 1  # Kanal 2 (0-indexerat)
        
        # CC-nummer från officiella MIDI-specen
        self.lfo_cc = 71       # Modulation Source
        self.vco_cc = 74       # VCO 1 Octave
        
        # Värden från officiella specen
        self.lfo_values = {
            'triangle': 0,
            'square': 16, 
            'saw': 32,
            'ramp': 48,
            'sample_hold': 64,
            'sh': 64,  # förkortning för sample & hold
            'filter_env': 80,
            'env': 80  # förkortning för filter envelope
        }
        
        self.vco_values = {
            '16': 16,    # 16'
            '8': 32,     # 8'
            '4': 48,     # 4'
            '2': 64      # 2'
        }
        
    def connect(self):
        """Anslut till Sub Phatty"""
        output_ports = mido.get_output_names()
        
        for port in output_ports:
            if 'Sub Phatty' in port or 'Moog' in port:
                try:
                    self.outport = mido.open_output(port)
                    print(f"✓ Ansluten till: {port}")
                    return True
                except Exception as e:
                    print(f"✗ Fel vid anslutning till {port}: {e}")
        
        print("✗ Ingen Sub Phatty hittades")
        return False
    
    def send_cc(self, cc_number, value, description=""):
        """Skicka CC-meddelande"""
        if not self.outport:
            print("✗ Ingen MIDI-anslutning")
            return False
            
        try:
            msg = mido.Message('control_change',
                             channel=self.midi_channel,
                             control=cc_number,
                             value=value)
            self.outport.send(msg)
            print(f"✓ Skickat: {description} (CC#{cc_number}={value})")
            return True
        except Exception as e:
            print(f"✗ Fel vid sändning: {e}")
            return False
    
    def set_lfo_wave(self, wave):
        """Sätt LFO våg-form"""
        if wave not in self.lfo_values:
            print(f"✗ Okänd LFO-våg: {wave}")
            print(f"  Giltiga: {list(self.lfo_values.keys())}")
            return False
            
        value = self.lfo_values[wave]
        return self.send_cc(self.lfo_cc, value, f"LFO Wave: {wave}")
    
    def set_vco_octave(self, octave):
        """Sätt VCO 1 oktav"""
        octave = str(octave).replace("'", "")  # Ta bort ' om det finns
        
        if octave not in self.vco_values:
            print(f"✗ Okänd VCO-oktav: {octave}")
            print(f"  Giltiga: {list(self.vco_values.keys())}")
            return False
            
        value = self.vco_values[octave]
        return self.send_cc(self.vco_cc, value, f"VCO Octave: {octave}'")
    
    def interactive_mode(self):
        """Interaktivt läge"""
        print("\n=== Sub Phatty Kontroller ===")
        print("Kommandon:")
        print("  lfo triangle|square|saw|ramp|sample_hold|filter_env")
        print("  vco 16|8|4|2") 
        print("  quit")
        print()
        
        while True:
            try:
                cmd = input("sub-phatty> ").strip().lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    break
                elif cmd.startswith('lfo '):
                    wave = cmd[4:]
                    self.set_lfo_wave(wave)
                elif cmd.startswith('vco '):
                    octave = cmd[4:]
                    self.set_vco_octave(octave)
                elif cmd == 'help':
                    print("Kommandon:")
                    print("  lfo triangle|square|saw|ramp|sample_hold|filter_env")
                    print("  vco 16|8|4|2")
                    print("  quit")
                elif cmd == '':
                    continue
                else:
                    print("✗ Okänt kommando. Skriv 'help' för hjälp.")
                    
            except KeyboardInterrupt:
                print("\nAvslutar...")
                break
            except EOFError:
                break
    
    def close(self):
        """Stäng MIDI-anslutning"""
        if self.outport:
            self.outport.close()
            print("✓ MIDI-anslutning stängd")

def show_help():
    """Visa hjälptext"""
    print("""
Sub Phatty Simple Controller

ANVÄNDNING:
  python3 sub_phatty_final.py                    # Interaktivt läge
  python3 sub_phatty_final.py lfo triangle       # Sätt LFO till triangle
  python3 sub_phatty_final.py vco 8              # Sätt VCO till 8'
  python3 sub_phatty_final.py help               # Visa denna hjälp

LFO VÅGOR:
  triangle, square, saw, ramp, sample_hold, filter_env
  (Även kortformer: sh, env)

VCO OKTAVER:
  16, 8, 4, 2 (motsvarar 16', 8', 4', 2')

EXEMPEL:
  python3 sub_phatty_final.py lfo square
  python3 sub_phatty_final.py vco 2

OBSERVERA:
- Använder MIDI-kanal 2 (som Sub Phatty Editor)
- Kräver att Sub Phatty är ansluten via USB
""")

def main():
    """Huvudfunktion"""
    
    if len(sys.argv) > 1 and sys.argv[1] in ['help', '-h', '--help']:
        show_help()
        return
    
    controller = SubPhattySimpleController()
    
    # Anslut
    if not controller.connect():
        return 1
    
    try:
        # Kommandoradsanvändning
        if len(sys.argv) >= 3:
            cmd = sys.argv[1].lower()
            param = sys.argv[2].lower()
            
            if cmd == 'lfo':
                controller.set_lfo_wave(param)
            elif cmd == 'vco':
                controller.set_vco_octave(param)
            else:
                print(f"✗ Okänt kommando: {cmd}")
                print("Använd 'help' för instruktioner")
                return 1
        else:
            # Interaktivt läge
            controller.interactive_mode()
            
    except Exception as e:
        print(f"✗ Fel: {e}")
        return 1
    finally:
        controller.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())