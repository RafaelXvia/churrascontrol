# Guia de Configuração e Uso do Xano Developer MCP — ChurrasControl

## 1. Visão Geral
Este projeto utiliza o **Xano Developer MCP** (`@xano/developer-mcp`) para fornecer ao agente de Inteligência Artificial (GitHub Copilot, Gemini CLI ou Antigravity) acesso em tempo real à documentação oficial, referências de sintaxe e validação de código **XanoScript** (`.xs`).

O servidor foi configurado no projeto através do padrão aberto MCP (Model Context Protocol).

---

## 2. Arquivos de Configuração do Projeto

### VS Code & GitHub Copilot: `.vscode/mcp.json`
```json
{
  "servers": {
    "xano": {
      "command": "npx",
      "args": [
        "-y",
        "@xano/developer-mcp"
      ]
    }
  }
}
```

### Gemini CLI & Agentes Locais: `.gemini/settings.json`
```json
{
  "mcpServers": {
    "xano": {
      "command": "npx",
      "args": [
        "-y",
        "@xano/developer-mcp"
      ]
    }
  }
}
```

---

## 3. O que o Xano Developer MCP faz?
- **Documentação de XanoScript**: Consulta regras oficiais de tipagem, declarações de tabelas (`table PRODUTO { ... }`), filtros (`filters=trim`, `filters=min:0`) e índices.
- **Validação de Arquivos `.xs`**: Valida arquivos locais na pasta `xano/table/` e `xano/api/` antes da sincronização.
- **Documentação da Xano CLI**: Instruções oficiais para comandos como `xano workspace pull` e `xano workspace push`.
- **Documentação das APIs Meta & Run**: Consulta direta dos padrões de endpoints REST do Xano.
- **Segurança**: Opera localmente na máquina sem exigir tokens de administrador do Xano.

---

## 4. Como Ativar e Testar no VS Code

1. Abra o projeto no **VS Code** na pasta `crudfaculdade`.
2. Abra a Command Palette:
   - `Ctrl + Shift + P`
3. Digite e selecione:
   - **MCP: List Servers**
4. Localize o servidor **xano** e clique em **Start** (ou verifique o status verde de conectado).
5. No chat da IA (Copilot ou Gemini), você pode fazer perguntas diretas ou pedir validações de esquemas:
   - *"Valide o schema da tabela produto.xs utilizando a documentação oficial do Xano."*
   - *"Quais são os filtros suportados no XanoScript para campos de texto?"*

---

## 5. Diferenciação Importante (Diretrizes da Disciplina)
- **Language Server**: Responsável pelo realce de sintaxe no editor VS Code.
- **Xano CLI**: Responsável pela sincronização (`pull` e `push`) entre os arquivos `.xs` locais e a nuvem.
- **Xano Developer MCP**: Responsável por fornecer inteligência, documentação oficial e validação ao Agente de IA.
