# Analisador de Contratos — Lógica e Design

> Visão funcional do produto: colocar planilhas de orçamento em uma pasta,
> interpretar sua estrutura e apresentar um dashboard financeiro simples para
> análise e tomada de decisão.

---

## 1. Objetivo do sistema

O Analisador de Contratos é um leitor de orçamentos. Ele deve transformar
planilhas de clientes em uma visão clara da distribuição financeira do
contrato, permitindo identificar rapidamente onde está o maior peso
orçamentário e navegar até as linhas que o compõem.

O sistema é exclusivamente **orçamentário**. Ele não registra custos
realizados, medições, tickets, boletins de medição, memória de cálculo de
medição, histórico operacional ou lançamentos manuais.

Perguntas que o dashboard deve responder:

- Qual é o valor total do contrato?
- Quais grupos, frentes/linhas de execução e itens concentram mais valor?
- Como o orçamento se distribui entre mão de obra, equipamentos e materiais,
  quando houver composição de preço unitário (CPU)?
- Como o orçamento planejado evolui durante o prazo contratual?
- Quais linhas formam cada grupo e qual é seu valor, quantidade e unidade?

---

## 2. Fluxo principal: pasta → leitor → cadastro → dashboard

```text
excel/*.xlsx
    │
    ├── varredura automática de arquivos e identificação das abas
    │
    ▼
Tela Contratos
    │  lista os arquivos, indica o formato e permite selecionar um contrato
    │
    ├── cadastro persistente: nome, cliente, obra, início e duração
    │
    ▼
data/contratos.json
    │  metadados do contrato associados ao arquivo e à sua assinatura
    │
    ▼
Leitor de orçamento
    │  QQP/LD ou Dados; CPU quando disponível
    │
    ▼
Formato intermediário único
    │
    ▼
Dashboard orçamentário + Curva S financeira planejada
```

Colocar um arquivo `.xlsx` na pasta `excel/` deve ser suficiente para que ele
apareça na tela **Contratos**. Não haverá upload manual. A seleção e os
metadados são persistidos localmente para que não precisem ser preenchidos de
novo a cada abertura do sistema.

---

## 3. Formatos aceitos

O reconhecimento é feito pelos nomes das abas, e não pelo nome do arquivo.
Isso permite receber arquivos com nomes diferentes vindos de clientes.

| Formato | Como identificar | Leitura esperada |
|---|---|---|
| QQP | Aba `QQP` ou nome contendo `QQP` | Itens, hierarquia, unidade, quantidade, preço unitário e total |
| LD | Aba `LD<número>`, como `LD1` ou `LD3` | Mesmo tratamento do QQP, excluindo abas auxiliares como `LD1 - 1` |
| Dados | Aba exata `Dados` | Formato legado já processado, com a hierarquia descrita na planilha |
| CPU | Aba `CPU`, complementar | Composição de preço unitário por mão de obra, equipamentos e materiais |

O leitor deve localizar cabeçalhos por texto — por exemplo, `ITEM`,
`DESCRIÇÃO`, `UNIDADE`, `QUANTIDADE`, `PREÇO UNITÁRIO` e `TOTAL` — e não por
posição fixa. Isso reduz a dependência de layouts idênticos entre contratos.

Um arquivo real de cliente costuma trazer diversas outras abas além das
listadas acima — por exemplo `F. Rosto`, `CMS`, `MC Serv. Extraordinários`,
`MO`, `Equip`, `BDI`, `BDI-ADM LOCAL` ou `ES`. Nenhuma delas deve ser tratada
como orçamento ou CPU; o leitor reconhece apenas os nomes/padrões da tabela
acima e ignora silenciosamente o restante. Em particular, abas de memória de
cálculo (`MC ...`) e critério de medição (`CMS`) são fora de escopo e nunca
alimentam o dashboard.

