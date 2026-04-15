#!/usr/bin/env python3
"""
MONITORAMENTO DE BOMBA D'ÁGUA COM SUPABASE
univesp
Descrição: Monitora o contato auxiliar do contat da bomba e envia dados de monitoramento para o Supabase
"""

import RPi.GPIO as GPIO
import time
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# CARREGAR CONFIGURAÇÕES DO ARQUIVO .env

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
VAZAO_BOMBA = float(os.getenv('VAZAO_BOMBA', 5.0))  # padrão 5 m³/para testes // definir depois
SENSOR_PIN = int(os.getenv('SENSOR_PIN', 26))

# Configurações de tempo
INTERVALO_VERIFICACAO = 0.5  # segundos entre verificações (500m // considerar aumentar o tempo
TIMEOUT_RECONEXAO = 10  # segundos para tentar reconectar à internet


# VARIÁVEIS GLOBAIS
bomba_ligada = False
hora_ligou = None
tempo_acumulado_dia = 0  # segundos
volume_acumulado_dia = 0.0  # m³
ultimo_reset_dia = datetime.now().date()

# Buffer para envio em lote (evita perda se a internet cair)
buffer_eventos = []
TAMANHO_MAX_BUFFER = 10  # envia a cada 10 eventos se internet estiver OK / verificar a necessidade de alteração


# FUNÇÕES DE APOIO
def calcular_volume(segundos):
    """
    Calcula o volume em m³ baseado no tempo em segundos
    Fórmula: volume = vazão (m³/h) × tempo (horas)
    """
    horas = segundos / 3600
    return VAZAO_BOMBA * horas


def enviar_para_supabase(evento, duracao=0, volume=0):
    """
    Envia um evento para o Supabase via API REST
    Retorna True se sucesso, False se falha
    """
    global buffer_eventos

    # Monta o payload no formato suportado pelo Supabase
    payload = {
        "evento": evento,
        "timestamp": datetime.now().isoformat(),
        "duracao_segundos": duracao if duracao > 0 else None,
        "volume_m3": volume if volume > 0 else None,
        "vazao_bomba": VAZAO_BOMBA
    }

    # Adiciona ao buffer (arquivado localmente por segurança)
    buffer_eventos.append(payload)

    # Tenta enviar se o buffer atingiu o tamanho máximo ou se mudança de estado
    if len(buffer_eventos) >= TAMANHO_MAX_BUFFER or evento == 'DESLIGOU':
        return enviar_buffer()

    return True


def enviar_buffer():
    """
    Envia todos os eventos acumulados no buffer para o Supabase
    """
    global buffer_eventos

    if not buffer_eventos:
        return True

    # URL da API do Supabase (REST)
    url = f"{SUPABASE_URL}/rest/v1/bomba_eventos"

    # Headers necessários para autenticação
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    try:
        # Envia TODOS os eventos do buffer de uma vez (requisição em lote)
        response = requests.post(
            url,
            headers=headers,
            json=buffer_eventos,  # Supabase aceita array para inserção em lote
            timeout=10
        )

        if response.status_code in [200, 201, 204]:
            # Sucesso! Limpa o buffer
            print(f" {len(buffer_eventos)} evento(s) enviado(s) com sucesso")
            buffer_eventos = []
            return True
        else:
            print(f" Erro no envio: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f" Falha de conexão: {e}")
        # Mantém os eventos no buffer para tentar depois
        return False


def verificar_novo_dia():
    """
    Verifica se mudou o dia para resetar os acumuladores
    """
    global ultimo_reset_dia, tempo_acumulado_dia, volume_acumulado_dia

    hoje = datetime.now().date()
    if hoje > ultimo_reset_dia:
        print(f"\n--- NOVO DIA: {hoje} ---")
        print(f"Resumo do dia anterior: {tempo_acumulado_dia/3600:.2f} horas, {volume_acumulado_dia:.2f} m³")

        # Reset acumuladores
        tempo_acumulado_dia = 0
        volume_acumulado_dia = 0
        ultimo_reset_dia = hoje


def configurar_gpio():
    """
    Configura os pinos GPIO do Raspberry Pi
    """
    GPIO.setmode(GPIO.BCM)  # Usar numeração BCM (pinos por função, não posição física)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print(f"GPIO configurado. Monitorando pino {SENSOR_PIN}...")



# FUNÇÃO PRINCIPAL


def main():
    """
    Loop principal do programa
    """
    global bomba_ligada, hora_ligou, tempo_acumulado_dia, volume_acumulado_dia

    print("=" * 50)
    print("MONITORAMENTO DE BOMBA D'ÁGUA INICIADO")
    print(f"Vazão configurada: {VAZAO_BOMBA} m³/h")
    print(f"Pino GPIO: {SENSOR_PIN}")
    print(f"Supabase URL: {SUPABASE_URL}")
    print("=" * 50)
    print()

    configurar_gpio()

    # Pequena pausa para estabilizar
    time.sleep(2)

    try:
        while True:
            # Verifica se mudou o dia
            verificar_novo_dia()

            # Lê o estado atual do sensor (0 = desligado, 1 = ligado)
            estado_atual = GPIO.input(SENSOR_PIN)

            # DETECÇÃO DE LIGAMENTO (borda de subida: 0 → 1)
            if estado_atual == 1 and not bomba_ligada:
                bomba_ligada = True
                hora_ligou = time.time()

                horario = datetime.now().strftime("%H:%M:%S")
                print(f" [{horario}] BOMBA LIGOU")

                # Envia evento de ligamento para a nuvem
                enviar_para_supabase('LIGOU')


            # DETECÇÃO DE DESLIGAMENTO (borda de descida: 1 → 0)
            elif estado_atual == 0 and bomba_ligada:
                bomba_ligada = False

                # Calcula quanto tempo ficou ligada
                duracao = time.time() - hora_ligou
                tempo_acumulado_dia += duracao

                # Calcula o volume consumido
                volume = calcular_volume(duracao)
                volume_acumulado_dia += volume

                horario = datetime.now().strftime("%H:%M:%S")
                print(f" [{horario}] BOMBA DESLIGOU")
                print(f"   Duração: {duracao/60:.1f} minutos")
                print(f"   Volume: {volume:.3f} m³")
                print(f"   Acumulado hoje: {volume_acumulado_dia:.2f} m³")

                # Envia evento de desligamento (MAIS IMPORTANTE - contém os dados de consumo)
                enviar_para_supabase('DESLIGOU', duracao, volume)

            # Pequena pausa para não sobrecarregar a CPU
            time.sleep(INTERVALO_VERIFICACAO)

    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário")

        # Se a bomba estava ligada, registra o desligamento forçado
        if bomba_ligada:
            duracao = time.time() - hora_ligou
            volume = calcular_volume(duracao)
            print(f"Bomba estava ligada. Registrando desligamento forçado...")
            enviar_para_supabase('DESLIGOU', duracao, volume)

        # Tenta enviar o buffer antes de sair
        if buffer_eventos:
            print(f"Enviando {len(buffer_eventos)} eventos pendentes...")
            enviar_buffer()

        GPIO.cleanup()
        print("GPIO limpo. Programa encerrado.")



# PONTO DE ENTRADA DO PROGRAMA
if __name__ == "__main__":
    main()