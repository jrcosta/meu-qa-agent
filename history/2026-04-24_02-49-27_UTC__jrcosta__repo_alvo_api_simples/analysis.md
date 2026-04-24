# Arquivo analisado: java-api/src/main/java/com/repoalvo/javaapi/controller/UserController.java

# Tipo da mudança

Implementação de um novo endpoint HTTP PUT para atualização parcial de usuários (`/users/{userId}`) no `UserController`.

---

# Evidências observadas

- Inclusão do método `updateUser` anotado com `@PutMapping("/users/{userId}")` no `UserController`.
- O método recebe um `userId` via path variable e um payload do tipo `UserUpdateRequest` validado.
- Validação explícita para garantir que pelo menos um dos campos `name` ou `email` esteja presente no payload, caso contrário retorna `400 BAD_REQUEST`.
- Verificação de conflito de email: se o email informado já estiver cadastrado para outro usuário (diferente do `userId`), retorna `409 CONFLICT`.
- Chamada ao serviço `userService.update(userId, payload)` que retorna um `Optional<UserResponse>`, lançando `404 NOT_FOUND` se o usuário não existir.
- Importação de `UserUpdateRequest` e `PutMapping` adicionadas.
- Contexto do arquivo mostra que o controller já possui endpoints para criação, listagem, busca e outras operações com usuários, seguindo padrão REST.
- Testes existentes no repositório indicam boa cobertura para outros endpoints do `UserController`, mas não há evidência direta de testes para atualização de usuário.

---

# Impacto provável

- Novo comportamento para atualização parcial de usuários via HTTP PUT em `/users/{userId}`.
- Possibilidade de alterar nome e/ou email do usuário.
- Regras de negócio importantes:
  - Não permite atualização sem pelo menos um campo informado.
  - Garante unicidade do email entre usuários diferentes.
- Pode impactar clientes da API que desejam atualizar usuários.
- Pode afetar integridade dos dados se a validação de email não for consistente.
- Pode gerar erros 400, 404 e 409 conforme as validações e existência do usuário.

---

# Riscos identificados

- **Validação insuficiente do payload**: o método só verifica se `name` e `email` são nulos, mas não valida formatos (ex: email válido) ou outros campos que possam existir em `UserUpdateRequest`.
- **Condição de corrida na verificação de email duplicado**: entre a verificação `findByEmail` e a atualização, outro usuário pode ser criado com o mesmo email, causando possível inconsistência.
- **Dependência do serviço `userService.update`**: se o método `update` não tratar corretamente a atualização parcial, pode haver perda de dados ou comportamento inesperado.
- **Ausência de testes específicos para o novo endpoint**: não há evidência de testes unitários ou integração cobrindo o fluxo de atualização, o que aumenta risco de regressão.
- **Possível impacto em dados sensíveis**: embora o payload atual só tenha `name` e `email`, se futuramente o modelo for estendido, pode haver risco de exposição ou alteração indevida.
- **Tratamento de erros HTTP**: mensagens de erro são genéricas, pode ser necessário padronizar para facilitar o consumo da API.

---

# Cenários de testes manuais

1. **Atualização parcial com apenas nome**
   - Enviar PUT `/users/{userId}` com payload contendo apenas `name`.
   - Verificar retorno 200 e atualização correta do nome.
2. **Atualização parcial com apenas email**
   - Enviar PUT `/users/{userId}` com payload contendo apenas `email`.
   - Verificar retorno 200 e atualização correta do email.
3. **Atualização com nome e email**
   - Enviar PUT `/users/{userId}` com ambos os campos.
   - Verificar retorno 200 e atualização correta.
4. **Atualização sem campos (payload com `name=null` e `email=null`)**
   - Enviar PUT com payload vazio ou com ambos campos nulos.
   - Verificar retorno 400 com mensagem "Informe ao menos um campo para atualizar".
