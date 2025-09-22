# RPG App API

Este projeto faz parte projeto final da Disciplina Desenvolvimento Full Stack Básico.

Esta API foi desenvolvida para gerenciar campanhas e anotações de jogos de RPG de mesa. O objetivo é permitir que mestres e jogadores organizem suas campanhas, criem notas de sessões e mantenham um registro organizado de suas aventuras.

## Funcionalidades

- **Gerenciamento de Campanhas**: Criar, listar, visualizar e excluir campanhas de RPG
- **Sistema de Notas**: Adicionar anotações e registros de sessões vinculados a campanhas específicas
- **API RESTful**: Interface padronizada para integração com aplicações frontend
- **Documentação Interativa**: Swagger UI integrado para testar endpoints
- **Persistência SQLite**: Banco de dados local criado automaticamente na primeira execução

## Como executar

Será necessário ter todas as libs python listadas no `requirements.txt` instaladas. Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

É fortemente indicado o uso de ambientes virtuais do tipo virtualenv.

```bash
(env)$ pip install -r requirements.txt
```

Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

**Nota**: Na primeira execução, o sistema criará automaticamente:
- O arquivo de banco de dados `database.db`
- O diretório `logs/` para arquivos de log
- Todas as tabelas necessárias no banco de dados

Para executar a API basta executar:

```bash
(env)$ flask run --host 0.0.0.0 --port 5000
```

Abra o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar o status da API em execução e acessar a documentação interativa.

## Endpoints Principais

### Campanhas
- `POST /campaigns` - Criar nova campanha
- `GET /campaigns` - Listar todas as campanhas
- `GET /campaigns/{campaign_id}` - Buscar campanha por ID

### Notas
- `POST /notes` - Criar nova nota
- `GET /notes` - Listar todas as notas
- `GET /campaigns/{campaign_name}/notes` - Listar notas de uma campanha específica pelo nome

## Estrutura do Projeto

- `app.py` - Aplicação principal Flask com definição dos endpoints
- `model.py` - Modelos de dados SQLAlchemy e configuração do banco
- `schemas.py` - Schemas Pydantic para validação
- `logger.py` - Configuração de logs
- `requirements.txt` - Dependências do projeto
- `database.db` - Banco de dados SQLite (criado automaticamente)
- `logs/` - Diretório de arquivos de log (criado automaticamente)
- `database.db` - Banco de dados SQLite (criado automaticamente)
- `logs/` - Diretório de arquivos de log (criado automaticamente)
- `logs/` - Diretório de arquivos de log (criado automaticamente)
