#!/usr/bin/env python3
"""
Enkel MIDI-kontroller för Moog Sub Phatty
Styr LFO Wave Shape och VCO 1 Footage (16', 8', 4', 2')
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import time

# Försök importera mido, fallback till enklare lösning om det misslyckas
try:
    import mido
    MIDO_AVAILABLE = True
except ImportError as e:
    print(f"Varning: Kunde inte importera mido: {e}")
    MIDO_AVAILABLE = False
    # Försök med rtmidi direkt
    try:
        import rtmidi
        RTMIDI_AVAILABLE = True
    except ImportError:
        RTMIDI_AVAILABLE = False
        print("Varning: Ingen MIDI-support hittades")

class SubPhattyController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sub Phatty Controller")
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        
        # MIDI-relaterade variabler
        self.midi_out = None
        self.midi_channel = 0  # MIDI-kanal 1 (0-indexed)
        
        # MIDI CC-nummer för Sub Phatty (från officiell dokumentation)
        self.MODULATION_SOURCE_CC = 71  # LFO Wave Shape
        self.VCO1_OCTAVE_CC = 74        # VCO 1 Octave/Footage
        
        # Aktuella värden
        self.current_lfo_wave = tk.IntVar(value=0)
        self.current_vco1_footage = tk.IntVar(value=32)  # Default till 8'
        
        self.setup_gui()
        self.connect_midi()
    
    def setup_gui(self):
        # Huvudram
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # LFO Wave Shape sektion
        lfo_frame = ttk.LabelFrame(main_frame, text="LFO Wave Shape", padding="10")
        lfo_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        lfo_waves = [
            ("Triangle LFO", 0),
            ("Square LFO", 16),
            ("Saw LFO", 32),
            ("Ramp LFO", 48),
            ("S&H", 64),
            ("Filter Envelope", 80)
        ]
        
        for i, (text, value) in enumerate(lfo_waves):
            ttk.Radiobutton(lfo_frame, text=text, variable=self.current_lfo_wave, 
                           value=value, command=self.send_lfo_wave).grid(row=i, column=0, sticky=tk.W)
        
        # VCO 1 Footage sektion
        vco_frame = ttk.LabelFrame(main_frame, text="VCO 1 Footage", padding="10")
        vco_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        vco_footages = [
            ("16' (Sub-oktav)", 16),
            ("8' (Normal)", 32),
            ("4' (En oktav upp)", 48),
            ("2' (Två oktaver upp)", 64)
        ]
        
        for i, (text, value) in enumerate(vco_footages):
            ttk.Radiobutton(vco_frame, text=text, variable=self.current_vco1_footage, 
                           value=value, command=self.send_vco1_footage).grid(row=i, column=0, sticky=tk.W)
        
        # Status och knappar
        self.status_label = ttk.Label(main_frame, text="Ansluter till Sub Phatty...")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(10, 5))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(button_frame, text="Återanslut MIDI", command=self.connect_midi).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Avsluta", command=self.root.quit).grid(row=0, column=1)
    
    def connect_midi(self):
        """Anslut till Sub Phatty via MIDI"""
        try:
            # Stäng befintlig anslutning
            if self.midi_out:
                if MIDO_AVAILABLE:
                    self.midi_out.close()
                elif RTMIDI_AVAILABLE:
                    self.midi_out.close_port()
            
            if MIDO_AVAILABLE:
                # Använd mido
                output_ports = mido.get_output_names()
                sub_phatty_port = None
                
                # Leta efter Sub Phatty i portlistan
                for port in output_ports:
                    if 'sub phatty' in port.lower() or 'moog' in port.lower():
                        sub_phatty_port = port
                        break
                
                if not sub_phatty_port:
                    if output_ports:
                        sub_phatty_port = output_ports[0]
                        self.status_label.config(text=f"Använder: {sub_phatty_port}")
                    else:
                        raise Exception("Inga MIDI-utgångar hittades")
                else:
                    self.status_label.config(text=f"Ansluten till: {sub_phatty_port}")
                
                self.midi_out = mido.open_output(sub_phatty_port)
                
            elif RTMIDI_AVAILABLE:
                # Använd rtmidi direkt
                self.midi_out = rtmidi.MidiOut()
                ports = self.midi_out.get_ports()
                
                if not ports:
                    raise Exception("Inga MIDI-utgångar hittades")
                
                # Leta efter Sub Phatty
                sub_phatty_port_idx = None
                for i, port in enumerate(ports):
                    if 'sub phatty' in port.lower() or 'moog' in port.lower():
                        sub_phatty_port_idx = i
                        break
                
                if sub_phatty_port_idx is None:
                    sub_phatty_port_idx = 0  # Använd första porten som fallback
                
                self.midi_out.open_port(sub_phatty_port_idx)
                self.status_label.config(text=f"Ansluten till: {ports[sub_phatty_port_idx]}")
                
            else:
                raise Exception("Ingen MIDI-support tillgänglig. Installera python-rtmidi eller mido.")
            
        except Exception as e:
            self.status_label.config(text=f"MIDI-fel: {str(e)}")
            port_list = []
            try:
                if MIDO_AVAILABLE:
                    port_list = mido.get_output_names()
                elif RTMIDI_AVAILABLE:
                    temp_midi = rtmidi.MidiOut()
                    port_list = temp_midi.get_ports()
                    temp_midi.close_port()
            except:
                pass
            
            messagebox.showerror("MIDI-anslutningsfel", 
                               f"Kunde inte ansluta till Sub Phatty:\n{str(e)}\n\n"
                               f"Tillgängliga MIDI-portar:\n" + "\n".join(port_list) if port_list else "Inga MIDI-portar hittades")
    
    def send_midi_cc(self, cc_number, value):
        """Skicka MIDI Control Change-meddelande"""
        if self.midi_out:
            try:
                if MIDO_AVAILABLE:
                    msg = mido.Message('control_change', 
                                     channel=self.midi_channel, 
                                     control=cc_number, 
                                     value=value)
                    self.midi_out.send(msg)
                elif RTMIDI_AVAILABLE:
                    # MIDI Control Change: Status byte (0xB0 + channel) + CC number + value
                    status_byte = 0xB0 + self.midi_channel
                    midi_message = [status_byte, cc_number, value]
                    self.midi_out.send_message(midi_message)
                
                print(f"Skickade MIDI CC: Kanal {self.midi_channel + 1}, CC #{cc_number}, Värde {value}")
            except Exception as e:
                self.status_label.config(text=f"Fel vid MIDI-sändning: {str(e)}")
    
    def send_lfo_wave(self):
        """Skicka Modulation Source till Sub Phatty"""
        wave_value = self.current_lfo_wave.get()
        self.send_midi_cc(self.MODULATION_SOURCE_CC, wave_value)
        
        wave_names = {0: "Triangle LFO", 16: "Square LFO", 32: "Saw LFO", 48: "Ramp LFO", 64: "S&H", 80: "Filter Envelope"}
        print(f"Modulation Source satt till: {wave_names.get(wave_value, f'Värde {wave_value}')}")
    
    def send_vco1_footage(self):
        """Skicka VCO 1 Octave till Sub Phatty"""
        footage_value = self.current_vco1_footage.get()
        self.send_midi_cc(self.VCO1_OCTAVE_CC, footage_value)
        
        footage_names = {16: "16'", 32: "8'", 48: "4'", 64: "2'"}
        print(f"VCO 1 Octave satt till: {footage_names.get(footage_value, f'Värde {footage_value}')}")
    
    def run(self):
        """Starta applikationen"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Stäng MIDI-anslutning när applikationen avslutas"""
        if self.midi_out:
            try:
                if MIDO_AVAILABLE:
                    self.midi_out.close()
                elif RTMIDI_AVAILABLE:
                    self.midi_out.close_port()
            except:
                pass  # Ignorera fel vid stängning
        self.root.destroy()

def main():
    try:
        app = SubPhattyController()
        app.run()
    except KeyboardInterrupt:
        print("\nAvbryter...")
        sys.exit(0)
    except Exception as e:
        print(f"Fel vid start: {e}")
        messagebox.showerror("Startfel", f"Kunde inte starta applikationen:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()