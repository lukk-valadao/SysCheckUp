SysCheckUp v1.3

Ferramenta: SysCheck-Up
Versão: 1.3
Descrição: Painel interativo de verificação, limpeza e segurança para sistemas Debian-based.
Autores: Shadows & Aeris Satana

Descrição do Projeto

O SysCheckUp é um script em Bash que oferece uma interface interativa para realizar verificações de sistema, limpeza, análise de segurança e auditoria básica em sistemas Debian e derivados.

Ele inclui funções como atualização de pacotes, limpeza de cache, verificação de firewall, scan de vírus, checagem de integridade de pacotes, e mais.

O script pode ser executado de forma interativa (SysCheckUp.sh), permitindo que o usuário escolha quais verificações deseja realizar, ou de forma automática (SysCheckUp_automatic.sh), via agendamento com systemd timer.

Estrutura do Projeto
SysCheckUp/
│
├─ SysCheckUp.sh            # Script principal (modo interativo)
├─ SysCheckUp_automatic.sh  # Script com agendamento automático
├─ Logs/                    # Diretório para logs gerados pelo script
├─ README.md                # Este arquivo de documentação
└─ modules/                 # Futuramente, funções/módulos separados

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

git clone https://github.com/lukk-valadao/SysCheckUp.git
cd SysCheckUp


Torne o script executável:

chmod +x SysCheckUp.sh


Execute o script (modo interativo):

./SysCheckUp.sh

Execução Automática (SysCheckUp_automatic.sh)

O script SysCheckUp_automatic.sh foi projetado para rodar sem interação, ideal para agendamento recorrente.

Ele é integrado ao systemd timer, permitindo que o sistema rode o check-up de forma periódica (ex.: semanal).

Instalação do serviço e timer

Copie os arquivos de serviço e timer para o systemd:

sudo cp syscheckup.service /etc/systemd/system/
sudo cp syscheckup.timer /etc/systemd/system/


Recarregue o systemd e ative o timer:

sudo systemctl daemon-reload
sudo systemctl enable --now syscheckup.timer

Verificação do status

Checar se o timer está ativo:

systemctl list-timers | grep syscheckup


Forçar uma execução manual:

sudo systemctl start syscheckup.service


Todos os resultados ficam salvos em SysCheckUp/Logs/ com data e hora.

Observações

Os logs são salvos automaticamente na pasta Logs/ com timestamp.

Algumas funções exigem privilégios de superusuário (sudo).

A primeira execução pode instalar pacotes necessários como clamav, deborphan, debsums e ufw.

.gitignore recomendado
Logs/*
*.log
*.tmp
*.swp


Isso evita versionar logs ou arquivos temporários do script.

Licença

Projeto privado, sem licença pública no momento.

Desenvolvedores: Shadows & Aeris Satana
