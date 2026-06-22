# TimeKeeper

App desktop para gerenciamento de coleção de relógios de pulso.
Construído com Python + PyQt6. Dados salvos localmente em SQLite.

---

## Instalação

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes do Python)

Verifique: `python --version`

### 2. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/timekeeper.git
cd timekeeper
```

### 3. Crie um ambiente virtual (recomendado)

Um ambiente virtual isola as dependências deste projeto das do seu sistema.

```bash
# Criar
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (macOS / Linux)
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

Isso instala apenas o `PyQt6` — todo o resto (SQLite, dataclasses) já vem com o Python.

### 5. Execute

```bash
python main.py
```

---

## Estrutura do projeto

```
timekeeper/
├── main.py           # Ponto de entrada — execute este arquivo
├── database.py       # Toda a lógica do banco de dados (SQLite)
├── models.py         # Estruturas de dados (Watch, Category)
├── requirements.txt  # Dependências Python
├── .gitignore        # Arquivos ignorados pelo Git
├── README.md
└── ui/
    ├── __init__.py       # Marca 'ui' como pacote Python
    ├── main_window.py    # Janela principal do app
    ├── watch_form.py     # Formulário de adicionar/editar relógio
    └── styles.py         # Tema visual (cores, QSS)
```

### Como os arquivos se relacionam

```
main.py
  └── cria QApplication e MainWindow
        └── main_window.py  (usa database.py para ler/salvar dados)
              ├── watch_form.py  (formulário de relógio)
              └── styles.py      (tema visual)
                    └── models.py  (Watch, Category)
                          └── database.py  (SQLite)
```

---

## Onde os dados ficam

O banco de dados SQLite é salvo em:

- **Windows**: `C:\Users\SEU_USUARIO\.timekeeper\timekeeper.db`
- **macOS**: `/Users/SEU_USUARIO/.timekeeper/timekeeper.db`
- **Linux**: `/home/SEU_USUARIO/.timekeeper/timekeeper.db`

A pasta `.timekeeper` é criada automaticamente na primeira execução.
O arquivo `.db` **não é versionado** (está no `.gitignore`) — seus dados são privados.

---

## Campos por relógio

| Grupo | Campos |
|---|---|
| Identidade | Marca, modelo, referência, número de série, ano de fabricação, mercado de origem |
| Classificação | Categoria (customizável), status (owned / wishlist / sold / loaned) |
| Movimento | Tipo, calibre, origem (in-house / ébauche) |
| Caixa | Diâmetro, espessura, material, cristal, resistência à água |
| Mostrador | Cor, material |
| Pulseira | Material, fecho |
| Aquisição | Fonte, data, preço em BRL, preço em moeda original, caixa, papéis |
| Condição | Escala mint → poor, última revisão, próxima revisão estimada, seguro |
| Pessoal | Rating 1–5, à venda, observações livres |

---

## Categorias padrão

Dress · Sport · Dive · Pilot · Vintage · Casual · Pocket

Você pode criar categorias novas e escolher uma cor para cada uma.
Categorias padrão não podem ser deletadas.

---

## Roadmap (futuras versões)

- [ ] Foto por relógio
- [ ] Log de serviços (histórico de revisões)
- [ ] Exportação para CSV / PDF
- [ ] Estatísticas visuais (gráfico por categoria, por movimento)
- [ ] Perfil social — compartilhar coleção com outros colecionadores (requer backend)

---

## Tecnologias

| Tecnologia | Papel |
|---|---|
| Python 3.10+ | Linguagem principal |
| PyQt6 | Interface gráfica (janelas, botões, tabelas) |
| SQLite | Banco de dados local (arquivo .db) |
| QSS | Estilização visual (similar ao CSS) |
