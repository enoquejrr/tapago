"""Exemplos de uso e configurações adicionais."""

# ============= EXEMPLO 1: CRIAR BOLETOS PROGRAMATICAMENTE =============
# Para testar localmente, crie um script test_data.py:

from storage_service import StorageService
from datetime import datetime, timedelta

storage = StorageService()

# Criar alguns boletos de teste
storage.create(
    descricao="Conta de Agua",
    valor=150.50,
    vencimento="2024-04-10",
    competencia="2024-04"
)

storage.create(
    descricao="Internet",
    valor=99.90,
    vencimento="2024-04-05",
    competencia="2024-04"
)

storage.create(
    descricao="Netflix",
    valor=39.90,
    vencimento="2024-04-15",
    competencia="2024-04"
)

print("✅ Dados de teste criados em data.json")


# ============= EXEMPLO 2: IMPORTAR DADOS (CSV para JSON) =============
# Se tiver uma planilha CSV, pode converter assim:

import csv
from storage_service import StorageService

def import_csv(csv_path: str):
    """Importa CSV para JSON."""
    storage = StorageService()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            storage.create(
                descricao=row['descricao'],
                valor=float(row['valor']),
                vencimento=row['vencimento'],  # YYYY-MM-DD
                competencia=row['competencia']  # YYYY-MM
            )
    
    print(f"✅ {csv_path} importado com sucesso!")

# Uso:
# import_csv("boletos.csv")


# ============= EXEMPLO 3: EXPORTAR DADOS (JSON para CSV) =============
import csv
from storage_service import StorageService

def export_csv(mes: str, output_path: str = "export.csv"):
    """Exporta boletos de um mês para CSV."""
    storage = StorageService()
    boletos = storage.get_by_month(mes)
    
    if not boletos:
        print(f"Nenhum boleto encontrado em {mes}")
        return
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['id', 'descricao', 'valor', 'vencimento', 'pago']
        )
        writer.writeheader()
        
        for b in boletos:
            writer.writerow({
                'id': b['id'],
                'descricao': b['descricao'],
                'valor': f"{b['valor']:.2f}",
                'vencimento': b['vencimento'],
                'pago': 'Sim' if b['pago'] else 'Não'
            })
    
    print(f"✅ Exportado em {output_path}")

# Uso:
# export_csv("2024-04", "boletos_abril.csv")


# ============= EXEMPLO 4: LISTAR BOLETOS VENCIDOS =============
from storage_service import StorageService
from utils import is_overdue, get_current_month

def listar_vencidos():
    """Lista todos os boletos vencidos."""
    storage = StorageService()
    boletos = storage.get_by_month(get_current_month())
    
    vencidos = [b for b in boletos if is_overdue(b['vencimento']) and not b['pago']]
    
    if vencidos:
        print("🔴 BOLETOS VENCIDOS:")
        for b in vencidos:
            print(f"  - {b['descricao']}: R${b['valor']:.2f} (Venc: {b['vencimento']})")
    else:
        print("✅ Nenhum boleto vencido!")

# Uso:
# listar_vencidos()


# ============= EXEMPLO 5: BACKUP AUTOMÁTICO =============
import shutil
import os
from datetime import datetime

def backup():
    """Cria backup de data.json."""
    if not os.path.exists("data.json"):
        print("Arquivo data.json não encontrado")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"data_backup_{timestamp}.json"
    shutil.copy("data.json", backup_name)
    print(f"✅ Backup criado: {backup_name}")

# Uso:
# backup()


# ============= EXEMPLO 6: RELATÓRIO MENSAL =============
from storage_service import StorageService
from utils import format_currency

def relatorio_mes(competencia: str):
    """Gera relatório completo de um mês."""
    storage = StorageService()
    boletos = storage.get_by_month(competencia)
    
    if not boletos:
        print(f"Nenhum boleto em {competencia}")
        return
    
    total = storage.get_total_month(competencia)
    pago = storage.get_total_paid_month(competencia)
    pendente = total - pago
    
    print(f"\n📊 RELATÓRIO - {competencia}")
    print(f"{'='*40}")
    print(f"Total de boletos: {len(boletos)}")
    print(f"Total: {format_currency(total)}")
    print(f"Pago: {format_currency(pago)}")
    print(f"Pendente: {format_currency(pendente)}")
    print(f"{'='*40}")
    
    pago_count = sum(1 for b in boletos if b['pago'])
    percentual = (pago_count / len(boletos)) * 100 if boletos else 0
    print(f"Taxa de pagamento: {percentual:.1f}%")

# Uso:
# relatorio_mes("2024-04")


# ============= DICAS =============
"""
1. Backup regular:
   - Faça backup de data.json periodicamente
   - Use a função backup() acima

2. Limpeza de dados antigos:
   - Após 12 meses, delete boletos muito antigos
   - Use storage.delete(boleto_id)

3. Recorrência automática:
   - Copie boletos do mês anterior
   - Atualize apenas a data de vencimento

4. Integração com Google Sheets:
   - Exporte CSV e importe no Google Sheets para visualizações

5. Sincronização entre dispositivos:
   - Use Dropbox/Google Drive para sincronizar data.json
   - Coloque a pasta do projeto lá
"""
