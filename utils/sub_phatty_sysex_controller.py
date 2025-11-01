#!/usr/bin/env python3
"""
Sub Phatty SysEx Controller - Använder samma metod som Sub Phatty Editor

Denna version baserar sig på analysen av Sub Phatty Editor och använder:
- SysEx-meddelanden istället för CC
- MIDI-kanal 2 
- Moog SysEx-format (04 06...)

Baserat på den observerade MIDI-trafiken från Sub Phatty Editor.
"""

import mido
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class SubPhattySysExController:
    def __init__(self):
        self.outport = None
        self.inport = None
        self.current_patch_data = None
        
        # Moog Manufacturer ID: 0x04
        # Sub Phatty Device ID: 0x06  
        self.moog_header = [0x04, 0x06]
        
        # Baserat på observerad trafik - detta är gissningar som behöver verifieras
        self.lfo_wave_positions = {
            # Position i SysEx-data där LFO wave shape lagras (gissning)
            'triangle': 0,   # Värde 0x00
            'square': 16,    # Värde 0x10  
            'saw': 32,       # Värde 0x20
            'sample_hold': 64 # Värde 0x40
        }
        
        self.vco_octave_positions = {
            # Position i SysEx-data där VCO 1 octave lagras (gissning)
            "32'": 16,    # Värde 0x10
            "16'": 32,    # Värde 0x20
            "8'": 48,     # Värde 0x30
            "4'": 64      # Värde 0x40
        }
        
        self.setup_ui()
        self.connect_midi()
        
    def setup_ui(self):
        """Skapa GUI"""
        self.root = tk.Tk()
        self.root.title("Sub Phatty SysEx Controller (Experimentell)")
        self.root.geometry("400x600")
        
        # Info text
        info_text = """EXPERIMENTELL VERSION

Denna version försöker använda SysEx-meddelanden
baserat på analys av Sub Phatty Editor.

VARNING: Detta är experimentellt och kan
potentiellt påverka andra inställningar!

Använd på egen risk.
"""
        info_label = tk.Label(self.root, text=info_text, 
                             justify=tk.LEFT, fg="red", font=("Arial", 9))
        info_label.pack(pady=10, padx=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ansluter...", fg="gray")
        self.status_label.pack(pady=5)
        
        # LFO Wave Shape
        lfo_frame = ttk.LabelFrame(self.root, text="LFO Wave Shape")
        lfo_frame.pack(pady=10, padx=10, fill="x")
        
        self.lfo_var = tk.StringVar(value="triangle")
        for wave in ['triangle', 'square', 'saw', 'sample_hold']:
            wave_name = wave.replace('_', ' ').title()
            ttk.Radiobutton(lfo_frame, text=wave_name, 
                          variable=self.lfo_var, value=wave,
                          command=self.send_lfo_change).pack(anchor="w", padx=10, pady=2)
        
        # VCO 1 Octave  
        vco_frame = ttk.LabelFrame(self.root, text="VCO 1 Octave")
        vco_frame.pack(pady=10, padx=10, fill="x")
        
        self.vco_var = tk.StringVar(value="8'")
        for octave in ["32'", "16'", "8'", "4'"]:
            ttk.Radiobutton(vco_frame, text=octave,
                          variable=self.vco_var, value=octave,
                          command=self.send_vco_change).pack(anchor="w", padx=10, pady=2)
        
        # Knappar
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Läs Nuvarande Patch", 
                  command=self.request_patch_data).pack(pady=5)
        ttk.Button(button_frame, text="Återanslut MIDI", 
                  command=self.reconnect_midi).pack(pady=5)
        ttk.Button(button_frame, text="Avsluta", 
                  command=self.close_app).pack(pady=5)
        
        # Log output
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def log(self, message):
        """Lägg till meddelande i loggen"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def connect_midi(self):
        """Anslut till Sub Phatty via MIDI"""
        try:
            # Hitta Sub Phatty MIDI-portar
            input_ports = mido.get_input_names()
            output_ports = mido.get_output_names()
            
            sub_phatty_in = None
            sub_phatty_out = None
            
            for port in input_ports:
                if 'Sub Phatty' in port or 'Moog' in port:
                    sub_phatty_in = port
                    break
                    
            for port in output_ports:
                if 'Sub Phatty' in port or 'Moog' in port:
                    sub_phatty_out = port
                    break
            
            if sub_phatty_out:
                self.outport = mido.open_output(sub_phatty_out)
                self.log(f"Ansluten till utgång: {sub_phatty_out}")
            else:
                self.log("VARNING: Ingen Sub Phatty utgång hittades")
                
            if sub_phatty_in:
                self.inport = mido.open_input(sub_phatty_in)
                self.log(f"Ansluten till ingång: {sub_phatty_in}")
                # Starta MIDI-lyssning i bakgrunden
                threading.Thread(target=self.listen_for_midi, daemon=True).start()
            else:
                self.log("VARNING: Ingen Sub Phatty ingång hittades")
            
            if self.outport:
                self.status_label.config(text="Ansluten", fg="green")
                self.log("MIDI-anslutning etablerad")
            else:
                self.status_label.config(text="Ingen enhet hittades", fg="red")
                
        except Exception as e:
            self.log(f"MIDI-anslutningsfel: {e}")
            self.status_label.config(text="Anslutningsfel", fg="red")
    
    def listen_for_midi(self):
        """Lyssna på inkommande MIDI-meddelanden"""
        if not self.inport:
            return
            
        try:
            for msg in self.inport:
                if hasattr(msg, 'data') and len(msg.data) > 4:
                    # Kolla om det är en Moog SysEx
                    if msg.data[0:2] == bytes(self.moog_header):
                        self.log(f"Mottog Moog SysEx: {msg.data[:10].hex()}...")
                        if len(msg.data) > 20:  # Stor patch data
                            self.current_patch_data = msg.data
                            self.log("Patch-data sparad")
        except Exception as e:
            self.log(f"MIDI-lyssningsfel: {e}")
    
    def request_patch_data(self):
        """Begär nuvarande patch-data från Sub Phatty"""
        if not self.outport:
            self.log("Ingen MIDI-utgång tillgänglig")
            return
            
        try:
            # SysEx patch request (gissning baserat på observerad trafik)
            # Detta är en gissning - kanske 04 06 06 betyder "request patch data"
            patch_request = mido.Message('sysex', data=self.moog_header + [0x06, 0x00])
            
            self.outport.send(patch_request)
            self.log("Skickade patch-dataförfrågan...")
            
        except Exception as e:
            self.log(f"Fel vid patch-förfrågan: {e}")
    
    def send_lfo_change(self):
        """Skicka LFO wave shape ändring via SysEx"""
        if not self.outport:
            self.log("Ingen MIDI-utgång tillgänglig")
            return
        
        try:
            wave = self.lfo_var.get()
            self.log(f"Försöker ändra LFO wave till: {wave}")
            
            # EXPERIMENTELL: Försök skicka en minimal SysEx-ändring
            # Baserat på observerat mönster - detta är gissningar!
            
            # Skicka en kort SysEx med bara LFO-ändringen
            lfo_value = self.lfo_wave_positions[wave]
            
            # Format: Moog header + kommando + data 
            sysex_data = self.moog_header + [0x04, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, lfo_value]
            
            msg = mido.Message('sysex', data=sysex_data)
            self.outport.send(msg)
            self.log(f"Skickade LFO SysEx: {sysex_data}")
            
        except Exception as e:
            self.log(f"Fel vid LFO-ändring: {e}")
    
    def send_vco_change(self):
        """Skicka VCO octave ändring via SysEx"""
        if not self.outport:
            self.log("Ingen MIDI-utgång tillgänglig")
            return
        
        try:
            octave = self.vco_var.get()
            self.log(f"Försöker ändra VCO octave till: {octave}")
            
            # EXPERIMENTELL: Liknande som LFO men för VCO
            vco_value = self.vco_octave_positions[octave]
            
            # Format: Moog header + kommando + data
            sysex_data = self.moog_header + [0x04, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, vco_value]
            
            msg = mido.Message('sysex', data=sysex_data)
            self.outport.send(msg)
            self.log(f"Skickade VCO SysEx: {sysex_data}")
            
        except Exception as e:
            self.log(f"Fel vid VCO-ändring: {e}")
    
    def reconnect_midi(self):
        """Återanslut MIDI"""
        if self.outport:
            self.outport.close()
        if self.inport:
            self.inport.close()
        
        self.status_label.config(text="Återansluter...", fg="gray")
        self.connect_midi()
    
    def close_app(self):
        """Stäng applikationen"""
        if self.outport:
            self.outport.close()
        if self.inport:
            self.inport.close()
        self.root.destroy()
    
    def run(self):
        """Starta GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Sub Phatty SysEx Controller - Experimentell version")
    print("Baserad på analys av Sub Phatty Editor MIDI-trafik")
    print("VARNING: Experimentell - använd försiktigt!")
    
    controller = SubPhattySysExController()
    controller.run()