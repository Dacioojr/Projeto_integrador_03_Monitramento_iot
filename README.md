README — Projeto Integrador III (UNIVESP)
 Título do Projeto:
Sistema de Monitoramento Remoto de Consumo de Água em Poço Artesiano com IoT e Análise de Dados e raspberry pi

Descrição: 
Este projeto, desenvolvido no âmbito do Projeto Integrador III da UNIVESP, tem como objetivo a criação de uma aplicação web integrada a um sistema de aquisição de dados baseado em IoT, voltada ao monitoramento remoto do consumo de água de um poço artesiano.

A solução permite:
Monitoramento em tempo real
Consolidação de consumo diário, semanal e mensal
Geração de relatórios analíticos
Identificação de anomalias e possíveis vazamentos
Visualização de indicadores de desempenho (KPIs)

Motivação:
Poços artesianos são amplamente utilizados em áreas rurais e industriais, porém frequentemente carecem de sistemas de monitoramento confiáveis, aliado a necessidade de relatórios ambientais sobre o uso da água, e considerando muitas vezes a distância e o risco de acesso aos locais (para industrias).

A ausência de dados estruturados dificulta:
Controle de consumo
Detecção de desperdícios
Planejamento de manutenção

Este projeto busca resolver esse problema através de uma abordagem de baixo custo, escalável e baseada em dados.

Arquitetura do Sistema

O sistema é dividido em três camadas principais:

1. Camada de Aquisição (IoT)
Dispositivo: Raspberry Pi 4B+
Interface: GPIO
Fonte de dados:
Contator de acionamento da bomba
Funcionamento:
O estado do contator (ligado/desligado) é monitorado
Cada acionamento é registrado com timestamp
Os dados são enviados para processamento

2. Camada de Processamento
A partir dos dados coletados, é aplicada uma modelagem matemática para estimar a vazão:

Cálculo da Vazão

A vazão não é medida diretamente. Em vez disso:
Considera-se uma vazão nominal da bomba
O tempo de funcionamento é utilizado como variável principal

	​
3. Camada de Aplicação Web
Responsável por:
Visualização dos dados
Consolidação de consumo
Geração de relatórios
Apresentação de indicadores

Funcionalidades:
Dashboard em tempo real
Consumo por período: Diário Semanal Mensal
Gráficos históricos
Alertas de anomalias
Indicadores de desempenho (KPIs)
Banco de Dados

O sistema utiliza um banco de dados relacional para armazenar:
Eventos de acionamento da bomba
Tempo de funcionamento
Consumo estimado
Dados agregados para relatórios
Exemplo de dados armazenados:
timestamp	              evento         	duração   	volume_estimado
30/03/2026 08:00	       ligou            1h	          3.6 m³

Análise de Dados
O projeto implementa análise de dados para:
Consolidação
Soma de consumo por período
Média de consumo
Detecção de Anomalias
Funcionamento fora do padrão esperado
Tempo excessivo de operação
Previsão de Vazamentos

Baseado em:
Aumento progressivo do tempo de operação
Consumo acima da média histórica

Tecnologias Utilizadas

Hardware: 
Raspberry Pi 4B+
Interface GPIO
Contator da bomba

Software: 
Backend: (ex: Python / Node.js)
Banco de Dados: (ex: PostgreSQL / MySQL)
Frontend: (ex: HTML, CSS, JavaScript)

Conceitos Aplicados:
IoT (Internet das Coisas)
Sistemas embarcados
Análise de dados
Modelagem matemática
Monitoramento remoto

Fluxo de Funcionamento:
A bomba é acionada (contator fecha)
O Raspberry Pi detecta o evento via GPIO
O sistema registra:
Timestamp de início
A bomba é desligada
O sistema registra:
Timestamp de fim
O tempo de funcionamento é calculado
O volume estimado é gerado
Os dados são armazenados no banco
A aplicação web exibe as informações
Indicadores de Desempenho (KPIs)
Tempo total de operação
Volume consumido
Frequência de acionamento
Consumo médio por período
Índice de anomalias

Limitações
A vazão é estimada, não medida diretamente
Depende da constância da vazão nominal da bomba podendo esta ser ajustada (no código) conforme calibrações periódicas.

Possíveis Melhorias
Integração com sensor de vazão real
Uso de machine learning para previsão mais precisa
Aplicativo mobile
Integração com sistemas SCADA
Alarmes em tempo real (SMS/WhatsApp)

Contexto Acadêmico

Projeto desenvolvido como parte do:

Curso: Tecnologia da Informação
Instituição: UNIVESP
Disciplina: Projeto Integrador III

Conclusão

O projeto demonstra a aplicação prática de conceitos de:

IoT
Engenharia de dados
Automação
Sistemas web

Proporcionando uma solução eficiente para monitoramento e gestão de recursos hídricos, com aplicação real em ambientes industriais
