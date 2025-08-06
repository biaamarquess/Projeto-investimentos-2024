from flask import Flask, render_template, request,redirect, jsonify,session,url_for
import sqlite3
import plotly.graph_objs as go
import plotly.io as pio
import os

app = Flask(__name__)
app.secret_key = 'secreta_chave'  # Necessário para usar sessões

def get_db_connection():
    # Caminho absoluto para o banco de dados dentro de static/models
    db_path = os.path.join(os.path.dirname(__file__), 'static', 'models', 'investimento.db')
    conn = sqlite3.connect(db_path)  # Conecta ao banco de dados
    conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
    return conn

# Configuração existente
app.config['dados_login'] = []

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar se o usuário existe no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username  # Salva o nome de usuário na sessão
            return redirect(url_for('bemvindo'))  # Redireciona para a página de boas-vindas
        else:
            return "Login falhou. Usuário ou senha incorretos."

    return render_template('login.html')

@app.route('/bemvindo')
def bemvindo():
    return render_template('bemvindo.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']  # Captura o valor do nome
        username = request.form['username']
        password = request.form['password']

        # Verificar se o usuário já existe
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user_existente = cursor.fetchone()

        if user_existente:
            conn.close()
            return "Usuário já existe."

        # Salvar o novo usuário no banco de dados
        cursor.execute("INSERT INTO usuarios (nome, username, password) VALUES (?, ?, ?)", (nome, username, password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('cadastro.html')

# Rota para a página de simulação
@app.route('/simulacao')
def simulacao():
    return render_template('simulacao.html')

# Rota para processar a simulação
@app.route('/simular', methods=['POST'])
def simular():
    try:
        # Obtém os dados enviados pelo formulário
        aporte_inicial = float(request.form['aporte_inicial'])
        aporte_mensal = float(request.form['aporte_mensal'])
        taxa_juros = float(request.form['taxa_juros']) / 100  # Convertendo para decimal
        periodo = int(request.form['periodo'])

        print(f"Dados recebidos: Aporte inicial: {aporte_inicial}, Aporte mensal: {aporte_mensal}, Taxa juros: {taxa_juros}, Período: {periodo}")

        # Calcula os valores da simulação
        saldo = aporte_inicial
        valores = []
        for i in range(1, periodo + 1):
            saldo += aporte_mensal
            saldo *= (1 + taxa_juros)
            valores.append(saldo)

        # Cria o gráfico
        bar_data = go.Figure(
            data=[
                go.Bar(x=[f"Mês {i+1}" for i in range(periodo)], y=valores, marker=dict(color='#7E57C2'))
            ]
        )
        bar_data.update_layout(
            title="Simulação de Investimento",
            xaxis_title="Mês",
            yaxis_title="Saldo (R$)",
            template="plotly_white"
        )

        # Retorna o gráfico como HTML
        graph_html = pio.to_html(bar_data, full_html=False)
        return jsonify({'graph': graph_html})

    except Exception as e:
        print(f"Erro na simulação: {e}")
        return jsonify({'error': str(e)}), 400
    
app.run(host='127.0.0.1', port=80, debug=True)
