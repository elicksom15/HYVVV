from flask import Flask, render_template_string, request, jsonify
import threading
import time
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Bingo Automático</title>
    <script>
        let interval = null;
        function startRequests() {
            const datetime = document.getElementById('datetime').value;
            if (!datetime) {
                alert('Por favor, insira uma data e hora!');
                return;
            }
            document.getElementById('status').innerText = 'Enviando...';
            interval = setInterval(() => {
                fetch('/send_request', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({datetime: datetime})
                });
            }, 500);
        }
        function stopRequests() {
            clearInterval(interval);
            document.getElementById('status').innerText = 'Pausado';
        }
        function clearFields() {
            document.getElementById('datetime').value = '';
            document.getElementById('status').innerText = 'Aguardando...';
        }
    </script>
</head>
<body>
    <h1>Bingo Automático</h1>
    <input type="datetime-local" id="datetime">
    <button onclick="startRequests()">Iniciar</button>
    <button onclick="stopRequests()">Pausar</button>
    <button onclick="clearFields()">Apagar</button>
    <p>Status: <span id="status">Aguardando...</span></p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/send_request', methods=['POST'])
def send_request():
    data = request.json
    datetime = data.get('datetime')
    payload = {
        'functionname': '',
        'arguments[]': datetime.replace('T', '+')
    }
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    requests.post("http://www.bixopix.com/bingo/venda_bilhetes.php", data=payload, headers=headers)
    return jsonify({'status': 'sent'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181, debug=True)