5. **Atualização com email já usado por outro usuário**
   - Enviar PUT com email que pertence a outro usuário.
   - Verificar retorno 409 com mensagem "E-mail já cadastrado por outro usuário".
6. **Atualização de usuário inexistente**
   - Enviar PUT para `userId` que não existe.
   - Verificar retorno 404 com mensagem "Usuário não encontrado".
7. **Atualização com email inválido (se aplicável)**
   - Testar envio de email com formato inválido (se validação existir no payload).
   - Verificar comportamento (idealmente 400).
8. **Testar payload com campos extras (se possível)**
   - Enviar campos não esperados no JSON para verificar rejeição ou ignorância.
9. **Testar comportamento com dados limite (ex: nomes muito longos)**
   - Verificar se há restrições e tratamento adequado.

---

# Sugestões de testes unitários

- Testar `updateUser` com payload contendo apenas `name` válido, mockando `userService.update` para retornar usuário atualizado.
- Testar `updateUser` com payload contendo apenas `email` válido, mockando `userService.findByEmail` para retornar vazio e `userService.update` para sucesso.
- Testar `updateUser` com payload contendo `email` já usado por outro usuário, esperando `ResponseStatusException` 409.
- Testar `updateUser` com payload sem campos `name` e `email`, esperando `ResponseStatusException` 400.
- Testar `updateUser` com `userService.update` retornando `Optional.empty()`, esperando `ResponseStatusException` 404.
- Testar que `userService.findByEmail` não bloqueia atualização se o email pertence ao mesmo usuário (`userId` igual).
- Testar comportamento com payload contendo campos nulos e não nulos.
- Testar que exceções inesperadas são propagadas ou tratadas conforme política.

---

# Sugestões de testes de integração

- Testar fluxo completo de atualização:
  - Criar usuário via POST `/users`.
  - Atualizar nome via PUT `/users/{userId}`.
  - Validar que GET `/users/{userId}` retorna nome atualizado.
- Testar atualização de email para um email não usado.
- Testar tentativa de atualização para email já existente em outro usuário, validar 409.
- Testar atualização com payload inválido (sem campos), validar 400.
- Testar atualização de usuário inexistente, validar 404.
- Testar concorrência: duas atualizações simultâneas com emails diferentes para verificar consistência (se possível).
- Validar que campos não atualizados permanecem inalterados.
- Testar integração com camada de persistência para garantir que atualização parcial funciona corretamente.

---

# Sugestões de testes de carga ou desempenho

- Não há evidência na mudança que justifique testes de carga ou desempenho específicos para este endpoint.

---

# Pontos que precisam de esclarecimento

- Qual o comportamento esperado se o payload contiver campos adicionais além de `name` e `email`? Devem ser ignorados ou rejeitados?
- Existe validação de formato para o campo `email` no `UserUpdateRequest`? Se não, seria recomendável incluir.
- O método `userService.update` realiza atualização parcial ou substituição completa? Como ele trata campos nulos?
- Há necessidade de controle de concorrência para evitar condições de corrida na verificação de email duplicado?
- Qual o comportamento esperado se o usuário tentar atualizar para o mesmo email que já possui? Atualmente parece permitido, mas confirmar.
- Existe política para campos obrigatórios no update além de pelo menos um campo informado?
- Como é o tratamento de logs e auditoria para atualizações de usuário? Isso pode impactar testes e riscos.

---

# Resumo

A mudança introduz um endpoint PUT para atualização parcial de usuários, com validações básicas para campos obrigatórios e unicidade de email. O impacto é direto na API de usuários, com riscos relacionados à validação, concorrência e ausência de testes específicos. Recomenda-se focar em testes que cubram os fluxos de sucesso e erro, especialmente conflitos de email e ausência de campos no payload. Pontos de negócio e implementação precisam ser esclarecidos para garantir robustez e evitar regressões.

---

