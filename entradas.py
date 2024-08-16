import requests
import json
from ics import Calendar, Event

# Configuração de autenticação do Notion API
NOTION_API_KEY = 'secret_XORa2y02Ll03dMruX1tmpAovFwFTND3F7SjZKTQDV17'  # Substitua com sua chave de API do Notion
HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

# IDs dos bancos de dados de entradas
DATABASE_IDS = [
    "6c870692445042f588b8133e41dd82aa",
    "768a8af6d1d842a286e03fa183bfce76",
    "25d8162ad0c041dd9650904dc1030d2d",
    "1c7955e0d6ce40718b0b1647177f652d",
    "1601c179ba4141dba19f234def48128c",
    "77c6f53a6f014c33a86e971f3ef550cf",
]

# Função para consultar o database do Notion
def fetch_notion_data(database_id):
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    response = requests.post(url, headers=HEADERS)

    if response.status_code == 200:
        print(f"Dados recebidos com sucesso do database {database_id}")
        return response.json()
    else:
        print(f"Erro ao consultar o database {database_id}: {response.status_code}")
        return None

# Função para processar os dados e gerar eventos no iCal
def process_and_generate_ical(database_data, cal):
    if 'results' in database_data:
        for page in database_data['results']:
            properties = page['properties']
            
            # Captura o nome do evento (título)
            try:
                nome = properties['Nome']['title'][0]['text']['content']
            except (KeyError, IndexError):
                nome = "Evento sem título"

            # Captura o valor da quantia e formata como moeda brasileira
            try:
                quantia = properties['Quantia']['number']
                quantia_formatada = f"R$ {quantia:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (KeyError, IndexError):
                quantia_formatada = "N/A"

            # Verifica se o campo 'Lembrete' existe e se não é None
            try:
                if properties['Lembrete'] and properties['Lembrete']['date'] and properties['Lembrete']['date']['start']:
                    data = properties['Lembrete']['date']['start']
                else:
                    data = None
            except KeyError:
                data = None
            
            # Se a data for None, pula a criação do evento
            if data:
                # Montar a descrição do evento (apenas a quantia)
                descricao = f"Quantia: {quantia_formatada}"
                
                # Criar o evento All Day (sem horário definido)
                event = Event()
                event.name = nome  # Título do evento
                event.begin = data  # Data do evento
                event.make_all_day()  # Define o evento como All Day
                event.description = descricao  # Descrição contendo a quantia
                
                # Adicionar ao calendário
                cal.events.add(event)
            else:
                print(f"Evento '{nome}' ignorado por não ter data.")
    else:
        print("A chave 'results' não foi encontrada na resposta da API.")
    
    return cal

# Função principal para gerar o iCal com todos os bancos de dados
def generate_ical_for_databases():
    cal = Calendar()
    
    for db_id in DATABASE_IDS:
        notion_data = fetch_notion_data(db_id)
        
        # Verifica se os dados foram recebidos corretamente
        if notion_data:
            cal = process_and_generate_ical(notion_data, cal)
    
    # Salvar o arquivo .ics com o nome "entradas.ics"
    with open('entradas.ics', 'w') as my_file:
        my_file.writelines(cal)
    print("Arquivo iCal de Entradas gerado com sucesso!")

# Executar a função principal
if __name__ == "__main__":
    generate_ical_for_databases()