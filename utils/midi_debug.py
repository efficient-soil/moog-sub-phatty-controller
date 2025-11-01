#!/usr/bin/env python3
"""
MIDI-felsökningsverktyg för Sub Phatty
Testar olika CC-nummer och visar detaljerad information
"""

import mido
import time

def test_midi_connection():
    """Testa MIDI-anslutning och visa detaljerad information"""
    print("=== Sub Phatty MIDI Felsökning ===\n")
    
    # Lista alla MIDI-portar
    output_ports = mido.get_output_names()
    input_ports = mido.get_input_names()
    
    print("MIDI-utgångar:")
    for i, port in enumerate(output_ports):
        print(f"  {i}: {port}")
    
    print("\nMIDI-ingångar:")
    for i, port in enumerate(input_ports):
        print(f"  {i}: {port}")
    
    # Hitta Sub Phatty
    sub_phatty_out = None
    for port in output_ports:
        if 'sub phatty' in port.lower() or 'moog' in port.lower():
            sub_phatty_out = port
            break
    
    if not sub_phatty_out:
        print("\n❌ Ingen Sub Phatty hittad i MIDI-utgångarna!")
        return
    
    print(f"\n✅ Hittade Sub Phatty: {sub_phatty_out}")
    
    # Anslut
    try:
        midi_out = mido.open_output(sub_phatty_out)
        print("✅ MIDI-utgång öppnad")
    except Exception as e:
        print(f"❌ Kunde inte öppna MIDI-utgång: {e}")
        return
    
    # Testa olika MIDI-kanaler och CC-nummer
    print("\n=== Testar MIDI-kommunikation ===")
    print("Lyssna på din Sub Phatty medan vi testar...")
    time.sleep(2)
    
    # Kända CC-nummer från olika källor
    test_cases = [
        # (beskrivning, cc_nummer, test_värden)
        ("LFO Wave Shape (CC 24)", 24, [0, 1, 2, 3]),
        ("VCO 1 Footage (CC 15)", 15, [0, 1, 2, 3]),
        ("LFO Wave Shape (CC 26)", 26, [0, 1, 2, 3]),  # Alternativt nummer
        ("VCO 1 Octave (CC 23)", 23, [0, 1, 2]),       # Alternativt nummer
        ("Filter Cutoff (CC 74)", 74, [0, 64, 127]),   # Standard filter CC
        ("Volume (CC 7)", 7, [100, 127]),              # Volym-test
    ]
    
    for description, cc_num, values in test_cases:
        print(f"\nTestar {description}:")
        for channel in [0, 15]:  # Testa kanal 1 och 16
            print(f"  Kanal {channel + 1}:", end=" ")
            for value in values:
                try:
                    msg = mido.Message('control_change', 
                                     channel=channel, 
                                     control=cc_num, 
                                     value=value)
                    midi_out.send(msg)
                    print(f"{value}", end=" ")
                    time.sleep(0.5)  # Kort paus mellan meddelanden
                except Exception as e:
                    print(f"FEL({value})", end=" ")
            print()
        time.sleep(1)
    
    # Testa Program Change (preset-byte)
    print(f"\nTestar Program Change (preset-byte):")
    for channel in [0, 15]:
        print(f"  Kanal {channel + 1}: Preset 0->1->0")
        try:
            # Preset 0
            msg = mido.Message('program_change', channel=channel, program=0)
            midi_out.send(msg)
            time.sleep(1)
            # Preset 1  
            msg = mido.Message('program_change', channel=channel, program=1)
            midi_out.send(msg)
            time.sleep(1)
            # Tillbaka till preset 0
            msg = mido.Message('program_change', channel=channel, program=0)
            midi_out.send(msg)
        except Exception as e:
            print(f"    FEL: {e}")
    
    print("\n=== Test slutfört ===")
    print("Hörde du några förändringar på Sub Phatty under testet?")
    print("Om ja, notera vilken kanal och CC-nummer som fungerade.")
    
    midi_out.close()

def interactive_test():
    """Interaktiv testning av specifika CC-nummer"""
    print("\n=== Interaktiv MIDI-test ===")
    
    # Anslut till Sub Phatty
    output_ports = mido.get_output_names()
    sub_phatty_out = None
    for port in output_ports:
        if 'sub phatty' in port.lower() or 'moog' in port.lower():
            sub_phatty_out = port
            break
    
    if not sub_phatty_out:
        print("Ingen Sub Phatty hittad!")
        return
    
    try:
        midi_out = mido.open_output(sub_phatty_out)
    except Exception as e:
        print(f"Kunde inte ansluta: {e}")
        return
    
    print("Skriv kommandon i formatet: kanal cc_nummer värde")
    print("Exempel: 1 24 2  (skicka CC 24 med värde 2 på kanal 1)")
    print("Skriv 'q' för att avsluta")
    
    while True:
        try:
            cmd = input("\nMIDI> ").strip()
            if cmd.lower() == 'q':
                break
            
            parts = cmd.split()
            if len(parts) != 3:
                print("Format: kanal cc_nummer värde")
                continue
            
            channel = int(parts[0]) - 1  # Konvertera till 0-indexerat
            cc_num = int(parts[1])
            value = int(parts[2])
            
            if not (0 <= channel <= 15):
                print("Kanal måste vara 1-16")
                continue
            if not (0 <= cc_num <= 127):
                print("CC-nummer måste vara 0-127")
                continue
            if not (0 <= value <= 127):
                print("Värde måste vara 0-127")
                continue
            
            msg = mido.Message('control_change', 
                             channel=channel, 
                             control=cc_num, 
                             value=value)
            midi_out.send(msg)
            print(f"✅ Skickat: Kanal {channel + 1}, CC {cc_num}, Värde {value}")
            
        except ValueError:
            print("Använd endast siffror")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Fel: {e}")
    
    midi_out.close()

if __name__ == "__main__":
    test_midi_connection()
    
    answer = input("\nVill du köra interaktiv test också? (j/n): ").strip().lower()
    if answer in ['j', 'ja', 'y', 'yes']:
        interactive_test()