# Arquivo analisado: java-api/src/main/java/com/repoalvo/javaapi/model/UserUpdateRequest.java

# Tipo da mudança

- **Adição de nova classe/modelo (record) para requisição de atualização de usuário**

# Evidências observadas

- O diff mostra a criação do arquivo `UserUpdateRequest.java` contendo um `record` Java com dois campos: `name` e `email`.
- Ambos os campos possuem anotações de validação Jakarta Bean Validation: `@Size(min=3, max=100)` para `name` e `@Email` para `email`.
- O contexto do repositório mostra que `UserUpdateRequest` já é referenciado em `UserService` no método `update(int userId, UserUpdateRequest payload)`, que atualiza um usuário existente.
- O `UserService` usa esse objeto para atualizar nome e email, permitindo que os campos sejam nulos para manter valores antigos.
- Não há evidência no diff de alteração em controladores ou serviços que modifiquem o comportamento atual, apenas a introdução do modelo.
- Testes existentes para `UserService` e `UserController` indicam cobertura para operações de usuário, mas não há testes específicos para `UserUpdateRequest` ainda.

# Impacto provável

- Introdução formal do modelo `UserUpdateRequest` para encapsular dados de atualização de usuário.
- Provável padronização e validação automática dos dados de atualização via Bean Validation.
- Pode impactar endpoints que aceitam atualização de usuário, especialmente se passarem a usar esse record para validação e transporte dos dados.
- Facilita a manutenção e evolução do payload de atualização, garantindo restrições mínimas (nome entre 3 e 100 caracteres, email válido).
- Pode afetar fluxos de atualização de usuário no backend, especialmente se o controlador ou serviço passar a usar esse record para validação.

# Riscos identificados

- **Validação parcial:** O record permite que `name` e `email` sejam nulos (não há anotação `@NotNull`), o que pode levar a atualizações parciais. Se o controlador ou serviço não tratar corretamente campos nulos, pode haver inconsistência.
- **Validação insuficiente:** A anotação `@Size(min=3, max=100)` no nome pode rejeitar nomes curtos legítimos (ex: "Al"), o que pode impactar usuários reais.
- **Ausência de validação explícita para campos nulos:** Se o controlador não usar `@Valid` ou não tratar corretamente a validação, dados inválidos podem passar.
- **Possível incompatibilidade com payloads JSON:** Se o cliente enviar campos vazios ou ausentes, pode haver problemas de desserialização ou validação.
- **Falta de testes específicos:** Não há evidência de testes unitários ou de integração cobrindo o uso do `UserUpdateRequest`, o que pode levar a regressões não detectadas.
- **Impacto em endpoints existentes:** Se o controlador que manipula atualização de usuário não for ajustado para usar esse record, pode haver inconsistência ou falha na validação.

# Cenários de testes manuais

1. **Atualização de usuário com nome válido e email válido**
   - Enviar payload com `name` entre 3 e 100 caracteres e email válido.
   - Verificar atualização correta dos dados.

2. **Atualização de usuário com nome menor que 3 caracteres**
   - Enviar payload com `name` com 1 ou 2 caracteres.
   - Verificar rejeição da requisição com erro de validação.

3. **Atualização de usuário com email inválido**
   - Enviar payload com email mal formatado (ex: "email@invalido").
   - Verificar rejeição da requisição com erro de validação.

4. **Atualização parcial com apenas nome ou apenas email**
   - Enviar payload com apenas `name` preenchido e `email` nulo/ausente.
   - Enviar payload com apenas `email` preenchido e `name` nulo/ausente.
   - Verificar que o campo não enviado permanece inalterado.

5. **Atualização com campos nulos explicitamente**
   - Enviar payload com `name` e `email` nulos.
   - Verificar comportamento do sistema (provável rejeição ou nenhuma alteração).

6. **Atualização com campos ausentes no JSON**
   - Enviar payload JSON sem o campo `name` ou `email`.
   - Verificar se o sistema trata corretamente como atualização parcial.

