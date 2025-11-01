#!/usr/bin/env python3
"""
Sub Phatty SysEx Analyzer

Analyserar de SysEx-meddelanden vi fångade från Sub Phatty Editor
för att förstå hur parametrar ändras.
"""

def analyze_sysex_patterns():
    """
    Analysera de SysEx-mönster vi observerade från MIDI-monitorn
    
    Från monitorn såg vi:
    1. Moog SysEx header: 04 06 
    2. Två typer av meddelanden:
       - Korta: 04 06 06 00 00 00 00 00 00 00 00 00 00 00 00
       - Långa: 04 06 04 07 00 00 00 00 00 00 00 00 00 60 00 00 ... (mycket data)
    """
    
    print("=== Sub Phatty SysEx-analys ===")
    print()
    
    # Moog Manufacturer ID och Device ID
    print("Moog SysEx Header:")
    print("  04 = Moog Manufacturer ID") 
    print("  06 = Sub Phatty Device ID")
    print()
    
    # Observerade mönster
    print("Observerade SysEx-typer från Sub Phatty Editor:")
    print()
    
    print("1. Kort meddelande (förmodligen ACK eller status):")
    print("   04 06 06 00 00 00 00 00 00 00 00 00 00 00 00")
    print("   ^  ^  ^")
    print("   |  |  +-- Command: 06 (status/ack?)")  
    print("   |  +-- Device: Sub Phatty")
    print("   +-- Mfg: Moog")
    print()
    
    print("2. Långt meddelande (patch data):")
    print("   04 06 04 07 00 00 00 00 00 00 00 00 00 60 00 00 ...")
    print("   ^  ^  ^  ^")
    print("   |  |  |  +-- Sub-command: 07 (patch data?)")
    print("   |  |  +-- Command: 04 (write/send patch?)")
    print("   |  +-- Device: Sub Phatty") 
    print("   +-- Mfg: Moog")
    print()
    
    # Observationer om när meddelanden skickas
    print("Timing-observationer:")
    print("- Editor skickar först CC-meddelanden (feedback till användare)")
    print("- Därefter kommer långa SysEx-meddelanden med full patch-data")
    print("- SysEx verkar skriva över allt (därför kvarstår Editor-ändringar)")
    print("- Våra CC-meddelanden blir översrivna av SysEx från fysiska kontroller")
    print()
    
    # Strategi för lösning
    print("Strategier att testa:")
    print()
    print("1. FÖRSTÅ PATCH-FORMAT:")
    print("   - Begär patch-data från Sub Phatty")
    print("   - Ändra en parameter i Editor") 
    print("   - Begär patch-data igen")
    print("   - Jämför skillnaderna för att hitta parameter-positioner")
    print()
    
    print("2. EXPERIMENTERA MED SYSEX-KOMMANDON:")
    print("   - Testa olika kommando-bytes (04, 05, 06, 07...)")
    print("   - Försök skicka patch-data tillbaka")
    print("   - Testa partiella uppdateringar")
    print()
    
    print("3. KANAL-KORREKTION:")
    print("   - Alla meddelanden från Editor var på kanal 2")
    print("   - Vi har använt kanal 1 (därför fungerar inte våra CC)")
    print("   - Testa kanal 2 för både CC och SysEx")
    print()

def suggest_next_steps():
    """Föreslå nästa steg för att lösa problemet"""
    
    print("=== NÄSTA STEG ===")
    print()
    
    print("STEG 1: Testa korrekt MIDI-kanal")
    print("- Ändra våra CC-meddelanden till kanal 2")
    print("- Se om de håller längre (kanske fungerar utan SysEx)")
    print()
    
    print("STEG 2: Experimentera med SysEx-kommandon")
    print("- Skicka patch-request (04 06 06...)")
    print("- Analysera svarets format")
    print("- Försök modifiera och skicka tillbaka")
    print()
    
    print("STEG 3: Sekvens-analys")
    print("- Spela in exakt sekvens från Editor")
    print("- Replikera samma sekvens från vårt program")
    print("- Jämför resultat")
    print()

def create_test_commands():
    """Skapa några test-kommandon att prova"""
    
    print("=== TEST-KOMMANDON ATT PROVA ===")
    print()
    
    # SysEx kommandon baserat på observationer
    commands = {
        "patch_request": [0x04, 0x06, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        "patch_dump_header": [0x04, 0x06, 0x04, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60, 0x00, 0x00],
    }
    
    for name, data in commands.items():
        hex_str = " ".join([f"{b:02X}" for b in data])
        print(f"{name}:")
        print(f"  Bytes: {data}")
        print(f"  Hex:   {hex_str}")
        print(f"  mido.Message('sysex', data={data})")
        print()

if __name__ == "__main__":
    analyze_sysex_patterns()
    print()
    suggest_next_steps() 
    print()
    create_test_commands()
    
    print("=== SAMMANFATTNING ===")
    print()
    print("Huvudproblemet: Vi använde fel MIDI-kanal (1 istället för 2)")
    print("Lösningsförslag: Testa CC på kanal 2 först, sedan SysEx om det inte räcker")
    print("Editor använder SysEx för att säkerställa att ändringar kvarstår")
    print("Fysiska kontroller skickar förmodligen SysEx som överrider CC-meddelanden")