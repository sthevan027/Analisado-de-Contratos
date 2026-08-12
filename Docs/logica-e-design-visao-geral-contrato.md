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
Excel/*.xlsx
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

Colocar um arquivo `.xlsx` na pasta `Excel/` deve ser suficiente para que ele
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

Quando a CPU existir, ela complementa a leitura do orçamento: cada item recebe
uma composição proporcional de Mão de Obra, Equipamentos e Materiais. O BDI,
quando vier incorporado, é redistribuído nessas categorias, em vez de formar
um quarto grupo isolado. Sem CPU, o item continua analisável pela própria
hierarquia do QQP/LD ou da aba `Dados`.

Inconsistências entre total da QQP/LD e total recomposto pela CPU devem virar
um aviso visível. Elas não impedem a análise do contrato e nunca são
silenciosamente corrigidas.

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

---

## 6. Tela Contratos

A tela Contratos é o ponto de entrada do sistema. Ela deve:

1. Listar todos os `.xlsx` não temporários em `Excel/` — arquivos iniciados
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
  e CPU divergente.
- Alterações no cadastro precisam de testes de gravação/leitura, reabertura e
  arquivo-fonte alterado.

---

## 10. Evolução posterior: comparação entre contratos

O cadastro já atribui um identificador estável a cada contrato. Quando a
comparação for aprovada, a tela poderá permitir a seleção de poucos contratos
e confrontar totais, grupos, composições e Curvas S normalizadas. Essa evolução
não deve mudar o leitor de planilha nem a estrutura do cadastro; deve apenas
consumir contratos já normalizados.
