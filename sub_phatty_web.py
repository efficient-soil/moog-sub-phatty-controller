#!/usr/bin/env python3
"""
Sub Phatty Web Controller

En webbaserad controller som fungerar i vilken webbläsare som helst.
Kringgår tkinter-problem på äldre macOS-versioner.
"""

import mido
import http.server
import socketserver
import urllib.parse
import json
import threading
import webbrowser
import time
import os

class SubPhattyWebController:
    def __init__(self):
        self.outport = None
        self.midi_channel = 1  # Kanal 2 (0-indexerat)
        
        # CC-nummer från officiella MIDI-specen
        self.lfo_cc = 71
        self.lfo_rate_cc = 3
        self.vco_cc = 74
        
        # Värden från officiella specen
        self.lfo_values = {
            'Triangle': 0,
            'Square': 16, 
            'Saw': 32,
            'Ramp': 48,
            'Sample & Hold': 64,
            'Filter Envelope': 80
        }
        
        self.vco_values = {
            "16'": 16,
            "8'": 32,
            "4'": 48,
            "2'": 64
        }
        
        self.log_messages = []
        self.connect_midi()
    
    def log(self, message):
        """Lägg till meddelande i loggen"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        print(log_entry)  # Visa också i terminalen
        
        # Behåll bara senaste 50 meddelanden
        if len(self.log_messages) > 50:
            self.log_messages = self.log_messages[-50:]
    
    def connect_midi(self):
        """Anslut till Sub Phatty via MIDI"""
        try:
            output_ports = mido.get_output_names()
            
            sub_phatty_port = None
            for port in output_ports:
                if 'Sub Phatty' in port or 'Moog' in port:
                    sub_phatty_port = port
                    break
            
            if sub_phatty_port:
                self.outport = mido.open_output(sub_phatty_port)
                self.log(f"✓ Ansluten till: {sub_phatty_port}")
                self.log("Använder MIDI-kanal 2 (som Sub Phatty Editor)")
                return True
            else:
                self.log("✗ Ingen Sub Phatty hittades")
                return False
                
        except Exception as e:
            self.log(f"✗ MIDI-anslutningsfel: {e}")
            return False
    
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
            return False
            
        value = self.lfo_values[wave]
        success = self.send_cc(self.lfo_cc, value, f"LFO Wave: {wave}")
        
        if success:
            self.log(f"🎵 LFO inställt till: {wave}")
        return success
    
    def set_vco_octave(self, octave):
        """Sätt VCO 1 oktav"""
        if octave not in self.vco_values:
            self.log(f"✗ Okänd VCO-oktav: {octave}")
            return False
            
        value = self.vco_values[octave]
        success = self.send_cc(self.vco_cc, value, f"VCO Octave: {octave}")
        
        if success:
            self.log(f"🎵 VCO oktav inställt till: {octave}")
        return success
    
    def set_lfo_rate(self, rate):
        """Sätt LFO rate (0-127)"""
        rate_int = int(rate)
        if rate_int < 0 or rate_int > 127:
            self.log(f"✗ LFO rate måste vara 0-127, fick: {rate_int}")
            return False
            
        success = self.send_cc(self.lfo_rate_cc, rate_int, f"LFO Rate: {rate_int}")
        
        if success:
            self.log(f"🎵 LFO rate inställt till: {rate_int}")
        return success
    
    def get_html_page(self):
        """Generera HTML-sidan"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Sub Phatty Controller</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .status {
            text-align: center;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
            font-weight: bold;
        }
        .status.connected { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .section {
            margin-bottom: 25px;
            padding: 20px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
        }
        .section h3 {
            margin-top: 0;
            color: #495057;
        }
        .button-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .lfo-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        button {
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            background: #007bff;
            color: white;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #0056b3;
        }
        button:active {
            background: #004085;
        }
        .slider-container {
            margin-top: 15px;
        }
        .slider {
            width: 100%;
            height: 8px;
            border-radius: 4px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #007bff;
            cursor: pointer;
        }
        .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #007bff;
            cursor: pointer;
            border: none;
        }
        .slider-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            font-size: 12px;
            color: #666;
        }
        .slider-labels span:nth-child(2) {
            font-weight: bold;
            color: #007bff;
        }
        .log {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
        }
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        .controls button {
            background: #6c757d;
            margin: 0 5px;
        }
        .controls button:hover {
            background: #545b62;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎹 Moog Sub Phatty Controller</h1>
        <div id="status" class="status">Ansluter...</div>
        
        <div class="section">
            <h3>LFO Wave Shape</h3>
            <div class="lfo-grid">
                <button onclick="setLFO('Triangle')">Triangle</button>
                <button onclick="setLFO('Square')">Square</button>
                <button onclick="setLFO('Saw')">Saw</button>
                <button onclick="setLFO('Ramp')">Ramp</button>
                <button onclick="setLFO('Sample & Hold')">Sample & Hold</button>
                <button onclick="setLFO('Filter Envelope')">Filter Envelope</button>
            </div>
            
            <h4>LFO Rate</h4>
            <div class="slider-container">
                <input type="range" id="lfoRate" min="0" max="127" value="64" class="slider" oninput="setLFORate(this.value)">
                <div class="slider-labels">
                    <span>Slow (0)</span>
                    <span id="lfoRateValue">64</span>
                    <span>Fast (127)</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3>VCO 1 Octave</h3>
            <div class="button-grid">
                <button onclick="setVCO('16\\'')">16'</button>
                <button onclick="setVCO('8\\'')">8'</button>
                <button onclick="setVCO('4\\'')">4'</button>
                <button onclick="setVCO('2\\'')">2'</button>
            </div>
        </div>
        
        <div class="section">
            <h3>Status Log</h3>
            <div id="log" class="log"></div>
        </div>
        
        <div class="controls">
            <button onclick="reconnectMIDI()">Återanslut MIDI</button>
            <button onclick="clearLog()">Rensa Log</button>
            <button onclick="updateLog()">Uppdatera</button>
        </div>
    </div>

    <script>
        let updateInterval;
        
        function sendCommand(command, param) {
            fetch(`/${command}?param=${encodeURIComponent(param)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateStatus();
                        updateLog();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        
        function setLFO(wave) {
            sendCommand('lfo', wave);
        }
        
        function setVCO(octave) {
            sendCommand('vco', octave);
        }
        
        function setLFORate(rate) {
            // Uppdatera visningen
            document.getElementById('lfoRateValue').textContent = rate;
            
            // Skicka till servern
            fetch('/lfo_rate?param=' + encodeURIComponent(rate))
                .then(response => response.json())
                .then(data => {
                    updateLog();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        
        function reconnectMIDI() {
            fetch('/reconnect')
                .then(response => response.json())
                .then(data => {
                    updateStatus();
                    updateLog();
                });
        }
        
        function clearLog() {
            fetch('/clear_log')
                .then(response => response.json())
                .then(data => {
                    updateLog();
                });
        }
        
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const statusEl = document.getElementById('status');
                    if (data.connected) {
                        statusEl.textContent = '✓ Ansluten till Sub Phatty';
                        statusEl.className = 'status connected';
                    } else {
                        statusEl.textContent = '✗ Ingen anslutning';
                        statusEl.className = 'status error';
                    }
                });
        }
        
        function updateLog() {
            fetch('/log')
                .then(response => response.json())
                .then(data => {
                    const logEl = document.getElementById('log');
                    logEl.textContent = data.log.join('\\n');
                    logEl.scrollTop = logEl.scrollHeight;
                });
        }
        
        // Auto-uppdatera varje 2 sekunder
        function startAutoUpdate() {
            updateStatus();
            updateLog();
            updateInterval = setInterval(() => {
                updateStatus();
                updateLog();
            }, 2000);
        }
        
        // Starta när sidan laddas
        window.onload = startAutoUpdate;
        
        // Stoppa auto-update när sidan lämnas
        window.onbeforeunload = () => {
            if (updateInterval) clearInterval(updateInterval);
        };
    </script>
</body>
</html>
        """

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, controller, *args, **kwargs):
        self.controller = controller
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Hantera GET-förfrågningar"""
        
        # Logga inte tillgångsförfrågningar för att hålla loggen ren
        if self.path != '/log' and self.path != '/status':
            print(f"Request: {self.path}")
        
        if self.path == '/':
            # Huvudsidan
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.controller.get_html_page().encode('utf-8'))
            
        elif self.path.startswith('/lfo?'):
            # LFO-kommando
            params = urllib.parse.parse_qs(self.path.split('?')[1])
            wave = params.get('param', [''])[0]
            success = self.controller.set_lfo_wave(wave)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': success}).encode('utf-8'))
            
        elif self.path.startswith('/vco?'):
            # VCO-kommando
            params = urllib.parse.parse_qs(self.path.split('?')[1])
            octave = params.get('param', [''])[0]
            success = self.controller.set_vco_octave(octave)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': success}).encode('utf-8'))
            
        elif self.path.startswith('/lfo_rate?'):
            # LFO Rate-kommando
            params = urllib.parse.parse_qs(self.path.split('?')[1])
            rate = params.get('param', [''])[0]
            success = self.controller.set_lfo_rate(rate)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': success}).encode('utf-8'))
            
        elif self.path == '/reconnect':
            # Återanslut MIDI
            self.controller.connect_midi()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
            
        elif self.path == '/clear_log':
            # Rensa logg
            self.controller.log_messages.clear()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
            
        elif self.path == '/status':
            # Status
            connected = self.controller.outport is not None
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'connected': connected}).encode('utf-8'))
            
        elif self.path == '/log':
            # Logg-meddelanden
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'log': self.controller.log_messages}).encode('utf-8'))
            
        else:
            # 404
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Stäng av HTTP-server loggning"""
        pass

def get_local_ip():
    """Hämta lokal IP-adress"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Anslut till Google DNS för att få lokal IP
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.xxx"  # Fallback om det misslyckas

def run_web_server(controller, port=8080):
    """Starta webbservern"""
    
    handler = lambda *args, **kwargs: RequestHandler(controller, *args, **kwargs)
    local_ip = get_local_ip()
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n🌐 Sub Phatty Web Controller startad!")
        print(f"� På denna Mac: http://localhost:{port}")
        print(f"📱 Från iPhone/iPad: http://{local_ip}:{port}")
        print(f"⏹️  Tryck Ctrl+C för att avsluta\n")
        
        # Försök öppna webbläsare automatiskt
        try:
            webbrowser.open(f'http://localhost:{port}')
        except:
            pass  # Inte så viktigt om det misslyckas
            
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Stänger ner server...")
            if controller.outport:
                controller.outport.close()

if __name__ == "__main__":
    controller = SubPhattyWebController()
    run_web_server(controller)