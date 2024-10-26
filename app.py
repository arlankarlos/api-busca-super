from flask import Flask, request, jsonify
from buscar_e_agrupar import buscar_produto
from flask_cors import CORS
from utils.email_sender import send_email


app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas


@app.route("/api/produtos", methods=["POST"])
def buscar_produtos():
    data = request.get_json()  # Recebe os dados da requisição como JSON
    consulta = data.get("consulta")  # Acessa a chave 'consulta'

    if not consulta:
        return jsonify({"error": "Consulta não fornecida"}), 400

    try:
        produtos_agrupados = buscar_produto(
            consulta
        )  # Chama a função para buscar produtos
        return jsonify(produtos_agrupados)  # Retorna os produtos em formato JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Nova rota para enviar e-mail
@app.route("/api/send_email", methods=["POST"])
def enviar_email():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    # Monta a mensagem a ser enviada
    full_message = f"Nome: {name}\nE-mail: {email}\n\nMensagem:\n{message}"

    # Tenta enviar o e-mail
    try:
        send_email(to_email=email, subject=subject, message=full_message)
        return jsonify({"success": "E-mail enviado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', debug=True)
