import os
import time
from google import genai
from dotenv import load_dotenv  # Importa a biblioteca para ler o .env

# 1. Carrega as variáveis do arquivo .env
load_dotenv()

# 2. Configuração da API - Agora pegando de forma segura
API_KEY = os.getenv("GEMINI_API_KEY")

# Verifica se a chave foi carregada corretamente para não dar erro depois
if not API_KEY:
    raise ValueError("Erro: A variável GEMINI_API_KEY não foi encontrada no arquivo .env")

client = genai.Client(api_key=API_KEY)

def realizar_upload(caminho):
    nome_arquivo = os.path.basename(caminho)
    print(f"Processando documento: {nome_arquivo}...")
    
    try:
        arquivo = client.files.upload(path=caminho)
        
        while arquivo.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            arquivo = client.files.get(name=arquivo.name)
            
        print(f"\n{nome_arquivo} carregado com sucesso.")
        return arquivo
    except Exception as e:
        print(f"\nErro no upload de {nome_arquivo}: {e}")
        raise

def gerar_recurso_multa(caminho_multa, caminho_condutor):
    # Upload dos documentos (Notificação de Autuação e CNH/CRLV)
    doc_multa = realizar_upload(caminho_multa)
    doc_infos = realizar_upload(caminho_condutor)

    # O Prompt Estratégico
    prompt = """
    Você é um advogado especialista em Direito de Trânsito Brasileiro. 
    Analise a Notificação de Autuação anexada e elabore um Recurso de Defesa Prévia robusto.

    Diretrizes:
    1. Identifique erros formais no Auto de Infração (falta de aferição do radar, erro de endereçamento, ausência de dados obrigatórios conforme o CTB).
    2. Baseie a fundamentação legal no Código de Trânsito Brasileiro (CTB) e nas Resoluções do CONTRAN.
    3. Use um tom formal, técnico e persuasivo.
    4. Estruture o texto com: Endereçamento (JARI/Órgão Autuador), Dos Fatos, Do Direito e Pedido de Deferimento/Anulação.
    5. Verifique se os dados do condutor/veículo no segundo documento batem com a multa.

    Retorne o texto pronto para ser copiado e colado em um documento oficial.
    """

    print("\nIniciando inteligência jurídica com Gemini 2.5 Flash...")
    
    try:
        # Usando o modelo 2.0 Flash conforme sua preferência de estabilidade
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[doc_multa, doc_infos, prompt]
        )
        
        if response:
            print("\n" + "="*60)
            print("MINUTA DO RECURSO DE MULTA GERADA")
            print("="*60)
            print(response.text)
            print("="*60)
            
    except Exception as e:
        print(f"\nErro na geração: {e}")

if __name__ == "__main__":
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    os.chdir(diretorio_script)
    
    # Arquivos necessários
    arquivo_multa = "notificacao_multa.pdf"
    arquivo_cliente = "documentos_cliente.pdf"
    
    if os.path.exists(arquivo_multa) and os.path.exists(arquivo_cliente):
        gerar_recurso_multa(arquivo_multa, arquivo_cliente)
    else:
        print(f"Erro: Certifique-se que {arquivo_multa} e {arquivo_cliente} estão na pasta.")