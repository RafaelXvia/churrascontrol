## 1. Configuração da Plataforma Discloud

- [x] 1.1 Criar o manifesto `discloud.config` com limites operacionais (512MB RAM, autorestart e entrypoint `run.py`).
- [x] 1.2 Criar o arquivo `.discloudignore` contendo todas as exclusões de desenvolvimento.

## 2. Orquestrador de Execução

- [x] 2.1 Implementar `run.py` executando o comando `streamlit run app.py` com bind nas portas de produção (`0.0.0.0:8080`).
- [x] 2.2 Integrar rotina de supressão do aviso ProactorEventLoop do Windows no topo de `app.py`.

## 3. Testes e Verificação

- [x] 3.1 Testar a execução do script `run.py` localmente assegurando que os parâmetros do Streamlit sejam passados corretamente.
- [x] 3.2 Verificar integridade do pacote compactado `churrascontrol_discloud.zip` respeitando as regras do `.discloudignore`.
