import requests
import json
from flask import Flask, request

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

    if started == False and job_ok == False and obrigatory == False and interest == False:
        started = True
        return "Olá. Seja bem vindo ao chatbot do SiDi. Me chamo SidX! Qual o código da sua vaga?"

    if started == True and job_ok == False and obrigatory == False and interest == False:
        if tries >= 3:
          restart_application()
          return "Não foi possível prosseguir. Tente mais tarde"

        check = check_job_id(message)
        if check == False:
          tries += 1
          return "Código da vaga não existe. Por favor, verifique e informe novamente."
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
                return "Ótimo! Agora vamos seguir para as perguntas da vaga. Responda 1 para SIM e 0 para NÃO para as seguintes perguntas. " + elim_questions[elim_count - 1]['pergunta']

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
            return elim_questions[elim_count - 1]['pergunta']
        else:
            for a in answers:
                if a == False:
                    rejected = True
            if rejected == True:
                restart_application()
                return "Esse conhecimento é obrigatório para essa vaga. Tente outras vagas disponíveis."
            else:
                obrigatory = True
                if obri_count - 1 < len(obri_questions) - 1:
                    obri_count += 1
                    return "Ok! Agora responda as seguintes perguntas: " + obri_questions[obri_count - 1]['pergunta']
                
    if started == True and job_ok == True and obrigatory == True and interest == False:

        answers.append(str(message))
        if obri_count - 1 < len(obri_questions) - 1:
            obri_count += 1
            return obri_questions[obri_count - 1]['pergunta']
        
        else:
            interest = True
            return "Confirmar sua aplicação à vaga? Digite 1 para SIM e 0 para NÃO."
        
    if started == True and job_ok == True and obrigatory == True and interest == True:

        if bool(int(message)) == True:
            job_application(answers, job_id)
            restart_application()
            return "Sua candidatura a vaga foi registrada com sucesso. Obrigado por participar. :D"
        else:
            restart_application()
            return "Confirmado sua desistência da vaga."



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020)