7. **Testar limites de tamanho do nome**
   - Enviar nome com exatamente 3 caracteres e 100 caracteres.
   - Verificar aceitação.

8. **Testar atualização com dados inválidos e verificar mensagens de erro**
   - Confirmar que mensagens de erro são claras e indicam o campo inválido.

# Sugestões de testes unitários

- Testar criação de `UserUpdateRequest` com:
  - Nome válido dentro dos limites.
  - Nome menor que 3 caracteres (esperar falha de validação).
  - Nome maior que 100 caracteres (esperar falha de validação).
  - Email válido.
  - Email inválido (ex: sem '@', com espaços).
  - Campos nulos (verificar comportamento da validação).

- Testar método `UserService.update` com:
  - Payload com nome e email válidos.
  - Payload com nome nulo e email válido.
  - Payload com email nulo e nome válido.
  - Payload com ambos nulos (deve manter dados antigos).
  - Verificar que o usuário é atualizado corretamente no `List<UserResponse>`.

- Testar integração da validação Bean Validation no controlador (se aplicável):
  - Simular requisição com payload inválido e verificar que a validação falha.

# Sugestões de testes de integração

- Testar endpoint HTTP que utiliza `UserUpdateRequest` para atualizar usuário:
  - Enviar requisição PUT/PATCH com payload válido e verificar resposta 200 e dados atualizados.
  - Enviar payload com nome inválido e verificar resposta 400 com mensagem de erro.
  - Enviar payload com email inválido e verificar resposta 400.
  - Enviar payload parcial (apenas nome ou email) e verificar atualização parcial.
  - Enviar payload com campos nulos e verificar comportamento (erro ou sem alteração).
  - Testar atualização de usuário inexistente e verificar resposta adequada (404 ou similar).

- Testar fluxo completo de atualização:
  - Criar usuário.
  - Atualizar usuário com `UserUpdateRequest`.
  - Buscar usuário e verificar dados atualizados.

# Sugestões de testes de carga ou desempenho

- **Não aplicável**: A mudança é estrutural e de modelo, sem impacto direto em performance ou carga.

# Pontos que precisam de esclarecimento

- O `UserUpdateRequest` permite campos nulos? O sistema deve aceitar atualização parcial?  
  (O código do serviço sugere sim, mas não há anotação explícita para `@NotNull`.)

- Como o controlador que recebe `UserUpdateRequest` trata a validação? Usa `@Valid`?  
  (Não há diff nem evidência direta do controlador atual.)

- Qual o comportamento esperado se ambos os campos forem nulos?  
  (O serviço mantém dados antigos, mas o controlador deve permitir isso?)

- Há necessidade de validação adicional, como evitar atualização para email já existente?  
  (No `UserCreateRequest` há verificação de email duplicado, mas não está claro para atualização.)

- O limite mínimo de 3 caracteres para nome é adequado para todos os casos de uso?  
  (Pode rejeitar nomes legítimos muito curtos.)

---

# Resumo

A mudança introduz um novo record `UserUpdateRequest` com validação para nome e email, que será usado para atualizar usuários. Isso formaliza o payload de atualização e adiciona restrições básicas. O impacto funcional está na validação e no transporte dos dados de atualização. Riscos reais incluem validação parcial e ausência de testes específicos. Recomenda-se testes manuais e automatizados focados em validação, atualização parcial e limites dos campos. Pontos de negócio e implementação precisam ser esclarecidos para garantir comportamento consistente e evitar regressões.

---

# Arquivo analisado: java-api/src/main/java/com/repoalvo/javaapi/service/UserService.java

# Tipo da mudança

Implementação de nova funcionalidade: adição do método `update` para atualização parcial de usuários na classe `UserService`.

---

# Evidências observadas

