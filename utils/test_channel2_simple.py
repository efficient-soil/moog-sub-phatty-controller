#!/usr/bin/env python3
"""
Sub Phatty Channel 2 Test - Kommandorad

Enkel test för att se om MIDI-kanal 2 löser problemet.
"""

import mido
import time

def test_midi_channel_2():
    """Testa CC-meddelanden på MIDI-kanal 2"""
    
    print("=== Sub Phatty Kanal 2 Test ===")
    print()
    
    # Hitta Sub Phatty
    output_ports = mido.get_output_names()
    print("Tillgängliga MIDI-utgångar:")
    for i, port in enumerate(output_ports):
        print(f"  {i}: {port}")
    
    sub_phatty_port = None
    for port in output_ports:
        if 'Sub Phatty' in port or 'Moog' in port:
            sub_phatty_port = port
            break
    
    if not sub_phatty_port:
        print("VARNING: Ingen Sub Phatty hittades!")
        return
    
    print(f"\nAnsluter till: {sub_phatty_port}")
    
    try:
        with mido.open_output(sub_phatty_port) as outport:
            print("Ansluten!")
            print()
            
            # VIKTIGT: Använd kanal 1 (= MIDI-kanal 2, 0-indexerat)
            channel = 1  # Kanal 2 i MIDI-termer
            
            print("Testar LFO Wave Shape på KANAL 2...")
            
            # CC #71 för LFO Wave Shape
            lfo_tests = [
                (0, "Triangle LFO"),
                (16, "Square LFO"),
                (32, "Saw LFO"),
                (64, "Sample & Hold")
            ]
            
            for value, description in lfo_tests:
                print(f"  Skickar CC#71 = {value} ({description}) på kanal 2...")
                
                msg = mido.Message('control_change', 
                                 channel=channel, 
                                 control=71, 
                                 value=value)
                outport.send(msg)
                
                print(f"    Skickat! Kontrollera om LFO-switchen ändras på Sub Phatty")
                
                # Vänta för att användaren ska hinna se
                time.sleep(2)
            
            print()
            print("Testar VCO 1 Octave på KANAL 2...")
            
            # CC #74 för VCO 1 Octave
            vco_tests = [
                (16, "32' octave"),
                (32, "16' octave"), 
                (48, "8' octave"),
                (64, "4' octave")
            ]
            
            for value, description in vco_tests:
                print(f"  Skickar CC#74 = {value} ({description}) på kanal 2...")
                
                msg = mido.Message('control_change',
                                 channel=channel,
                                 control=74, 
                                 value=value)
                outport.send(msg)
                
                print(f"    Skickat! Kontrollera om VCO-switchen ändras på Sub Phatty")
                
                time.sleep(2)
            
            print()
            print("Test avslutat.")
            print()
            print("RESULTAT-INSTRUKTIONER:")
            print("1. Om switcharna ändrades och KVARSTOD = Problem löst!")
            print("2. Om switcharna ändrades men gick tillbaka = Behöver SysEx")  
            print("3. Om inget hände = Kanske andra CC-nummer eller problem")
            
    except Exception as e:
        print(f"Fel: {e}")

if __name__ == "__main__":
    test_midi_channel_2()