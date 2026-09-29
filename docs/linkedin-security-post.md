# Post para LinkedIn

Segurança de software não acontece só na autenticação. Ela precisa acompanhar o caminho real de cada operação.

Nesta etapa do Smart Schedule, reforcei alguns desses pontos:

- O atendimento pelo WhatsApp consulta apenas os agendamentos associados ao telefone de origem e à empresa correta.
- O cancelamento exige confirmação do mesmo remetente e preserva o registro no histórico.
- Cadastros antigos só passam a ser atendidos pelo WhatsApp depois que a equipe confirma o vínculo do telefone.
- A imagem Docker deixa de copiar o projeto inteiro: segredos, bancos locais, ambientes virtuais e outros artefatos ficam fora do build.

Também ampliei a cobertura dos fluxos de autorização. A suíte passou com 100 testes; o build e o lint do frontend também foram validados.

É um passo de melhoria contínua: segurança precisa ser revisada junto com o produto, as integrações e a forma como ele é distribuído.

#SegurancaDaInformacao #DesenvolvimentoDeSoftware #FastAPI #React #DevSecOps

Arte: [linkedin-security-hardening.png](screenshots/linkedin-security-hardening.png)