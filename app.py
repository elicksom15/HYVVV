from flask import Flask, render_template_string, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# Função para enviar requisição POST
def send_request(datetime):
    try:
        payload = {
            'functionname': '',
            'datetime': datetime.replace('T', '+').replace(':', '%3A')
        }
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        response = requests.post("http://www.bixopix.com/bingo/venda_bilhetes.php", data=payload, headers=headers)
        return response.text
    except Exception as e:
        return str(e)

# Função para enviar requisições a cada 500ms
def send_requests_periodically(datetime):
    while True:
        response = send_request(datetime)
        print("Resposta do Servidor:", response)
        time.sleep(0.5)

# Rota principal
@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="pt">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bingo - Venda Bilhetes</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                    text-align: center;
                }
                input[type="text"] {
                    padding: 10px;
                    margin: 10px;
                    width: 250px;
                    font-size: 16px;
                }
                button {
                    padding: 10px 20px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                button:hover {
                    background-color: #45a049;
                }
                .status {
                    margin-top: 20px;
                    font-size: 18px;
                }
            </style>
        </head>
        <body>
            <h1>Venda de Bilhetes - Bingo</h1>
            <form id="datetime-form">
                <input type="text" id="datetime" placeholder="Digite o horário (ex: 2025-03-30 13:00:00)" required>
                <br>
                <button type="button" id="start-button">Iniciar</button>
                <button type="button" id="stop-button" style="background-color: #f44336;">Parar</button>
            </form>

            <div class="status" id="status"></div>

            <script>
                document.getElementById('start-button').addEventListener('click', function() {
                    const datetime = document.getElementById('datetime').value;
                    if (datetime) {
                        fetch('/start', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: `datetime=${datetime}`
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'started') {
                                document.getElementById('status').innerText = `Requisições iniciadas para ${data.datetime}`;
                            }
                        })
                        .catch(error => {
                            document.getElementById('status').innerText = 'Erro ao iniciar requisições';
                        });
                    } else {
                        document.getElementById('status').innerText = 'Por favor, insira um horário válido.';
                    }
                });

                document.getElementById('stop-button').addEventListener('click', function() {
                    fetch('/stop', {
                        method: 'POST',
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'stopped') {
                            document.getElementById('status').innerText = 'Requisições paradas.';
                        }
                    });
                });
            </script>
        </body>
        </html>
    ''')

# Rota para iniciar a requisição
@app.route('/start', methods=['POST'])
def start():
    datetime = request.form.get('datetime')
    if datetime:
        # Iniciar a thread que envia requisições a cada 500ms
        thread = threading.Thread(target=send_requests_periodically, args=(datetime,))
        thread.daemon = True  # A thread será encerrada quando o processo principal for encerrado
        thread.start()
        return jsonify({'status': 'started', 'datetime': datetime}), 200
    return jsonify({'status': 'error', 'message': 'Datetime missing'}), 400

# Rota para parar a execução
@app.route('/stop', methods=['POST'])
def stop():
    global stop_thread
    stop_thread = True
    return jsonify({'status': 'stopped'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181, debug=True)
