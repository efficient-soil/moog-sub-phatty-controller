#!/usr/bin/env python3
"""
Sub Phatty Controller - Persistent version
Håller inställningar genom kontinuerlig sändning
"""

import mido
import time
import threading
import sys

class PersistentSubPhattyController:
    def __init__(self):
        self.midi_out = None
        self.running = False
        
        # MIDI CC-nummer
        self.MODULATION_SOURCE_CC = 71
        self.VCO1_OCTAVE_CC = 74
        
        # Aktuella värden
        self.current_mod_source = 0   # Triangle LFO
        self.current_vco1_octave = 32 # 8'
        
        # Värden enligt MIDI-spec
        self.mod_source_values = [0, 16, 32, 48, 64, 80]
        self.mod_source_names = ["Triangle LFO", "Square LFO", "Saw LFO", "Ramp LFO", "S&H", "Filter Envelope"]
        
        self.vco_octave_values = [16, 32, 48, 64]
        self.vco_octave_names = ["16'", "8'", "4'", "2'"]
        
        # Thread för kontinuerlig sändning
        self.sender_thread = None
    
    def connect(self):
        """Anslut till Sub Phatty"""
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
                return False
            
            self.midi_out = mido.open_output(sub_phatty_port)
            print(f"✅ Ansluten till: {sub_phatty_port}")
            return True
            
        except Exception as e:
            print(f"MIDI-fel: {e}")
            return False
    
    def send_parameter(self, cc_number, value):
        """Skicka MIDI CC-meddelande"""
        if self.midi_out:
            try:
                msg = mido.Message('control_change', channel=0, control=cc_number, value=value)
                self.midi_out.send(msg)
                return True
            except Exception as e:
                print(f"Fel vid sändning: {e}")
        return False
    
    def parameter_keeper(self):
        """Kontinuerligt säkerställ att rätt parametrar är aktiva"""
        while self.running:
            # Skicka aktuella värden var 500ms
            self.send_parameter(self.MODULATION_SOURCE_CC, self.current_mod_source)
            time.sleep(0.1)
            self.send_parameter(self.VCO1_OCTAVE_CC, self.current_vco1_octave)
            time.sleep(0.4)  # Totalt 500ms mellan cykler
    
    def start_parameter_keeper(self):
        """Starta kontinuerlig parametersändning"""
        if not self.running:
            self.running = True
            self.sender_thread = threading.Thread(target=self.parameter_keeper, daemon=True)
            self.sender_thread.start()
            print("🔄 Parameterkontroll aktiverad (skickar värden kontinuerligt)")
    
    def stop_parameter_keeper(self):
        """Stoppa kontinuerlig parametersändning"""
        self.running = False
        if self.sender_thread:
            self.sender_thread.join(timeout=1)
        print("⏹️  Parameterkontroll stoppad")
    
    def set_modulation_source(self, index):
        """Sätt modulationskälla"""
        if 0 <= index <= 5:
            self.current_mod_source = self.mod_source_values[index]
            print(f"✅ Modulation Source: {self.mod_source_names[index]} (CC {self.MODULATION_SOURCE_CC} = {self.current_mod_source})")
            return True
        return False
    
    def set_vco1_octave(self, index):
        """Sätt VCO 1 oktav"""
        if 0 <= index <= 3:
            self.current_vco1_octave = self.vco_octave_values[index]
            print(f"✅ VCO 1 Octave: {self.vco_octave_names[index]} (CC {self.VCO1_OCTAVE_CC} = {self.current_vco1_octave})")
            return True
        return False
    
    def run_interactive(self):
        """Kör interaktiv loop"""
        print("\n=== Sub Phatty Controller (Persistent version) ===")
        print("Denna version håller inställningar genom kontinuerlig sändning\n")
        
        if not self.connect():
            return
        
        print("\n=== Kommandon ===")
        print("Modulation Source:")
        for i, name in enumerate(self.mod_source_names):
            print(f"  m{i} = {name}")
        print("\nVCO 1 Octave:")
        for i, name in enumerate(self.vco_octave_names):
            print(f"  v{i} = {name}")
        print("\nKontroll:")
        print("  start = Aktivera kontinuerlig parametersändning")
        print("  stop  = Stoppa kontinuerlig parametersändning") 
        print("  q     = Avsluta")
        print()
        
        try:
            while True:
                cmd = input("Sub Phatty> ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == 'start':
                    self.start_parameter_keeper()
                elif cmd == 'stop':
                    self.stop_parameter_keeper()
                elif cmd.startswith('m') and len(cmd) == 2 and cmd[1].isdigit():
                    idx = int(cmd[1])
                    if not self.set_modulation_source(idx):
                        print("✗ Modulation Source: 0-5")
                elif cmd.startswith('v') and len(cmd) == 2 and cmd[1].isdigit():
                    idx = int(cmd[1])
                    if not self.set_vco1_octave(idx):
                        print("✗ VCO 1 Octave: 0-3")
                else:
                    print("✗ Okänt kommando")
                    
        except KeyboardInterrupt:
            pass
        
        # Städa upp
        self.stop_parameter_keeper()
        if self.midi_out:
            self.midi_out.close()
        print("\nMIDI-anslutning stängd")

def main():
    controller = PersistentSubPhattyController()
    controller.run_interactive()

if __name__ == "__main__":
    main()