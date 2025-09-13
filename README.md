 SysCheckUp v1.3:

# SysCheckUp v1.3

**Ferramenta:** SysCheck-Up
**Versão:** 1.3
**Descrição:** Painel interativo de verificação, limpeza e segurança para sistemas Debian-based.
**Autor:** Shadows & Aeris Satana

---

## Descrição do Projeto

O **SysCheckUp** é um script em Bash que oferece uma interface interativa para realizar verificações de sistema, limpeza, análise de segurança e auditoria básica em sistemas Debian e derivados. Ele inclui funções como atualização de pacotes, limpeza de cache, verificação de firewall, scan de vírus, checagem de integridade de pacotes, e mais.

O script pode ser executado de forma modular, permitindo que o usuário escolha quais verificações deseja realizar, ou executar todas em sequência, com confirmação `s/n` antes de cada uma.

---

## Estrutura do Projeto

```text
SysCheckUp/
│
├─ SysCheckUp.sh        # Script principal
├─ Logs/                # Diretório para logs gerados pelo script
├─ README.md            # Este arquivo de documentação
└─ modules/             # Futuramente, funções/módulos separados

Funcionalidades Principais

Atualização do sistema (apt update && apt upgrade)

Limpeza de pacotes e cache (autoremove, autoclean, limpeza de thumbnails e lixeira)

Verificação e configuração do firewall UFW

Scan de vírus com ClamAV (opcional, com exclusão de Metasploit)

Identificação de pacotes órfãos (deborphan)

Verificação de diretórios de backup comuns

Listagem de usuários com privilégios sudo

Listagem de serviços ativos (systemctl)

Verificação de espaço em disco (df -h)

Listagem de conexões de rede ativas (ss -tulnp)

Checagem de integridade de pacotes (debsums)

O script também gera um log detalhado de todas as operações na pasta Logs/.

Instalação

Clone o repositório:

git clone https://github.com/lukk-valadao/SysCheckUp.git
cd SysCheckUp


Torne o script executável:

chmod +x SysCheckUp.sh


Execute o script:

./SysCheckUp.sh

Observações

Os logs são salvos automaticamente na pasta Logs/ com timestamp.

Algumas funções podem exigir privilégios de superusuário (sudo).

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
