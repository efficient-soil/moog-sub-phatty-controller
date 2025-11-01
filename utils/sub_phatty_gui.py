#!/usr/bin/env python3
"""
Sub Phatty GUI Controller - Final Version

Ett enkelt GUI som kapslar kommandoradsfunktionaliteten.
Använder korrekt MIDI-kanal (kanal 2) för att styra trasiga switchar.
"""

import mido
import tkinter as tk
from tkinter import ttk
import threading
import time

class SubPhattyGUIController:
    def __init__(self):
        self.outport = None
        self.midi_channel = 1  # Kanal 2 (0-indexerat)
        
        # CC-nummer från officiella MIDI-specen
        self.lfo_cc = 71       # Modulation Source
        self.vco_cc = 74       # VCO 1 Octave
        
        # Värden från officiella specen
        self.lfo_values = {
            'Triangle': 0,
            'Square': 16, 
            'Saw': 32,
            'Sample & Hold': 64
        }
        
        self.vco_values = {
            "32'": 16,
            "16'": 32,
            "8'": 48,
            "4'": 64
        }
        
        self.setup_ui()
        self.connect_midi()
        
    def setup_ui(self):
        """Skapa GUI"""
        self.root = tk.Tk()
        self.root.title("Sub Phatty Controller")
        self.root.geometry("350x450")
        self.root.resizable(False, False)
        
        # Huvudram
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titel
        title_label = ttk.Label(main_frame, text="Moog Sub Phatty Controller", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ansluter...", foreground="gray")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        # LFO Wave Shape sektion
        lfo_frame = ttk.LabelFrame(main_frame, text="LFO Wave Shape", padding="10")
        lfo_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.lfo_var = tk.StringVar(value="Triangle")
        
        lfo_row = 0
        for wave in ['Triangle', 'Square', 'Saw', 'Sample & Hold']:
            btn = ttk.Button(lfo_frame, text=wave, width=12,
                           command=lambda w=wave: self.set_lfo_wave(w))
            btn.grid(row=lfo_row // 2, column=lfo_row % 2, padx=5, pady=3, sticky=tk.W+tk.E)
            lfo_row += 1
        
        # VCO 1 Octave sektion
        vco_frame = ttk.LabelFrame(main_frame, text="VCO 1 Octave", padding="10")
        vco_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.vco_var = tk.StringVar(value="8'")
        
        vco_row = 0
        for octave in ["32'", "16'", "8'", "4'"]:
            btn = ttk.Button(vco_frame, text=octave, width=12,
                           command=lambda o=octave: self.set_vco_octave(o))
            btn.grid(row=vco_row // 2, column=vco_row % 2, padx=5, pady=3, sticky=tk.W+tk.E)
            vco_row += 1
        
        # Status/log sektion
        log_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Skapa en Frame för Text och Scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(text_frame, height=8, width=40, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Konfigurera grid weights
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Kontrollknappar
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(control_frame, text="Återanslut MIDI", 
                  command=self.reconnect_midi).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(control_frame, text="Rensa Log", 
                  command=self.clear_log).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Avsluta", 
                  command=self.close_app).grid(row=0, column=2, padx=(5, 0))
        
        # Konfigurera grid weights för huvudfönster
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def log(self, message, color="black"):
        """Lägg till meddelande i loggen"""
        def update_log():
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            
        # Säkerställ att GUI uppdateras från main thread
        self.root.after(0, update_log)
        
    def connect_midi(self):
        """Anslut till Sub Phatty via MIDI"""
        def connect_worker():
            try:
                output_ports = mido.get_output_names()
                
                sub_phatty_port = None
                for port in output_ports:
                    if 'Sub Phatty' in port or 'Moog' in port:
                        sub_phatty_port = port
                        break
                
                if sub_phatty_port:
                    self.outport = mido.open_output(sub_phatty_port)
                    self.root.after(0, lambda: self.status_label.config(
                        text="✓ Ansluten", foreground="green"))
                    self.log(f"✓ Ansluten till: {sub_phatty_port}")
                    self.log("Använder MIDI-kanal 2 (som Sub Phatty Editor)")
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text="✗ Ingen enhet hittades", foreground="red"))
                    self.log("✗ Ingen Sub Phatty hittades")
                    
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(
                    text="✗ Anslutningsfel", foreground="red"))
                self.log(f"✗ MIDI-anslutningsfel: {e}")
        
        # Kör anslutning i bakgrund för att inte frysa GUI
        threading.Thread(target=connect_worker, daemon=True).start()
    
    def send_cc(self, cc_number, value, description=""):
        """Skicka CC-meddelande"""
        if not self.outport:
            self.log("✗ Ingen MIDI-anslutning")
            return False
            
        try:
            msg = mido.Message('control_change',
                             channel=self.midi_channel,
                             control=cc_number,
                             value=value)
            self.outport.send(msg)
            self.log(f"✓ {description} (CC#{cc_number}={value})")
            return True
        except Exception as e:
            self.log(f"✗ Fel vid sändning: {e}")
            return False
    
    def set_lfo_wave(self, wave):
        """Sätt LFO våg-form"""
        if wave not in self.lfo_values:
            self.log(f"✗ Okänd LFO-våg: {wave}")
            return
            
        value = self.lfo_values[wave]
        self.lfo_var.set(wave)
        success = self.send_cc(self.lfo_cc, value, f"LFO Wave: {wave}")
        
        if success:
            self.log(f"🎵 LFO inställt till: {wave}")
    
    def set_vco_octave(self, octave):
        """Sätt VCO 1 oktav"""
        if octave not in self.vco_values:
            self.log(f"✗ Okänd VCO-oktav: {octave}")
            return
            
        value = self.vco_values[octave]
        self.vco_var.set(octave)
        success = self.send_cc(self.vco_cc, value, f"VCO Octave: {octave}")
        
        if success:
            self.log(f"🎵 VCO oktav inställt till: {octave}")
    
    def clear_log(self):
        """Rensa loggen"""
        self.log_text.delete(1.0, tk.END)
    
    def reconnect_midi(self):
        """Återanslut MIDI"""
        if self.outport:
            self.outport.close()
            self.outport = None
        
        self.status_label.config(text="Återansluter...", foreground="gray")
        self.log("🔄 Återansluter MIDI...")
        self.connect_midi()
    
    def close_app(self):
        """Stäng applikationen"""
        if self.outport:
            self.outport.close()
        self.root.destroy()
    
    def run(self):
        """Starta GUI"""
        # Lägg till en välkomsttext
        self.log("🎹 Sub Phatty Controller startad")
        self.log("Använd knapparna för att styra LFO och VCO")
        
        self.root.mainloop()

if __name__ == "__main__":
    print("Startar Sub Phatty GUI Controller...")
    controller = SubPhattyGUIController()
    controller.run()