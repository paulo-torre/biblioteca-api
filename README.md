# Refactor

## Remoção do regex:

Antes, na validação da senha, era usado testes com regex. Essa opção é geralmente mal vista pela maioria dos desenvolvedores. O regex possui certos problemas, como backtracking e ilegibilidade.

## any() e all()

No lugar, foram usadas as função `any()` e `all()` que fazem o mesmo papel dos testes em regex.

## Set

Os caracteres especiais permitidos foram armazenados em um set. Em comparação om strings ou listas, sets são muito mais eficientes, pois a verificação de pertinência em um conjunto é **O(1)**, isto é, é uma constante, não varia em relação ao tamanho dele.