Na aba QQP/LD, o cabeçalho pode ocupar duas linhas mescladas (um rótulo geral
e, na linha seguinte, o rótulo específico ou código da coluna). A busca por
texto deve varrer essa faixa de linhas, não assumir cabeçalho de linha única.
Linhas de item têm um código hierárquico (`1.1.1.1.1`) e um total numérico;
linhas de grupo têm o mesmo tipo de código mas sem total (servem só para
nomear a hierarquia); linhas de subtotal/total (`SUB-TOTAL GERAL`, `TOTAL`)
têm total mas nenhum código — o leitor precisa distinguir essas três
situações pela combinação código/total, não só pela presença de um valor.
Colunas de critério de medição (ex.: `CMS`, `K`, `TT`, `UU`, `Seq`, quando
aparecem dentro da própria QQP) são referências à aba `CMS` e devem ser
ignoradas pelo leitor de orçamento.

### 3.1 Estrutura real da aba CPU

Ao contrário de QQP/LD/Dados, a CPU normalmente **não é uma tabela** com uma
linha por item. Ela é uma sequência de blocos, um por item orçamentário,
delimitados por linhas-marcador:

```text
SERVIÇO:            <descrição do item>
ITEM:               <código>      UNID.:  <unidade>   <valor total do item>
ITEM | DESCRIÇÃO | UNID | QUANTIDADE | VALOR UNIT. | VALOR TOTAL

1.0  MÃO DE OBRA
     <linha de recurso: descrição, unidade, quantidade, valor unit., total>
     ...
     TOTAL 1.0                                                    <total>

2.0  EQUIPAMENTOS
     ...
     TOTAL 2.0                                                    <total>

3.0  MATERIAIS
     ...
     TOTAL 3.0                                                    <total>

CUSTO DIRETO (A+B+C)                                               <total>
BDI                                                                 <total>
TOTAL GERAL                                                         <total>
```

O leitor de CPU deve varrer a aba procurando as linhas `ITEM:` para delimitar
cada bloco, extrair o código do item da própria linha `ITEM:` (não da
posição) e usá-lo para associar o bloco ao item correspondente da QQP/LD. O
tamanho de cada bloco é variável, pois cada categoria tem uma quantidade
diferente de linhas de recurso. A aba costuma ter muito mais linhas alocadas
do que blocos reais (linhas em branco no final) — o leitor deve parar de
varrer quando não houver mais `ITEM:`, e não depender do `max_row` da planilha
como sinal de quantidade de dados.

O `BDI` aparece na CPU como um valor absoluto já calculado — não uma
alíquota — separado das três categorias. Para redistribuí-lo nas categorias
(mão de obra, equipamentos e materiais), como descrito acima, aplica-se um
fator proporcional ao custo direto:

```text
fator = TOTAL GERAL / CUSTO DIRETO
total_categoria_com_bdi = TOTAL <categoria> × fator
```

`TOTAL GERAL` do bloco deve ser comparado ao total do mesmo item na QQP/LD;
divergência entre os dois vira aviso de leitura (seção 7).

Quando a CPU existir, ela complementa a leitura do orçamento: cada item recebe
uma composição proporcional de Mão de Obra, Equipamentos e Materiais. Sem CPU,
o item continua analisável pela própria hierarquia do QQP/LD ou da aba
`Dados`.

Inconsistências entre total da QQP/LD e total recomposto pela CPU devem virar
um aviso visível. Elas não impedem a análise do contrato e nunca são
silenciosamente corrigidas.

A CPU também pode cobrir apenas parte da QQP. Nesta planilha de referência,
foram encontradas 51 linhas orçamentárias e 50 blocos CPU; o item `6.1.1` não
tem composição. Itens nessa situação permanecem no total contratual e na
hierarquia, mas recebem o status `SEM_CPU`. A composição do dashboard deve
mostrar separadamente o valor com CPU e o valor sem composição disponível.

---

## 4. Cadastro persistente do contrato

O arquivo `data/contratos.json` é o cadastro local persistente dos contratos;
não é uma fonte de orçamento e não substitui a planilha do cliente.

Ao selecionar um arquivo pela primeira vez, a tela Contratos solicitará:

- nome do contrato;
- cliente;
- obra;
- data de início contratual (`AAAA-MM-DD`);
- duração contratual em meses.

O cadastro mantém também o nome do arquivo e o SHA-256 da versão lida. Em uma
nova abertura, o sistema associa o mesmo arquivo ao cadastro existente e
preenche esses dados automaticamente. Se o conteúdo do arquivo mudar, os
metadados são preservados, mas a tela sinaliza que a fonte foi atualizada para
que o usuário confirme se os dados contratuais ainda são válidos.

