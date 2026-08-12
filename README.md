# Analisador de Contratos

Leitor de planilhas orçamentárias que transforma contratos em um dashboard
financeiro claro para análise e tomada de decisão.

## Objetivo

O sistema recebe arquivos Excel de orçamento e permite identificar, de forma
rápida, o valor total do contrato, os grupos/frentes com maior peso financeiro
e as linhas que formam esse valor. Quando a planilha possuir CPU, também
mostra a composição entre mão de obra, equipamentos e materiais.

O produto é exclusivamente orçamentário. Ele não controla custo realizado,
medição, tickets, histórico operacional ou avanço físico.

## Fluxo de uso previsto

1. Coloque as planilhas dos contratos na pasta `excel/`.
2. Abra a tela **Contratos** para visualizar os arquivos identificados.
3. Selecione um contrato e informe uma única vez: nome, cliente, obra, data
   de início e duração em meses.
4. O sistema salva esses dados em `data/contratos.json` e os reaproveita nas
   próximas aberturas.
5. Abra o dashboard para analisar a distribuição do orçamento e a Curva S
   financeira planejada.

## Formatos de planilha aceitos

| Aba | Uso |
|---|---|
| `QQP` | Orçamento com itens, quantidades, preços e totais |
| `LD<número>` | Variação de QQP, como `LD1` e `LD3` |
| `Dados` | Formato legado de orçamento já processado |
| `CPU` | Complemento da composição de preço unitário |

O sistema deve reconhecer o formato pelas abas, e não pelo nome do arquivo.
Arquivos temporários do Excel, iniciados por `~$`, devem ser ignorados.

## Stack

- **Python 3.11+** para leitura, normalização e cálculos financeiros com
  `Decimal`.
- **Flask + Jinja2** no backend local e na renderização das telas.
- **HTML e CSS** para a UI; JavaScript simples apenas para interações e
  gráficos, sem SPA ou etapa de build.
- **Chart.js** para os gráficos de composição e da Curva S.
- **JSON local** em `data/contratos.json` para o cadastro persistente.

Não haverá banco externo, serviço externo ou frontend separado no MVP.

## Dashboard planejado

- KPIs: valor total orçado, início, prazo e quantidade de itens/grupos.
- Composição por grupo, frente ou linha de execução.
- Itens de maior peso financeiro.
- Tabela hierárquica com grupo, subgrupo, item, unidade, quantidade e valor.
- Composição por mão de obra, equipamentos e materiais, quando houver CPU.
- Curva S financeira planejada, calculada a partir do valor total, início e
  duração cadastrados.
- Avisos de leitura, incluindo divergências entre QQP/LD e CPU.

A Curva S é uma referência financeira planejada. Ela não representa medição,
custo realizado, avanço físico ou cronograma formal.

## Orçamento de referência analisado

A planilha em
`excel/Anexo_I_-_PQ-8001PZ-G-11007_Rev.ALT_REV08 (1).xlsx` contém `QQP` e
`CPU`, além de abas auxiliares (`MO`, `Equip`, `BDI` e outras). A análise
confirmou a necessidade de suportar:

- cabeçalho da QQP em múltiplas linhas;
- itens hierárquicos e linhas de grupo sem valor próprio;
- CPU em blocos por item, e não em uma tabela única;
- composição parcial: foram encontradas 51 linhas orçamentárias e 50 blocos
  de CPU; o item `6.1.1` permanece no total, porém sem composição disponível.

Esta planilha é uma referência de compatibilidade. O leitor não deve
codificar posições de linha, nomes de arquivo ou valores específicos dela.

## Persistência do cadastro

`data/contratos.json` será o cadastro local dos metadados dos contratos. A
planilha original continua sendo a fonte de verdade dos valores orçados.

Para cada contrato, o cadastro deve armazenar um identificador, nome do
arquivo, SHA-256, nome exibido, cliente, obra, data de início, duração e data
de atualização. Se o arquivo mudar, os metadados devem ser preservados e a
aplicação deve pedir apenas uma revisão — não todo o preenchimento novamente.

## Fora de escopo no MVP

- Lançamentos manuais e `lancamentos.txt`.
- Telas de lançamentos e histórico operacional.
- BM, MC, tickets, OCR, Dropbox e importação de medições.
- Cronograma importado, avanço físico e previsto × realizado.
- Curva ABC/Pareto.
- Comparação simultânea de contratos.

A comparação entre poucos contratos é uma evolução futura; a estrutura de
cadastro deve permitir essa expansão sem que ela seja implementada agora.

## Documentação

- [Lógica e design do produto](Docs/logica-e-design-visao-geral-contrato.md)
- [Instruções para agentes e manutenção](Docs/AGENTS.md)

## Status atual

Este repositório contém a especificação do produto e um exemplo real de
planilha em `excel/`, usado para validar o formato QQP/CPU descrito na
documentação. A implementação do leitor de Excel, da persistência e do
dashboard ainda será iniciada a partir desta documentação.
