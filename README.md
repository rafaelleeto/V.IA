# VIA

## Instalação

`pip install flask flask_sqlalchemy flask_migrate python-dotenv`

## Migração

A migração de banco de dados é necessária para que o sistema possa crescer e se
adaptar sem perder informações importantes. Ela ajuda a atualizar a estrutura
dos dados, acompanhar novas funcionalidades e garantir que tudo continue
funcionando bem, mesmo com mudanças na tecnologia ou na forma como o sistema é
usado.

Para criar o banco de dados inicialmente:

`flask db init`

Para registrar uma migração depois de fazer uma mudança:

`flask --app app db migrate` `flask --app app db upgrade`

## Pastas

| Pasta            | Descrição                                                                      |
| ---------------- | ------------------------------------------------------------------------------ |
| controladores    | Contem os "controllers" do sistema, onde a logica (rotas) da aplicação ficarão |
| instance         | Criada pelo banco de dados, não mexer, _não deve_ ser parte do git             |
| migrations       | Criada pelo banco de dados, não mexer, _deve_ ser parte do git                 |
| modelos          | Modelos do banco de dados, classes para cada tabela + a classe modelo base     |
| vistas/templates | Onde os templates ficam                                                        |

## Controladores

Controladores devem criar um objeto `Blueprint` do modulo `flask` e ao inves de
criar rotas com `app.route` deve ser feito `blueprint.route`

Depois no seu app.py deve importar essa blueprint e registra-la

## Modelos

Modelos usam flask_sqlalchemy

São classes do python que definem colunas como membros da classe, foi criada uma
classe base `Modelo` com `id` e `data_criacao`

Outras classes definidas devem herdar essa classe base `Modelo` e definir suas
colunas com:

`nome_coluna = db.Column(db.TIPO, ...)`

Os tipos mais comuns são:

| Tipo               | Descrição                                           |
| ------------------ | --------------------------------------------------- |
| db.Integer         | Numeros inteiros                                    |
| db.Float           | Numeros reais                                       |
| db.String(tamanho) | Textos de tamanho definido (maximo)                 |
| db.Text            | Textos de tamanho não definido (sem tamanho maximo) |
| db.Boolean         | Booleanos                                           |
| db.DateTime        | Objetos do tipo `datetime` no python                |

Colunas tambem podem conter atributos como `unique=True`, `nullable=False`,
`default=0`

Esse projeto usa SQLAlchemy 1, existe uma verção mais nova SQLAlchemy 2, cuidado
ao procurar documentação, veja da verção mais "antiga"

## Vistas

Templates do flask

# .env

O projeto carrega valores secretos de um arquivo `.env`, esse arquivo deve estar
na pasta base do projeto (junto com o app.py) e deve conter a seguinte
estrutura:

```env
SECRET_KEY="sua_chave_secreta"
SQLALCHEMY_DATABASE_URI="sqlite:///via.sqlite3"
# Ou para um banco de dados postgres
SQLALCHEMY_DATABASE_URI="postgres://..."
```
