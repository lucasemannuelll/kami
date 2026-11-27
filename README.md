# kami

Um registro de leitura minimalista para mangás, manhwas, manhuas, web novels, quadrinhos e afins. Uma CLI pequena e rápida, com SQLite por baixo.

O `kami` acompanha o que você está lendo, o que já leu e quando. Ele foi feito para não atrapalhar: um único arquivo de banco de dados, poucos de comandos e flag `--json` para usar em scripts.

---

## Recursos

- **Acompanhamento de séries**: título, tipo, autor, status e a data em que você começou a ler
- **Registro de capítulos**: registre capítulos avulsos, intervalos e capítulos decimais (`12.1,12.2,13`)
- **Datas de leitura**: registre quando você leu ou preencha retroativamente com `--date`
- **Busca aproximada**: refira-se a uma série por qualquer trecho único do título; ambiguidades são informadas de forma clara
- **Filtro por tags**: `--tag` pode ser repetido, com semântica AND
- **Saída para máquinas**: `--json` em todos os comandos de dados (`init`, `add`, `list`, `show`, `edit`, `rm`, `log`, `unlog`, `db path`); `db shell` é interativo e ignora essa opção
- **Simulação**: `--dry-run` em `log` e `unlog`
- **Inspeção direta**: abra o banco num shell `sqlite3` já configurado

---

## Instalação

Comece clonando o repositório e entrando nele. Os comandos de instalação abaixo assumem que você está dentro do diretório do repositório:

```bash
git clone <repository-url>
cd kami
```

### Opção 1: `uv` (recomendado)

