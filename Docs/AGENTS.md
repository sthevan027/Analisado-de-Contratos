# Instruções do Projeto — Analisador de Contratos

## Objetivo

Este repositório define um analisador de contratos exclusivamente
orçamentário. O produto recebe planilhas Excel de orçamento, interpreta sua
estrutura e apresenta um dashboard para analisar distribuição financeira,
grupos/frentes de maior peso e linhas detalhadas.

Não transformar o produto em controle de custos realizados, medição ou
execução de obra sem aprovação explícita.

## Fonte de verdade e persistência local

- As planilhas em `Excel/` são a fonte de verdade dos valores orçados e são
  apenas de leitura.
- `data/contratos.json` é o cadastro persistente local dos metadados; não
  contém valores substitutos do orçamento.
- O cadastro deve guardar: `id`, `arquivo`, `sha256`, `nome`, `cliente`,
  `obra`, `inicio`, `duracao_meses` e `atualizado_em`.
- Use `contrato_ativo_id` para indicar o contrato exibido.
- Grave o JSON atomicamente. Preserve os metadados quando a assinatura da
  planilha mudar e sinalize a mudança para revisão.

## Formatos e leitura

- Aceitar `.xlsx` e ignorar temporários do Office iniciados por `~$`.
- Detectar formatos pelos nomes das abas, sem depender do nome do arquivo.
- `QQP` e abas `LD<número>` são formatos de orçamento. Não tratar abas
  auxiliares, como `LD1 - 1` e `LD1 - 2`, como orçamento principal.
- A aba `Dados` é o formato legado aceito.
- A aba `CPU`, quando existir, complementa a composição dos itens em Mão de
  Obra, Equipamentos e Materiais.
- Descobrir cabeçalhos pelo texto das células, não por índices fixos de
  coluna.
- Normalizar toda fonte antes da camada visual. Cada item contém `code`,
  `name`, `planned`, `unit`, `qty`, `area` e `breakdown`.
- Use `Decimal` para cálculos monetários. Preserve divergências QQP/LD × CPU
  como avisos explícitos; nunca altere silenciosamente valores de origem.

## Dashboard

- Exibir um contrato ativo por vez no MVP.
- Priorizar valor total, prazo, grupos/frentes de maior peso, itens mais
  relevantes, detalhamento hierárquico e composição por CPU.
- Não implementar Curva ABC/Pareto.
- A Curva S é financeira planejada: deriva do valor total, data de início e
  duração em meses cadastrados pelo usuário. Não representa avanço físico,
  medição nem custo realizado.
- Para a Curva S sintética, use `s(x) = 3x² - 2x³`; o valor mensal é a
  diferença entre acumulados consecutivos.
- Use rótulos existentes no contrato para grupos e frentes; não invente
  categorias inexistentes na fonte.

## Fora de escopo

Não adicionar sem autorização explícita:

- lançamentos manuais, custos realizados ou `lancamentos.txt`;
- telas/rotas de lançamentos e histórico operacional;
- BM, MC, tickets, OCR, Dropbox, importação de medições ou competência;
- cronograma importado, avanço físico e previsto × realizado;
- comparação simultânea de contratos.

A comparação de poucos contratos é uma evolução planejada, não uma função do
MVP. Prepare leitores e cadastro para isso, mas não antecipe telas ou cálculos
de comparação.

## Validação obrigatória

- Leitores: QQP, LD, Dados, CPU ausente e divergência CPU × orçamento.
- Cadastro: gravação atômica, reabertura, preservação dos metadados e arquivo
  alterado.
- Curva S: total final igual ao valor orçado, período igual à duração e soma
  mensal igual ao total, respeitando arredondamento.
- Distinguir testes unitários, integração de leitura Excel e validação visual;
  um não prova automaticamente o outro.
