![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)


# 🛡️ SysCheckUp v1.4.1

**Ferramenta:** SysCheck-Up | **Versão:** 1.4.1
**Descrição:** Painel interativo de verificação, limpeza e segurança para sistemas Debian-based.
**Autor:** Luciano Valadão

---

## 📄 Descrição do Projeto

O **SysCheckUp** é um script robusto escrito em **Bash** que fornece uma interface interativa completa para administradores e usuários de sistemas **Debian e derivados (Ubuntu, Mint)**. Ele automatiza verificações essenciais de sistema, limpeza de disco, análise de segurança e auditoria básica.

O toolkit oferece dois modos de operação:

1.  **Interativo (`SysCheckUp.sh`):** Permite ao usuário escolher quais verificações deseja executar através de um menu.
2.  **Automático (`SysCheckUp_automatic.sh`):** Projetado para ser executado sem interação, ideal para agendamento recorrente via `systemd timer`.

---

## 📂 Estrutura do Projeto

O projeto é organizado com foco na manutenção e na integração com o `systemd`:
```
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
```
---

## 🔎 Funcionalidades Principais

```
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
```

> **📌 Nota:** Todas as operações geram logs detalhados na pasta `Logs/` com *timestamp* automático.

---

## ⚙️ Execução Manual (Modo Interativo)

Para utilizar o menu interativo, siga os passos abaixo:

### 1. Clonar e Acessar

bash
```
git clone [https://github.com/lukk-valadao/SysCheckUp.git](https://github.com/lukk-valadao/SysCheckUp.git)
cd SysCheckUp
```
2. Tornar Executável
Conceda permissão de execução ao script principal:
Bash
```
chmod +x SysCheckUp.sh
```
3. Executar
Execute o script para iniciar o painel interativo:
Bash
```
./SysCheckUp.sh
```

⏱️ Execução Automática (systemd Timer)
O script SysCheckUp_automatic.sh é ideal para tarefas recorrentes. Ele pode ser agendado usando o systemd timer.
1. Instalação do Serviço e Timer
Copie os arquivos de serviço e timer para o diretório do systemd:
Bash
```
sudo cp syscheckup.service /etc/systemd/system/
sudo cp syscheckup.timer /etc/systemd/system/
```
2. Ativação do Agendamento
Recarregue o daemon do systemd e ative o timer. Isso fará com que o check-up seja executado periodicamente (conforme configurado no .timer):
Bash
```
sudo systemctl daemon-reload
sudo systemctl enable --now syscheckup.timer
```
3. Verificação do Status
Para checar se o timer está ativo e qual é o próximo agendamento:
Bash
```
systemctl list-timers | grep syscheckup
```
Para forçar uma execução manual imediata do serviço:
Bash
```
sudo systemctl start syscheckup.service
```
📌 Observação: Os resultados das execuções automáticas e manuais são salvos em SysCheckUp/Logs/ com data e hora.

⚠️ Observações e Dependências
Privilégios: Algumas funções críticas (como atualização e configuração de firewall) exigem privilégios de superusuário (sudo).
Dependências: A primeira execução do script pode instalar pacotes necessários como clamav, deborphan, debsums e ufw.
.gitignore Recomendado
Use o seguinte conteúdo no seu arquivo .gitignore para evitar o versionamento de dados temporários e logs:
Snippet de código
Logs/*
*.log
*.tmp
*.swp


📜 Licença
Projeto privado. Licença pública não definida no momento.
Autor: Luciano Valadão - lukk.valadao@gmail.com
