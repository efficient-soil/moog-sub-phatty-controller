#!/usr/bin/env python3
"""
Sub Phatty Controller - Kanal 2 Version

VIKTIG UPPTÄCKT: Sub Phatty Editor använder MIDI-kanal 2, inte kanal 1!

Denna version testar om det räcker att använda rätt kanal för CC-meddelanden
innan vi behöver gå över till SysEx.
"""

import mido
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class SubPhattyChannel2Controller:
    def __init__(self):
        self.outport = None
        self.setup_ui()
        self.connect_midi()
        
        # MIDI-kanal 2 (Editor använder kanal 2!)
        self.midi_channel = 1  # MIDI-kanaler är 0-indexerade, så kanal 2 = 1
        
        # Korrekt CC-nummer från officiella specen
        self.cc_numbers = {
            'modulation_source': 71,  # LFO Wave Shape
            'vco1_octave': 74         # VCO 1 Octave
        }
        
        # Värden från officiella specen
        self.lfo_values = {
            'triangle': 0,      # Triangle LFO
            'square': 16,       # Square LFO  
            'saw': 32,          # Saw LFO
            'sample_hold': 64   # Sample & Hold
        }
        
        self.vco_values = {
            "32'": 16,    # 32 foot
            "16'": 32,    # 16 foot  
            "8'": 48,     # 8 foot
            "4'": 64      # 4 foot
        }
        
    def setup_ui(self):
        """Skapa GUI"""
        self.root = tk.Tk()
        self.root.title("Sub Phatty Controller - Kanal 2 Test")
        self.root.geometry("400x500")
        
        # Info text
        info_text = """KANAL 2 TEST

Viktigt: Sub Phatty Editor använder MIDI-kanal 2!
Vi har använt kanal 1 hela tiden - det är därför 
det inte fungerat.

Denna version testar CC på kanal 2.
"""
        info_label = tk.Label(self.root, text=info_text, 
                             justify=tk.LEFT, fg="blue", font=("Arial", 9))
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
        
        ttk.Button(button_frame, text="Test LFO Triangle", 
                  command=lambda: self.test_cc_send('lfo', 'triangle')).pack(pady=2)
        ttk.Button(button_frame, text="Test LFO Square", 
                  command=lambda: self.test_cc_send('lfo', 'square')).pack(pady=2)
        ttk.Button(button_frame, text="Test VCO 8'", 
                  command=lambda: self.test_cc_send('vco', "8'")).pack(pady=2)
        ttk.Button(button_frame, text="Test VCO 4'", 
                  command=lambda: self.test_cc_send('vco', "4'")).pack(pady=2)
        
        ttk.Button(button_frame, text="Återanslut MIDI", 
                  command=self.reconnect_midi).pack(pady=5)
        ttk.Button(button_frame, text="Avsluta", 
                  command=self.close_app).pack(pady=5)
        
        # Log output
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.log_text = tk.Text(log_frame, height=8, width=50)
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
            output_ports = mido.get_output_names()
            
            sub_phatty_out = None
            for port in output_ports:
                if 'Sub Phatty' in port or 'Moog' in port:
                    sub_phatty_out = port
                    break
            
            if sub_phatty_out:
                self.outport = mido.open_output(sub_phatty_out)
                self.status_label.config(text="Ansluten till kanal 2", fg="green")
                self.log(f"Ansluten till: {sub_phatty_out}")
                self.log("VIKTIGT: Använder nu MIDI-kanal 2 (som Editor)")
            else:
                self.status_label.config(text="Ingen enhet hittades", fg="red")
                self.log("VARNING: Ingen Sub Phatty hittades")
                
        except Exception as e:
            self.log(f"MIDI-anslutningsfel: {e}")
            self.status_label.config(text="Anslutningsfel", fg="red")
    
    def send_cc_message(self, cc_number, value, description=""):
        """Skicka CC-meddelande på kanal 2"""
        if not self.outport:
            self.log("Ingen MIDI-utgång tillgänglig")
            return False
            
        try:
            # KANAL 2 istället för kanal 1!
            msg = mido.Message('control_change', 
                             channel=self.midi_channel,  # Kanal 2 (1 i 0-indexerat)
                             control=cc_number, 
                             value=value)
            
            self.outport.send(msg)
            self.log(f"Skickade på KANAL 2 - CC#{cc_number}={value} ({description})")
            return True
            
        except Exception as e:
            self.log(f"Fel vid CC-sändning: {e}")
            return False
    
    def send_lfo_change(self):
        """Skicka LFO wave shape ändring"""
        wave = self.lfo_var.get()
        value = self.lfo_values[wave]
        cc_num = self.cc_numbers['modulation_source']
        
        wave_name = wave.replace('_', ' ').title()
        success = self.send_cc_message(cc_num, value, f"LFO {wave_name}")
        
        if success:
            self.log(f"✓ LFO ändrat till: {wave_name}")
    
    def send_vco_change(self):
        """Skicka VCO octave ändring"""
        octave = self.vco_var.get()
        value = self.vco_values[octave]
        cc_num = self.cc_numbers['vco1_octave']
        
        success = self.send_cc_message(cc_num, value, f"VCO {octave}")
        
        if success:
            self.log(f"✓ VCO oktav ändrat till: {octave}")
    
    def test_cc_send(self, param_type, param_value):
        """Testfunktion för att skicka specifika värden"""
        if param_type == 'lfo':
            value = self.lfo_values[param_value]
            cc_num = self.cc_numbers['modulation_source']
            desc = f"LFO {param_value.replace('_', ' ').title()}"
        else:  # vco
            value = self.vco_values[param_value]
            cc_num = self.cc_numbers['vco1_octave']
            desc = f"VCO {param_value}"
            
        self.log(f"*** TESTAR: {desc} ***")
        success = self.send_cc_message(cc_num, value, desc)
        
        if success:
            self.log("Test skickat - kontrollera om det kvarstår på Sub Phatty!")
        
    def reconnect_midi(self):
        """Återanslut MIDI"""
        if self.outport:
            self.outport.close()
        
        self.status_label.config(text="Återansluter...", fg="gray")
        self.connect_midi()
    
    def close_app(self):
        """Stäng applikationen"""
        if self.outport:
            self.outport.close()
        self.root.destroy()
    
    def run(self):
        """Starta GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Sub Phatty Controller - Kanal 2 Test")
    print("Testar CC-meddelanden på MIDI-kanal 2 (som Sub Phatty Editor använder)")
    
    controller = SubPhattyChannel2Controller()
    controller.run()