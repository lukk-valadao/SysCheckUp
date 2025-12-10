# SysCheckUp v1.4.1

**Ferramenta:** SysCheck-Up
**Versão:** 1.4.1
**Descrição:** Painel interativo de verificação, limpeza e segurança para sistemas Debian-based.
**Autor:** Luciano S Valadão

---

## Descrição do Projeto

O **SysCheckUp** é um script em Bash que oferece uma interface interativa para realizar verificações de sistema, limpeza, análise de segurança e auditoria básica em sistemas Debian e derivados.

Ele inclui funções como atualização de pacotes, limpeza de cache, verificação de firewall, scan de vírus, checagem de integridade de pacotes, e mais.

O script pode ser executado de forma **interativa** (`SysCheckUp.sh`), permitindo que o usuário escolha quais verificações deseja realizar, ou de forma **automática** (`SysCheckUp_automatic.sh`), via agendamento com **systemd timer**.

---

## Estrutura do Projeto

```text
SysCheckUp/
│
├─ SysCheckUp.sh              # Script principal (modo interativo)
├─ SysCheckUp_automatic.sh    # Script com agendamento automático
├─ syscheckup.service         # Unidade systemd para execução automática
├─ syscheckup.timer           # Timer systemd para agendamento
├─ README.md                  # Este arquivo de documentação
├─ VERSIONS.md                # Histórico da versões
├─ Logs/                      # Diretório para logs gerados pelo script
└─ modules/                   # Funções/módulos separados
   └─ sc.py                   # Script SysCheckUp.sh adaptado para python

Funcionalidades Principais

Atualização do sistema (apt update && apt upgrade)

Limpeza de pacotes e cache (autoremove, autoclean, thumbnails, lixeira)

Verificação e configuração do firewall UFW

Scan de vírus com ClamAV (opcional, com exclusão de Metasploit)

Identificação de pacotes órfãos (deborphan)

Verificação de diretórios de backup comuns

Listagem de usuários com privilégios sudo

Relatório de serviços ativos (systemctl)

Monitoramento de espaço em disco (df -h)

Listagem de conexões de rede ativas (ss -tulnp)

Checagem de integridade de pacotes (debsums)

📌 O script também gera logs detalhados de todas as operações na pasta Logs/, com timestamp automático.

Execução Manual

Clone o repositório:
Copiar código
git clone https://github.com/lukk-valadao/SysCheckUp.git
cd SysCheckUp

Torne o script executável:
Copiar código
chmod +x SysCheckUp.sh

Execute o script (modo interativo):
Copiar código
./SysCheckUp.sh

Execução Automática (SysCheckUp_automatic.sh)
O script SysCheckUp_automatic.sh foi projetado para rodar sem interação, ideal para agendamento recorrente.
Ele é integrado ao systemd timer, permitindo que o sistema rode o check-up de forma periódica (ex.: semanal).

Instalação do serviço e timer
Copie os arquivos de serviço e timer para o systemd:

Copiar código
sudo cp syscheckup.service /etc/systemd/system/
sudo cp syscheckup.timer /etc/systemd/system/
Recarregue o systemd e ative o timer:

Copiar código
sudo systemctl daemon-reload
sudo systemctl enable --now syscheckup.timer
Verificação do status
Checar se o timer está ativo:

Copiar código
systemctl list-timers | grep syscheckup
Forçar uma execução manual:

Copiar código
sudo systemctl start syscheckup.service
📌 Todos os resultados ficam salvos em SysCheckUp/Logs/ com data e hora.

Observações
Os logs são salvos automaticamente na pasta Logs/ com timestamp.

Algumas funções exigem privilégios de superusuário (sudo).

A primeira execução pode instalar pacotes necessários como clamav, deborphan, debsums e ufw.

.gitignore recomendado
gitignore

Logs/*
*.log
*.tmp
*.swp
Isso evita versionar logs ou arquivos temporários do script.

Licença
Projeto privado, sem licença pública no momento.

Desenvolvedor: Luciano Valadão
