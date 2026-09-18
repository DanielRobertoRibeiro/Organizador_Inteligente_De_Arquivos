# Estado atual do projeto

Atualizado em **18 de setembro de 2026**.

## Visão geral

| Área | Estado | Evidência |
| --- | --- | --- |
| Núcleo Python | ✅ Concluído | CLI, regras JSON, SHA-256, simulação, aplicação segura, CSV e logs. |
| Frontend React | ✅ Concluído | Vitrine responsiva e interativa em React 19 + TypeScript. |
| Regras compartilhadas | ✅ Concluído | React e Python consomem `config.example.json` como contrato. |
| Testes Python | ✅ Aprovado | 23 testes automatizados. |
| Testes frontend | ✅ Aprovado | 3 testes de classificação, duplicidade, colisão e CSV. |
| Build de produção | ✅ Aprovado | Vite gera artefatos estáticos otimizados. |
| CI | ✅ Configurado | GitHub Actions valida Python e React a cada push/PR. |
| GitHub Pages | 🟡 Configurado | A publicação depende da primeira execução bem-sucedida no GitHub. |
| Repositório remoto | 🟡 Preparado | O estado muda para concluído após o primeiro push para `main`. |

## O que o frontend faz

- recebe arquivos individuais, uma pasta ou drag-and-drop;
- classifica por extensão com as mesmas regras JSON da CLI;
- calcula SHA-256 localmente com Web Crypto;
- sinaliza conteúdos duplicados;
- resolve colisões de nomes na prévia;
- filtra o plano por estado e nome;
- exporta relatório CSV;
- não envia arquivos para serviços externos.

## Limite intencional da versão web

A interface web não move arquivos do dispositivo. Essa decisão evita depender de APIs experimentais e permissões diferentes entre navegadores. A aplicação real permanece na CLI Python, protegida pelo argumento explícito `--apply`.

## Próximos incrementos opcionais

- sincronizar configurações personalizadas do usuário entre a interface e a CLI;
- empacotar React + Python como aplicativo desktop com Tauri ou Electron;
- adicionar fluxo de reversão baseado no relatório CSV;
- criar análise recursiva com consentimento e limites explícitos;
- incluir testes visuais automatizados no CI.