- **Diff**: Inclusão do método `update(int userId, UserUpdateRequest payload)` na classe `UserService`.
- **Implementação**: O método é `synchronized` e percorre a lista interna `users` para localizar o usuário pelo `id`. Se encontrado, cria um novo objeto `UserResponse` com os campos atualizados (nome e email), preservando os valores antigos caso o payload não forneça novos valores (`null`).
- **Contexto do arquivo**: A classe `UserService` mantém uma lista em memória (`users`) de objetos `UserResponse` e já possui métodos sincronizados para listagem, busca, criação e busca por email.
- **Contexto do repositório**: 
  - Existe um modelo `UserUpdateRequest` importado, presumivelmente com campos `name` e `email` que podem ser nulos para indicar atualização parcial.
  - Testes unitários para `UserService` existem (`UserServiceUnitTest.java`), mas não há evidência de testes para o método `update`.
  - A API REST em `UserController` e testes relacionados indicam que a camada de serviço é consumida por controladores REST, mas não há evidência direta de endpoint para atualização de usuário (PUT/PATCH) no trecho fornecido.

---

# Impacto provável

- **Funcionalidade adicionada**: Permite atualizar parcialmente os dados de um usuário existente, alterando nome e/ou email.
- **Estado interno**: A lista `users` é modificada substituindo o objeto antigo pelo novo atualizado, mantendo a imutabilidade do objeto `UserResponse`.
- **Concorrência**: O método é sincronizado, mantendo a consistência da lista em ambiente multithread.
- **Possível uso futuro**: Pode ser utilizado por um endpoint REST para atualização de usuário, ainda que não esteja visível no contexto atual.
- **Sem alteração em outras funcionalidades**: Métodos existentes não foram alterados, portanto, comportamento atual de listagem, criação e busca permanece inalterado.

---

# Riscos identificados

- **Ausência de validação de dados**: O método aceita `UserUpdateRequest` com campos possivelmente nulos, mas não valida formatos (ex: email válido) ou regras de negócio (ex: email duplicado). Isso pode permitir atualização para dados inválidos ou duplicados.
- **Atualização de email para valor já existente**: Não há checagem para evitar que o email atualizado conflite com outro usuário já cadastrado, o que pode quebrar a regra de unicidade observada na criação.
- **Retorno de Optional.empty()**: Caso o usuário não exista, o método retorna `Optional.empty()`. Se o controlador não tratar isso adequadamente, pode gerar erros ou respostas inconsistentes.
- **Imutabilidade parcial**: O método cria novo objeto `UserResponse` para substituir o antigo, mas se houver referências externas ao objeto antigo, podem ficar desatualizadas.
- **Falta de testes específicos**: Não há evidência de testes unitários ou de integração cobrindo o novo método, o que aumenta o risco de regressão ou comportamento inesperado.
- **Possível inconsistência com outras camadas**: Se o controlador ou outras camadas não estiverem preparadas para lidar com atualização parcial, pode haver falhas ou erros.

---

# Cenários de testes manuais

1. **Atualização parcial com nome apenas**
   - Atualizar usuário existente passando somente o campo `name` no payload.
   - Verificar que o nome foi alterado e o email permaneceu o mesmo.

2. **Atualização parcial com email apenas**
   - Atualizar usuário existente passando somente o campo `email`.
   - Verificar que o email foi alterado e o nome permaneceu o mesmo.

3. **Atualização completa com nome e email**
   - Atualizar usuário existente passando ambos os campos.
   - Verificar que ambos foram atualizados corretamente.

4. **Atualização com campos nulos (sem alteração)**
   - Passar payload com `name` e `email` nulos.
   - Verificar que o usuário permanece inalterado.

5. **Atualização de usuário inexistente**
   - Tentar atualizar usuário com `userId` que não existe.
   - Verificar que o retorno é vazio (Optional.empty) e que o sistema responde adequadamente (ex: 404 se via API).

