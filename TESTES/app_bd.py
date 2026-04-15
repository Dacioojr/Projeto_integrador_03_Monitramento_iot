# app_envio de dados ao BD.py
import supabase
import random
import time
from datetime import datetime

# Configurações
SUPABASE_URL = "https://yjdeuxpsfzmrzxlvhbhn.supabase.co"
SUPABASE_KEY = "sb_publishable_uywGVNAZNWfzx2ccQXmhnA_FXnv-lPo"

client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

print("Enviando dados (True/False)")
print("Campos: timestamp | valor (true/false)")
print("Pressione Ctrl+C para parar\n")

# Define o primeiro valor aleatoriamente
valor_atual = random.choice([True, False])
contador = 0

while True:
    contador += 1
    
    # Gerar dados com o valor atual
    dados = {
        'timestamp': datetime.now().isoformat(),
        'valor': valor_atual
    }
    
    # Enviar para o Supabase
    try:
        client.table('dados_estadoligado').insert(dados).execute()
        print(f" {dados['timestamp']}, Valor: {str(dados['valor']):5}")
        
        # Alterna o valor para o próximo envio
        valor_atual = not valor_atual
        
        # Gera intervalo aleatório entre 30 e 300 segundos (0.5 a 5 minutos)
        intervalo = random.randint(30, 300)
        print(f"Próximo envio em {intervalo} segundos...\n")
        time.sleep(intervalo)
        
    except Exception as e:
        print(f" Erro: {e}")
        time.sleep(10)  # Se erro, espera 10 segundos e tenta novamente