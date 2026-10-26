# c--

Linguagem interpretada para calculos matematicos simples, destinada ao
aprendizado de analise lexica, analise sintatica e interpretacao.
Implementada em Python puro, sem dependencias externas e sem `eval()`.

## Requisitos

Python 3.11 ou superior. Nao e necessario instalar pacotes.
Execute os comandos na pasta raiz do projeto.

## Executar

Abrir o terminal interativo:

```console
python -m cminusminus
```

```text
cminusminus
c--> 2 + 3 * 4
14
c--> (2 + 3) * 4
20
c--> -10 / 4
-2.5
c--> 1 / 0
Erro: Divisao por zero (coluna 3)
1 / 0
  ^
c--> 2 + 2
4
c--> sair
```

Linhas vazias sao ignoradas. Use `sair`, Ctrl+C ou fim de entrada para encerrar.
No Windows, o fim de entrada pode ser enviado com Ctrl+Z seguido de Enter.

Calcular uma unica expressao:

```console
python -m cminusminus "(2 + 3) * 4"
python -m cminusminus -- "-2 + 3"
```

O separador `--` evita que uma expressao iniciada por `-` seja interpretada
como uma opcao do terminal. Erros nesse modo sao enviados para a saida de
erros e retornam codigo 1; calculos bem-sucedidos retornam codigo 0.

Executar um arquivo UTF-8 com uma expressao por linha:

```console
python -m cminusminus --file programa.cmm
```

Linhas vazias sao ignoradas. O programa valida a sintaxe de todas as linhas
antes de executar qualquer expressao; cada resultado e exibido em uma linha.
Se ocorrer um erro, a mensagem identifica o arquivo e o numero da linha.
O arquivo usa a mesma sintaxe de expressoes descrita abaixo; ainda nao ha
variaveis, atribuicoes ou comandos de impressao.

## Sintaxe

- Numeros inteiros: `0`, `12`, `345`.
- Decimais com digitos dos dois lados do ponto: `0.5`, `3.14`.
- Operadores: `+`, `-`, `*`, `/`.
- Agrupamento: `(2 + 3) * 4`.
- Sinais unarios: `-5`, `+3`, `-(2 + 4)`, `2 * -3`.
- Espacos em branco entre tokens sao ignorados.

Nao ha variaveis, atribuicoes, funcoes, comentarios, potencia,
multiplicacao implicita ou notacao cientifica nesta versao.
Entradas como `.5`, `1.`, `1,5`, `2(3)` e `1e3` sao rejeitadas.

## Gramatica

```ebnf
expressao = termo, { ("+" | "-"), termo } ;
termo     = unario, { ("*" | "/"), unario } ;
unario    = ("+" | "-"), unario | primario ;
primario  = NUMERO | "(", expressao, ")" ;
NUMERO    = DIGITO, { DIGITO }, [ ".", DIGITO, { DIGITO } ] ;
DIGITO    = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

Parenteses controlam o agrupamento. Sinais unarios tem precedencia sobre
multiplicacao e divisao, que tem precedencia sobre adicao e subtracao.
Operadores binarios de mesma precedencia associam a esquerda:
`10 - 3 - 2` resulta em `5`; `20 / 2 / 5` resulta em `2.0`.
O parser exige o consumo de toda a entrada.

## Etapas da Interpretacao

1. `lexer.py` converte o texto em tokens com suas posicoes.
2. `parser.py` usa descida recursiva para construir a AST.
3. `ast_nodes.py` define numeros e operacoes unarias e binarias.
4. `evaluator.py` percorre a AST e calcula o resultado.
5. `repl.py` recebe entradas e apresenta resultados ou erros.

A funcao publica `run_expression` integra essas etapas:

```python
from cminusminus import LanguageError, run_expression

try:
    print(run_expression("2 + 3 * 4"))
except LanguageError as error:
    print(error)
```

Inteiros usam o tipo `int`; decimais e divisao usam `float`.
Assim, `0.1 + 0.2` pode resultar em `0.30000000000000004`.
Divisao por zero, numeros ou resultados nao finitos e expressoes que
excedam a profundidade suportada produzem erros da linguagem.
Limites de conversao de inteiros do Python tambem sao tratados.
Esta implementacao didatica nao e uma sandbox para entradas hostis.

## Testes

```console
python -m unittest discover -s tests -v
```

Os testes cobrem tokens, AST, precedencia, associatividade, sinais unarios,
decimais, sintaxe invalida, divisao por zero, limites numericos,
profundidade e recuperacao do REPL apos erros, incluindo uma sessao
real executada em um subprocesso.