6. **Atualização com email já existente em outro usuário**
   - Tentar atualizar o email para um valor que já está cadastrado em outro usuário.
   - Verificar se o sistema permite ou bloqueia (atualmente não bloqueia, risco identificado).

7. **Concorrência**
   - Simular múltiplas atualizações simultâneas para o mesmo usuário.
   - Verificar se o estado final é consistente e sem erros.

---

# Sugestões de testes unitários

1. **update_shouldReturnUpdatedUser_whenUserExistsAndPayloadHasNameAndEmail**
   - Criar usuário, atualizar com nome e email novos.
   - Verificar que o objeto retornado tem os valores atualizados.

2. **update_shouldReturnUpdatedUser_whenPayloadHasOnlyName**
   - Atualizar usuário com apenas nome.
   - Verificar que email permanece o mesmo.

3. **update_shouldReturnUpdatedUser_whenPayloadHasOnlyEmail**
   - Atualizar usuário com apenas email.
   - Verificar que nome permanece o mesmo.

4. **update_shouldReturnEmpty_whenUserDoesNotExist**
   - Tentar atualizar usuário inexistente.
   - Verificar retorno Optional.empty().

5. **update_shouldNotModifyUser_whenPayloadHasNullFields**
   - Passar payload com campos nulos.
   - Verificar que usuário não é alterado.

6. **update_shouldReplaceUserInList**
   - Verificar que o usuário na lista interna é substituído pelo novo objeto atualizado.

7. **update_shouldBeThreadSafe**
   - Testar concorrência com múltiplas threads atualizando usuários.

---

# Sugestões de testes de integração

1. **PUT /users/{id} com payload parcial atualiza usuário**
   - Se existir endpoint REST para update, testar atualização parcial via API.
   - Verificar resposta HTTP 200 e dados atualizados.

2. **PUT /users/{id} com usuário inexistente retorna 404**
   - Testar atualização para id não cadastrado.

3. **PUT /users/{id} com email duplicado retorna erro**
   - Se regra de negócio for implementada, testar conflito de email.

4. **Fluxo completo: criar usuário → atualizar parcialmente → buscar e validar**
   - Criar usuário via API, atualizar parcialmente, buscar e validar dados.

5. **Atualização com payload inválido (ex: email mal formatado)**
   - Testar validação e resposta adequada (400 Bad Request).

---

# Sugestões de testes de carga ou desempenho

- **Não aplicável**: A mudança não indica impacto direto em performance ou carga, pois é uma operação simples em lista em memória com sincronização.

---

# Pontos que precisam de esclarecimento

1. **Existe endpoint REST para atualização de usuário?**
   - O controlador `UserController` não mostra método para update. Será que o método `update` será exposto via API? Se sim, qual o verbo HTTP e rota?

2. **Validação de dados no update**
   - Deve o método validar formato de email ou outras regras? Atualmente não há validação.

3. **Regra de unicidade de email na atualização**
   - Deve o método impedir atualização para email já existente em outro usuário? Atualmente não há essa checagem.

4. **Comportamento esperado para campos nulos no payload**
   - A implementação atual mantém valores antigos se o campo for nulo. Isso está alinhado com a regra de negócio?

5. **Imutabilidade e referências externas**
   - O objeto `UserResponse` é substituído na lista. Há risco de referências externas ficarem desatualizadas? Isso é aceitável?

---

# Resumo

A mudança adiciona um método `update` para atualização parcial de usuários na lista em memória, com sincronização para segurança de thread. O método substitui o objeto antigo por um novo com campos atualizados, preservando valores antigos quando o payload não fornece novos dados. Não há validação de dados nem checagem de unicidade de email, o que pode gerar inconsistências. Não há evidência de testes cobrindo essa funcionalidade nem de endpoint REST para expô-la. Recomenda-se criar testes unitários e de integração específicos para validar comportamento correto, tratar casos de erro e definir regras de negócio claras para validação e unicidade.