Estrutura inicial proposta:

```json
{
  "schema_version": 1,
  "contrato_ativo_id": "uuid-do-contrato",
  "contratos": [
    {
      "id": "uuid-do-contrato",
      "arquivo": "QQP-Cliente-A.xlsx",
      "sha256": "assinatura-do-arquivo-lido",
      "nome": "Contrato Usina A",
      "cliente": "Cliente A",
      "obra": "Obra A",
      "inicio": "2026-09-01",
      "duracao_meses": 18,
      "atualizado_em": "2026-08-12T00:00:00-03:00"
    }
  ]
}
```

O JSON deve ser gravado de forma atômica (arquivo temporário e substituição),
para não corromper o cadastro se a aplicação for interrompida durante a
gravação.

---

## 5. Contrato de dados interno

Todos os formatos de planilha devem ser convertidos para a mesma estrutura
antes de chegar ao dashboard. Assim, as telas não conhecem colunas, abas ou
particularidades do Excel de origem.

```python
{
    "code": "1.1.1",
    "name": "Descrição do item",
    "planned": 12345.60,
    "unit": "t",
    "qty": 100.0,
    "area": "Frente ou grupo de execução",
    "breakdown": [
        {
            "group": "Mão de Obra",
            "subgroup": "Especialidade",
            "name": "Descrição da composição",
            "planned": 4000.00
        }
    ]
}
```

`planned` representa exclusivamente o valor orçado. O cálculo financeiro deve
usar `Decimal`; números em ponto flutuante podem ser usados somente na camada
visual depois da conversão.

Em arquivos reais, as colunas dedicadas de área/subárea da QQP costumam vir
vazias — a planilha usa o código hierárquico do item (`1`, `1.1`, `1.1.1...`)
para organizar os grupos, sem preencher uma coluna literal de área. Quando
isso ocorrer, `area` deve ser derivada do nome do grupo de nível superior mais
próximo na hierarquia do código (ex.: a descrição da linha de código `1` ou
`1.1`), e não exigir uma coluna dedicada preenchida.

---

## 6. Tela Contratos

A tela Contratos é o ponto de entrada do sistema. Ela deve:

1. Listar todos os `.xlsx` não temporários em `excel/` — arquivos iniciados
   por `~$` devem ser ignorados.
2. Exibir nome do arquivo, formato identificado e situação de leitura.
3. Mostrar se o arquivo já possui cadastro e se sua assinatura mudou.
4. Permitir selecionar um contrato como ativo.
5. Criar ou editar os metadados persistentes do contrato ativo.
6. Abrir o dashboard do contrato selecionado.

Nesta primeira etapa, o dashboard trabalha com um contrato ativo por vez.
Os demais contratos permanecem cadastrados e prontos para seleção. Comparar
dois ou mais contratos é uma evolução futura, pensada para poucos casos, mas
não entra no primeiro dashboard.

---

## 7. Dashboard orçamentário

O dashboard deve ser direto e legível, com detalhamento progressivo: do total
do contrato até uma linha individual de orçamento.

| Seção | Decisão que apoia |
|---|---|
| KPIs | Valor orçado total, prazo, início e quantidade de itens/grupos |
| Composição do orçamento | Identificar grupos ou frentes de maior peso financeiro |
| Itens de maior peso | Priorizar a revisão das linhas mais relevantes, sem classificação ABC |
| Detalhamento hierárquico | Conferir grupo, subgrupo, item, unidade, quantidade e valor |
| Composição por CPU | Entender a participação de mão de obra, equipamentos e materiais |
| Curva S financeira | Visualizar a distribuição planejada do orçamento ao longo do prazo |
| Avisos de leitura | Avaliar divergências QQP/LD × CPU ou limitações da fonte |

Os rótulos de grupo, frente e linha de execução devem refletir os dados reais
do contrato. O sistema não deve inventar categorias que não existam no Excel.

### Curva S financeira planejada

A Curva S é inteiramente orçamentária e planejada. Ela não representa
medição, custo realizado nem avanço físico.

O valor total do contrato é distribuído ao longo de `duracao_meses`, a partir
da `data de início` cadastrada. A curva acumulada segue a função suavizada:

```text
s(x) = 3x² - 2x³, onde x varia de 0 a 1
valor acumulado do mês = valor total orçado × s(x)
valor mensal = acumulado do mês atual − acumulado do mês anterior
```

O gráfico deve mostrar valores mensais e acumulados, deixando claro o rótulo
**Planejado (Curva S financeira)**. A distribuição sintética é uma referência
gerencial; ela não substitui um cronograma físico-financeiro formal.

---

## 8. Fora de escopo

Não fazem parte deste produto nesta fase:

- lançamentos manuais, custos realizados e `lancamentos.txt`;
- tela ou rota de lançamentos;
- tela ou rota de histórico operacional;
- boletins de medição (BM), memórias de cálculo (MC), tickets e OCR;
- integração com Dropbox, importação de medições ou sincronização por
  competência;
- cronograma importado, avanço físico ou comparação previsto × realizado;
- Curva ABC/Pareto;
- comparação simultânea entre contratos.

---

## 9. Princípios de implementação e validação

- As planilhas de origem são somente leitura; o sistema grava apenas seu
  cadastro local em `data/contratos.json`.
- A identificação de formato deve ser rápida e baseada nas abas do arquivo.
- Cada leitor deve entregar o contrato de dados único descrito na seção 5.
- Avisos de qualidade de dados devem ser explícitos e não mascarar valores da
  fonte.
- O dashboard não deve depender de um layout específico de planilha.
- O cadastro de contrato deve sobreviver a reinicializações da aplicação.
- Alterações nos leitores precisam de testes com QQP, LD, Dados, CPU ausente
  e CPU divergente, inclusive cobertura parcial de CPU.
- Alterações no cadastro precisam de testes de gravação/leitura, reabertura e
  arquivo-fonte alterado.
- A planilha de referência deve validar 51 linhas de orçamento, 50 vínculos
  de CPU e o status `SEM_CPU` para `6.1.1`, sem fixar valores ou índices de
  linha da fonte no código de produção.

---

## 10. Evolução posterior: comparação entre contratos

O cadastro já atribui um identificador estável a cada contrato. Quando a
comparação for aprovada, a tela poderá permitir a seleção de poucos contratos
e confrontar totais, grupos, composições e Curvas S normalizadas. Essa evolução
não deve mudar o leitor de planilha nem a estrutura do cadastro; deve apenas
consumir contratos já normalizados.

---

## 11. Stack técnico

- **Linguagem**: Python 3.11+.
- **Leitura de Excel**: `openpyxl`, lendo com `data_only=True` para obter
  valores calculados em vez de fórmulas. Não usar `pandas` na camada de
  leitura — ele converte números para `float`, o que conflita com a exigência
  de `Decimal` para valores monetários (seção 5).
- **UI**: HTML renderizado no servidor, sem framework de frontend (sem
  SPA/bundler). Um servidor local em Flask expõe as
  telas Contratos e Dashboard como páginas HTML com Jinja2; interatividade
  pontual (ex.: expandir a tabela hierárquica) pode usar JavaScript simples,
  sem build step.
- **Gráficos**: Chart.js carregado por `<script>` para composição do orçamento
  e Curva S; sem geração de imagem no
  servidor.
- **Persistência**: `data/contratos.json`, gravado atomicamente com o módulo
  padrão (`tempfile` + `os.replace`), sem banco de dados.
- **Testes**: `pytest`, cobrindo leitores (seção 9) e cadastro isoladamente
  da camada web.

Estrutura de pastas proposta para quando a implementação começar:

```text
app.py                 # ponto de entrada do servidor Flask
readers/
    common.py           # detecção de aba/formato, achado de cabeçalho por texto
    qqp.py               # QQP/LD
    dados.py             # aba Dados (legado)
    cpu.py               # blocos de composição de preço unitário (seção 3.1)
storage/
    contratos.py         # leitura/gravação atômica de data/contratos.json
templates/
    contratos.html
    dashboard.html
static/
    css/
    js/
excel/                  # planilhas de origem (somente leitura)
data/
    contratos.json
tests/
```

Essa estrutura é um ponto de partida, não uma exigência rígida; pode ser
ajustada quando a implementação começar, desde que os leitores continuem
isolados da camada web (seção 9).
