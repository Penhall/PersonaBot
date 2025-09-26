import tweepy
import yaml
from pathlib import Path

def load_credentials() -> dict:
    """Carrega as credenciais do arquivo credentials.yaml."""
    creds_path = Path(__file__).parent.parent.parent / "config" / "credentials.yaml"
    try:
        with open(creds_path, 'r') as file:
            return yaml.safe_load(file)['twitter']
    except FileNotFoundError:
        print("AVISO: `config/credentials.yaml` não encontrado. As funções do Twitter não funcionarão.")
        return None
    except Exception as e:
        print(f"Erro ao carregar credenciais: {e}")
        return None

class TwitterClient:
    def __init__(self):
        """Inicializa o cliente Tweepy."""
        creds = load_credentials()
        if creds:
            # A autenticação com a API v2 é um pouco diferente
            # Usaremos a v1.1 para postar e a v2 para ler, se necessário.
            # Para este exemplo, focamos na estrutura.
            auth = tweepy.OAuth1UserHandler(
                creds['consumer_key'], creds['consumer_secret'],
                creds['access_token'], creds['access_token_secret']
            )
            self.api_v1 = tweepy.API(auth)
            self.api_v2 = tweepy.Client(bearer_token="SUA_BEARER_TOKEN_AQUI") # Bearer token é necessário para a v2
        else:
            self.api_v1 = None
            self.api_v2 = None

    def get_recent_mentions(self, last_tweet_id: str = None):
        """Busca menções recentes ao bot."""
        if not self.api_v1:
            print("API do Twitter não inicializada. Impossível buscar menções.")
            return []
        
        print(f"Buscando menções desde o tweet ID: {last_tweet_id}")
        # Lógica para buscar menções usando self.api_v1.mentions_timeline
        # Exemplo:
        # mentions = self.api_v1.mentions_timeline(since_id=last_tweet_id)
        # return mentions
        return [] # Placeholder

    def post_reply(self, text: str, in_reply_to_tweet_id: str):
        """Posta uma resposta a um tweet específico."""
        if not self.api_v1:
            print("API do Twitter não inicializada. Impossível postar resposta.")
            return

        try:
            self.api_v1.update_status(
                status=text,
                in_reply_to_status_id=in_reply_to_tweet_id,
                auto_populate_reply_metadata=True
            )
            print(f"Resposta postada para o tweet {in_reply_to_tweet_id}")
        except Exception as e:
            print(f"Erro ao postar no Twitter: {e}")
