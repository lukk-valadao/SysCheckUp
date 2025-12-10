# Histórico de Versões - SysCheckUp

Este arquivo documenta todas as versões do SysCheckUp, suas datas e as alterações principais realizadas.

| Versão | Data       | Alterações / Descrição |
|--------|------------|-----------------------|
| 1.0    | 2025-08-10 | Primeira versão funcional, incluía atualização de sistema e limpeza básica. |
| 1.1    | 2025-08-15 | Adição de verificação de firewall, scan básico de vírus ClamAV e pacotes órfãos. |
| 1.2    | 2025-08-22 | Inclusão de checagem de backups, usuários sudo e espaço em disco. |
| 1.3    | 2025-09-12 | Painel interativo completo, scan ClamAV opcional, registro de logs na pasta Logs/, menu interativo e opção "Executar tudo" com confirmação s/n. |
| 1.4    | 2025-09-12 | Adicionados SysCheckUp_automatic.sh, service e timer systemd |
| 1.4.1  | 2025-10-03 | Correção do módulo de atualizações: agora o SysCheckUp detecta repositórios inválidos ou quebrados, oferece opção para desabilitá-los automaticamente e permite a instalação interativa de pacotes     || |                     | disponíveis. Logs detalhados são mantidos para referência. Função atualizações revisada e aprimorada — com exibição dos nomes dos pacotes disponíveis.|


## Observações
- Todas as alterações importantes devem ser registradas neste arquivo antes de atualizar a versão do script.
- Logs continuam sendo salvos na pasta `Logs/` do projeto.


# Histórico de Versões - SysCheckUp - versão Python

| Versão | Data       | Alterações / Descrição |
|--------|------------|-----------------------|
| 1.0    | 2025-02-12 | Primeira versão funcional, inclui todas as funções executados pela versão Shell. |
