# Arquivo analisado: java-api/src/main/java/com/repoalvo/javaapi/controller/UserController.java

# Tipo da mudança

- **Nova funcionalidade (feature)**: inclusão de um novo endpoint REST `GET /users/names` que retorna uma lista ordenada alfabeticamente dos nomes dos usuários.

# Evidências observadas

- No diff, foi adicionada a função `listUserNames()` no `UserController`:

```java
@GetMapping("/users/names")
public List<String> listUserNames() {
    return userService.listAllUsers()
            .stream()
            .map(UserResponse::name)
            .sorted(String::compareToIgnoreCase)
            .toList();
}
```

- O método usa `userService.listAllUsers()` para obter todos os usuários, extrai apenas o nome (`UserResponse::name`), ordena ignorando case e retorna a lista.

- O arquivo `UserController.java` já possui outros endpoints que usam `userService.listAllUsers()`, como `/users/count`, `/users/duplicates`, `/users/search`, etc., indicando que o serviço retorna uma lista completa de usuários.

- Nos testes existentes (`UserControllerUnitTest.java`, `UserControllerIntegrationTest.java`, `UserControllerTest.java`) não há menção a esse endpoint, pois é novo.

- O contexto do repositório mostra que a API Java expõe endpoints REST para manipulação e consulta de usuários, e que testes unitários e de integração estão presentes para o controller.

# Impacto provável

- A mudança adiciona um novo endpoint público que expõe uma lista de nomes de usuários ordenada alfabeticamente.

- Não altera comportamento existente, pois é uma adição isolada.

- Pode impactar clientes que desejam obter apenas os nomes dos usuários, otimizando a consulta para esse caso.

- Como o método usa `listAllUsers()`, o desempenho e a escalabilidade dependem do tamanho da lista retornada pelo serviço.

# Riscos identificados

- **Risco de desempenho e memória**: `listAllUsers()` retorna todos os usuários em memória. Se a base crescer muito, pode causar lentidão ou uso excessivo de memória.

- **Risco de exposição de dados**: embora só retorne nomes, se houver alguma restrição de acesso ou privacidade sobre nomes, não está contemplada.

- **Risco de ordenação**: a ordenação é feita via `String::compareToIgnoreCase`, que pode não considerar regras locais de ordenação (collation). Pode impactar usuários com nomes com caracteres especiais.

- **Risco de inconsistência**: se `listAllUsers()` retornar usuários com nomes nulos ou vazios, pode causar exceções ou resultados inesperados (não há tratamento explícito para nomes nulos).

- **Risco de falta de paginação**: o endpoint retorna toda a lista, sem paginação, o que pode ser problemático para grandes volumes.

# Cenários de testes manuais

1. **Consulta básica**: chamar `GET /users/names` e verificar se retorna lista de strings com nomes de usuários.

2. **Ordem alfabética**: verificar se a lista está ordenada alfabeticamente ignorando case (ex: "ana", "Bruno", "carlos").

3. **Lista vazia**: simular ambiente sem usuários e verificar se retorna lista vazia sem erro.

4. **Nomes com caracteres especiais**: incluir usuários com nomes contendo acentos, cedilha, espaços e verificar ordenação e retorno correto.

5. **Nomes nulos ou vazios**: se possível, testar comportamento com usuários que tenham nome nulo ou vazio (verificar se gera erro ou ignora).

6. **Carga de usuários**: testar com grande número de usuários para avaliar tempo de resposta e uso de memória.

# Sugestões de testes unitários

- Testar que `listUserNames()` chama `userService.listAllUsers()` exatamente uma vez.

- Testar que o método retorna lista de nomes extraídos corretamente dos objetos `UserResponse`.

- Testar que a lista retornada está ordenada alfabeticamente ignorando case.

- Testar comportamento com lista vazia (retorna lista vazia).

- Testar comportamento com nomes duplicados (devem aparecer repetidos na lista).

- Testar comportamento com nomes nulos (se permitido) e garantir que não cause NullPointerException.

# Sugestões de testes de integração

- Testar endpoint `GET /users/names` com dados reais da base (seed ou mock) e validar:

  - Status HTTP 200.

  - Corpo da resposta é JSON array de strings.

  - Ordem alfabética correta.

  - Lista vazia quando não há usuários.

- Testar integração com o serviço `UserService` para garantir que o endpoint reflete o estado atual dos usuários.

- Testar que o endpoint não retorna dados além dos nomes (ex: não retorna emails ou ids).

- Testar comportamento com usuários criados via `POST /users` e verificar se aparecem no resultado.

# Sugestões de testes de carga ou desempenho

- Não há indicação clara na mudança que justifique testes de carga específicos, mas recomenda-se monitorar o desempenho do endpoint em ambientes com muitos usuários, devido ao uso de `listAllUsers()` e retorno de lista completa.

# Pontos que precisam de esclarecimento

- **Tratamento de nomes nulos ou vazios**: o que deve ocorrer se algum usuário tiver nome nulo ou vazio? Ignorar, lançar erro ou incluir?

- **Limitação de tamanho da lista**: há necessidade de paginação ou limite para evitar retorno de listas muito grandes?

- **Regras de ordenação**: a ordenação atual é suficiente ou deve considerar regras locais (locale) para ordenação?

- **Controle de acesso**: há alguma restrição para expor a lista de nomes? O endpoint é público?

---

# Resumo

A mudança adiciona um endpoint simples que retorna lista ordenada de nomes de usuários, usando dados já disponíveis via `userService.listAllUsers()`. Não altera funcionalidades existentes, mas pode impactar desempenho e uso de memória em bases grandes. Recomenda-se testes focados em validação da ordenação, tratamento de casos extremos (lista vazia, nomes nulos) e integração com o serviço. Pontos de negócio sobre tratamento de nomes e limites de retorno devem ser esclarecidos para evitar problemas futuros.