O [`uv`](https://docs.astral.sh/uv/) instala a CLI num ambiente isolado e cria um link para o executável `kami` em `~/.local/bin`.

```bash
uv tool install .
```

Para desenvolvimento (alterações no código-fonte são aplicadas sem reinstalar):

```bash
uv tool install --editable .
```

Se o comando `kami` não for encontrado depois disso, adicione `~/.local/bin` ao seu `PATH`:

```bash
uv tool update-shell
```

…depois reinicie o terminal (ou recarregue o perfil do seu shell).

---

### Opção 2: `pipx`

O [`pipx`](https://pipx.pypa.io/) cria um ambiente virtual dedicado para o `kami` e expõe o executável no seu `PATH`.

```bash
pipx install .
```

Para desenvolvimento:

```bash
pipx install --editable .
```

Se aparecer um erro de "command not found", verifique se o diretório de binários do pipx está no seu `PATH` (geralmente `~/.local/bin` no Linux/macOS):

```bash
pipx ensurepath
```

…depois reinicie o terminal.

---

### Opção 3: `pip`

O `pip` instala o `kami` e suas dependências no seu **user site-packages**.
Use a flag `--user` para não alterar o Python do sistema.

```bash
pip install --user .
```

Para desenvolvimento:

```bash
pip install --user --editable .
```

> Diferente do `uv` e do `pipx`, o `pip` **não** isola as dependências do `kami`.
> Elas são compartilhadas com quaisquer outros pacotes instalados no mesmo ambiente,
> o que pode causar conflitos de versão com o tempo. Prefira `uv` ou `pipx`, a menos
> que você esteja trabalhando dentro de um ambiente virtual dedicado (por exemplo, `python -m venv .venv`).

Se o `kami` não for encontrado, confira se o diretório de scripts do usuário está no seu `PATH`:
- **Linux/macOS:** `~/.local/bin`
- **Windows:** `%APPDATA%\Python\Scripts`

---

### Verificar a instalação

```bash
kami --help
```

---

### Desinstalar

```bash
uv tool uninstall kami       # se instalou com uv
pipx uninstall kami          # se instalou com pipx
pip uninstall kami           # se instalou com pip
```

---

## Início rápido

```bash
# Cria o banco de dados e o schema
kami init

# Adiciona uma série (--started = a data em que você começou a lê-la)
kami add "Frieren" --type Manga --author "Kanehito Yamada" \
    --tag fantasy --tag adventure --started 2026-11-01

# Registra os capítulos 1 a 10
kami log Frieren 1-10

# Registra uma data específica
kami log Frieren 11 --date 2026-11-02

# Vê tudo
kami list

# Mostra os detalhes de uma série
kami show Frieren
```

---

## Opções globais

Valem para todos os comandos:

| Opção             | Descrição                                                   |
| ----------------- | ----------------------------------------------------------- |
| `--db PATH`       | Caminho para o banco SQLite (substitui `$KAMI_DB`)          |
| `--json`          | Saída em JSON para máquinas                                 |
| `--verbose`, `-v` | Imprime informações de depuração (SQL, comandos executados) |

`--json` vale para todos os comandos de dados listados em Recursos. `db shell` é interativo e ignora essa opção (passe argumentos extras depois de `db shell`).

---

## Comandos

### `kami init`

Cria o banco de dados e o schema (cria diretórios pais conforme necessário).

```bash
kami init
kami init --json
```

---

### `kami add`

Adiciona uma série ao registro.

```bash
kami add TITLE --type TYPE [--author AUTHOR] [--status STATUS] [--tag TAG]... [--started DATE]
```

- `--type`, `-t`: um de `Manga`, `Manhwa`, `Manhua`, `Novel`, `Comic`
- `--status`, `-s`: um de `Reading`, `Completed`, `On Hold`, `Dropped` (padrão: `Reading`)
- `--author`, `-a`: autor opcional
- `--tag`: pode ser repetido
- `--started`: a data em que **você** começou a ler esta série (`YYYY-MM-DD`, ou `pre-catalog` se você começou antes de usar o `kami`). É uma data pessoal de início de leitura, não a data de publicação da série.

```bash
kami add "Vinland Saga" -t Manga -a "Makoto Yukimura" --tag historical --started 2005-04-01
```

---

### `kami list`

Lista séries, opcionalmente com filtros.

```bash
kami list [--status STATUS] [--type TYPE] [--tag TAG]...
```

Os filtros são combinados com AND. Repetir `--tag` exige *todas* as tags listadas.

```bash
kami list --status Reading
kami list --type Manhwa --tag romance --tag drama
kami list --json
```

---

### `kami show`

Mostra os metadados de uma série e seus 3 capítulos mais recentes.

```bash
kami show QUERY
```

`QUERY` pode ser o título completo ou qualquer trecho único do título.

---

### `kami edit`

Renomeia, altera status/autor ou adiciona/remove tags.

```bash
kami edit QUERY [--title NEW_TITLE] [--status STATUS] [--author AUTHOR] \
                [--add-tags TAG]... [--remove-tags TAG]...
```

```bash
kami edit Frieren --status Completed
kami edit Frieren --add-tags magic --remove-tags adventure
```

---

### `kami rm`

Remove uma série e, em cascata, seus capítulos e vínculos de tags. Pede confirmação, a menos que `--yes` seja usado.

```bash
kami rm QUERY [--yes]
```

Em contextos não interativos (scripts, pipes), `--yes` é obrigatório.

---

### `kami log`

Registra capítulos como lidos.

```bash
kami log QUERY SPEC [--date YYYY-MM-DD] [--dry-run]
```

`SPEC` aceita itens separados por vírgula, intervalos e decimais:

```bash
kami log Frieren 12
kami log Frieren 13-20
kami log Frieren 21.1,21.2,22
kami log Frieren 1-5 --date 2026-10-01
kami log Frieren 1-5 --dry-run
```

Com `--dry-run`, o comando informa quais capítulos seriam adicionados e quais seriam atualizados, sem gravar nada.

---

### `kami unlog`

O inverso de `log`. Remove as linhas de capítulos por completo. Útil para desfazer registros acidentais.

```bash
kami unlog QUERY SPEC [--yes] [--dry-run]
```

- `--yes`, `-y`: pula a confirmação
- `--dry-run`: mostra quais capítulos seriam removidos, sem gravar nada

Remover 10 ou mais capítulos exige confirmação e, em contextos não interativos (scripts, pipes), exige `--yes`.

```bash
kami unlog Frieren 11
kami unlog Frieren 12-15 --dry-run
kami unlog Frieren 12-20 --yes
```

---

### `kami db`

Manutenção e inspeção do banco de dados.

#### `kami db path`

Imprime o caminho resolvido do banco de dados. Com `--json`, também informa `exists` e `size`.

```bash
kami db path
kami db path --json
```

#### `kami db shell`

Abre um shell `sqlite3` interativo no banco de dados, já configurado com `.headers on` e `.mode box`. Argumentos extras são passados antes do caminho do banco. Este comando ignora `--json`.

```bash
kami db shell
```

---

## Especificação de capítulos

O argumento `SPEC` aceito por `log` e `unlog` suporta:

| Sintaxe         | Significado                              |
| --------------- | ---------------------------------------- |
| `12`            | Capítulo 12                              |
| `12.1`          | Capítulo 12.1 (decimais)                 |
| `12-20`         | Capítulos 12 a 20 (inclusive)            |
| `12.1-12.5`     | Intervalo decimal, passo `0.1`           |
| `1-3,5,7.1,7.2` | Combinação separada por vírgula          |

Duplicatas são removidas. Intervalos precisam ser ascendentes e numéricos.

---

## Status e tipos

**Tipos:** `Manga`, `Manhwa`, `Manhua`, `Novel`, `Comic`

**Status:** `Reading`, `Completed`, `On Hold`, `Dropped`

---

## Saída JSON

Passe `--json` para qualquer comando de dados para obter saída estruturada em vez de texto legível.

```bash
kami list --json
```

```json
[
  {
    "id": 1,
    "title": "Frieren",
    "type": "Manga",
    "status": "Reading",
    "author": "Kanehito Yamada",
    "tags": ["adventure", "fantasy"],
    "chapters_read": 10,
    "last_read": "2026-11-02"
  }
]
```

Erros também são estruturados no modo JSON:

```json
{ "error": "not_found", "query": "Frieren" }
```

```json
{
  "error": "ambiguous",
  "query": "F",
  "candidates": [
    { "id": 1, "title": "Frieren", "series_type": "Manga" },
    { "id": 2, "title": "Fullmetal Alchemist", "series_type": "Manga" }
  ]
}
```

---

## Códigos de saída

| Código | Significado                                                   |
| ------ | ------------------------------------------------------------- |
| `0`    | Sucesso                                                       |
| `1`    | Erro geral (série duplicada, renomeação inválida, etc.)       |
| `2`    | Consulta ambígua: várias séries corresponderam                |
| `3`    | Série não encontrada                                          |
| `5`    | Erro de banco de dados (banco ausente, binário `sqlite3` não encontrado, etc.) |
| `10`   | Confirmação destrutiva recusada ou indisponível em contexto não interativo |

---

## Schema do banco de dados

O `kami` armazena tudo num único arquivo SQLite com quatro tabelas:

- **`series`**: id, title, type, author, status, `started_at` (a data em que você começou a ler a série), `UNIQUE(title, series_type)`
- **`tags`**: id, name (`COLLATE NOCASE`)
- **`series_tags`**: junção muitos-para-muitos, com exclusões em cascata
- **`chapters`**: id, series_id, chapter, read_date, `UNIQUE(series_id, chapter)`

Inspecione diretamente com:

```bash
kami db shell
```
