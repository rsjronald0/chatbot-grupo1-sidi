import requests
import json
from flask import Flask, request, jsonify
import nltk
from nltk.chat.util import Chat, reflections

pares = [
    [
        r"Oi|Olá|E aí|Ola|E ai",
        ["Oi! Me chamo SidX.", "Olá! Me chamo SidX."]
    ],
    [
        r"Ajuda|Menu",
        ["Sou o SidX, um chatbot para auxiliar na contratação da SiDi! Envie a palavra 'iniciar' para começar o processo."]
    ],
    # pode incluir outros pares de perguntas e respostas
]

chatbot = Chat(pares, reflections)

app = Flask(__name__)

def check_job_id(job_id):
    check_job = "http://127.0.0.1:5002/check?job_id=" + job_id
    response = requests.get(check_job).json()
    if response['resp'] == True:
        return True
    else:
        return False
    
def get_job_questions(job_id):
    job_questions = "http://127.0.0.1:5003/job_questions?job_id=" + job_id
    response = requests.get(job_questions).json()['resp']
    return response

def job_application(answers, job_id):
    application = {
        "id_vaga": int(job_id)
    }
    cnt = 1
    for answer in answers:
        exec("application['resp"+ str(cnt) + "'] =  str(answer)")
        cnt += 1

    url = 'http://127.0.0.1:5000/job_application'
    requests.post(url, json = application)

def restart_application():
    global started
    global tries
    global job_ok
    global job_id
    global questions
    global elim_questions
    global obri_questions
    global elim_count
    global obri_count
    global answers
    global rejected
    global obrigatory
    global interest

    started = False
    tries = 0
    job_ok = False
    job_id = 0
    questions = 0
    elim_questions = []
    obri_questions = []
    elim_count = 0
    obri_count = 0
    answers = []
    rejected = False
    obrigatory = False
    interest = False

started = False
tries = 0
job_ok = False
job_id = 0
questions = 0
elim_questions = []
obri_questions = []
elim_count = 0
obri_count = 0
answers = []
rejected = False
obrigatory = False
interest = False
@app.route("/chatbot", methods=["POST"])
def chat():
    global started
    global tries
    global job_ok
    global job_id
    global questions
    global elim_questions
    global obri_questions
    global elim_count
    global obri_count
    global answers
    global rejected
    global obrigatory
    global interest
    
    msg = json.loads(request.data)
    message = str(msg['mensagem'])

    if (message.lower() == 'iniciar' or  message.lower() == 'inicia' or message.lower() == 'inicio' or message.lower() == 'inici' or message.lower() == 'start'):
        restart_application()
        started = True

        data = "Olá. Seja bem vindo ao chatbot do SiDi. Me chamo SidX! Qual o código da sua vaga?"
        response = jsonify(data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    if (message.lower() == 'tchau' or  message.lower() == 'xau' or message.lower() == 'chau' or message.lower() == 'adeus' or message.lower() == 'bye'):
        restart_application()
        data = 'Até a próxima!'
        response = jsonify(data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    resposta = chatbot.respond(message)

    if (resposta):
        response = jsonify(resposta)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    else:
        if started == False and job_ok == False and obrigatory == False and interest == False:
            started = True
            
            data = "Olá. Seja bem vindo ao chatbot do SiDi. Me chamo SidX! Qual o código da sua vaga?"
            response = jsonify(data)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

        if started == True and job_ok == False and obrigatory == False and interest == False:
            if tries >= 3:
                restart_application()
                data = "Não foi possível prosseguir. Tente mais tarde"
                response = jsonify(data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response

            check = check_job_id(message)
            if check == False:
                tries += 1
                data = "Código da vaga não existe. Por favor, verifique e informe novamente."
                response = jsonify(data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            else:
                questions = get_job_questions(message)
                job_ok = True
                job_id = message

                if started == True and job_ok == True:
                    if len(elim_questions) == 0 or len(obri_questions) == 0:
                        for q in questions:
                            if q['tipo'] == 'eliminatoria':
                                elim_questions.append(q)
                            else: 
                                obri_questions.append(q)

                if elim_count - 1 < len(elim_questions):
                    elim_count += 1
                    data = "Ótimo! Agora vamos seguir para as perguntas da vaga. Responda 1 para SIM e 0 para NÃO para as seguintes perguntas. " + elim_questions[elim_count - 1]['pergunta']
                    response = jsonify(data)
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    return response

        if started == True and job_ok == True and obrigatory == False and interest == False:

            answers.append(bool(int(message)))
            if len(elim_questions) == 0 or len(obri_questions) == 0:
                    for q in questions:
                        if q['tipo'] == 'eliminatoria':
                            elim_questions.append(q)
                        else:
                            obri_questions.append(q)
            
            if elim_count - 1 < len(elim_questions) - 1:
                elim_count += 1
                data = elim_questions[elim_count - 1]['pergunta']
                response = jsonify(data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            else:
                for a in answers:
                    if a == False:
                        rejected = True
                if rejected == True:
                    restart_application()
                    data = "Esse conhecimento é obrigatório para essa vaga. Tente outras vagas disponíveis."
                    response = jsonify(data)
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    return response
                else:
                    obrigatory = True
                    if obri_count - 1 < len(obri_questions) - 1:
                        obri_count += 1
                        data = "Ok! Agora responda as seguintes perguntas: " + obri_questions[obri_count - 1]['pergunta']
                        response = jsonify(data)
                        response.headers['Access-Control-Allow-Origin'] = '*'
                        return response
                    
        if started == True and job_ok == True and obrigatory == True and interest == False:

            answers.append(str(message))
            if obri_count - 1 < len(obri_questions) - 1:
                obri_count += 1
                data = obri_questions[obri_count - 1]['pergunta']
                response = jsonify(data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            
            else:
                interest = True
                data = "Confirmar sua aplicação à vaga? Digite 1 para SIM e 0 para NÃO."
                response = jsonify(data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            
        if started == True and job_ok == True and obrigatory == True and interest == True:

            if bool(int(message)) == True:
                job_application(answers, job_id)
                restart_application()
                data = "Sua candidatura a vaga foi registrada com sucesso. Obrigado por participar. :D"
                response = jsonify(data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            else:
                restart_application()
                data = "Confirmado sua desistência da vaga."
                response = jsonify(data)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020)