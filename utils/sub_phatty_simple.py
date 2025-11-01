#!/usr/bin/env python3
"""
Enkel kommandorads-version av Sub Phatty Controller
Fungerar utan GUI om MIDI-biblioteken krånglar
"""

import sys

# Försök importera MIDI-bibliotek
try:
    import mido
    MIDO_AVAILABLE = True
    print("✓ Mido MIDI-bibliotek laddat")
except ImportError:
    MIDO_AVAILABLE = False
    print("✗ Kunde inte ladda mido")

def list_midi_ports():
    """Lista tillgängliga MIDI-portar"""
    if MIDO_AVAILABLE:
        ports = mido.get_output_names()
        if ports:
            print("\nTillgängliga MIDI-portar:")
            for i, port in enumerate(ports):
                print(f"  {i}: {port}")
        else:
            print("Inga MIDI-portar hittades")
        return ports
    else:
        print("Kan inte lista MIDI-portar - inget MIDI-bibliotek tillgängligt")
        return []

def send_midi_cc(midi_out, cc_number, value, channel=0):
    """Skicka MIDI Control Change"""
    if MIDO_AVAILABLE and midi_out:
        msg = mido.Message('control_change', channel=channel, control=cc_number, value=value)
        midi_out.send(msg)
        return True
    return False

def main():
    print("=== Sub Phatty MIDI Controller (Kommandoradsversion) ===\n")
    
    # Lista portar
    ports = list_midi_ports()
    if not ports:
        print("Ingen Sub Phatty hittades. Kontrollera att den är ansluten och påslagen.")
        return
    
    # Försök hitta Sub Phatty
    sub_phatty_port = None
    for port in ports:
        if 'sub phatty' in port.lower() or 'moog' in port.lower():
            sub_phatty_port = port
            break
    
    if not sub_phatty_port:
        print(f"\nKunde inte hitta Sub Phatty specifikt. Använder första porten: {ports[0]}")
        sub_phatty_port = ports[0]
    else:
        print(f"\n✓ Hittade Sub Phatty: {sub_phatty_port}")
    
    # Anslut
    if not MIDO_AVAILABLE:
        print("Kan inte ansluta - ingen MIDI-support")
        return
        
    try:
        midi_out = mido.open_output(sub_phatty_port)
        print("✓ MIDI-anslutning etablerad")
    except Exception as e:
        print(f"✗ Kunde inte ansluta till MIDI: {e}")
        return
    
    # Interaktiv loop
    print("\n=== Kommandon ===")
    print("LFO Wave Shape:")
    print("  l0 = Sine, l1 = Triangle, l2 = Square, l3 = S&H")
    print("VCO 1 Footage:")
    print("  v0 = 16', v1 = 8', v2 = 4', v3 = 2'")
    print("  q = Avsluta")
    print()
    
    while True:
        try:
            cmd = input("Sub Phatty> ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd.startswith('l') and len(cmd) == 2 and cmd[1].isdigit():
                # LFO Wave Shape
                value = int(cmd[1])
                if 0 <= value <= 3:
                    if send_midi_cc(midi_out, 24, value):  # CC #24 för LFO Wave
                        wave_names = ["Sine", "Triangle", "Square", "S&H"]
                        print(f"✓ LFO Wave: {wave_names[value]}")
                    else:
                        print("✗ Kunde inte skicka MIDI")
                else:
                    print("✗ LFO Wave värde måste vara 0-3")
            elif cmd.startswith('v') and len(cmd) == 2 and cmd[1].isdigit():
                # VCO 1 Footage
                value = int(cmd[1])
                if 0 <= value <= 3:
                    if send_midi_cc(midi_out, 15, value):  # CC #15 för VCO 1 Footage
                        footage_names = ["16'", "8'", "4'", "2'"]
                        print(f"✓ VCO 1 Footage: {footage_names[value]}")
                    else:
                        print("✗ Kunde inte skicka MIDI")
                else:
                    print("✗ VCO 1 Footage värde måste vara 0-3")
            else:
                print("✗ Okänt kommando. Använd l0-l3, v0-v3, eller q")
                
        except KeyboardInterrupt:
            print("\nAvbryter...")
            break
        except Exception as e:
            print(f"✗ Fel: {e}")
    
    # Stäng anslutning
    try:
        midi_out.close()
        print("MIDI-anslutning stängd")
    except:
        pass

if __name__ == "__main__":
    main()