#!/bin/bash

# Ferramenta: SysCheck-Up v1.4.1
# Descrição: Painel interativo de verificação, limpeza e segurança para sistemas Debian-based
# Autor: Luciano Valadão

# === CORES PARA TERMINAL ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Diretório do script e logs
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$BASE_DIR/Logs"
mkdir -p "$LOG_DIR"
log_file="$LOG_DIR/syscheckup_$(date +%F_%H-%M-%S).log"
echo "[+] LOG INICIADO: $log_file"

log() {
  echo -e "$1" | tee -a "$log_file"
}

pause() {
  read -rp "Pressione Enter para continuar..."
}

# === FUNÇÕES DE INTERFACE ===

spinner() {
  local pid=$1
  local delay=0.1
  local spinstr='|/-\'
  while ps -p $pid > /dev/null 2>&1; do
    local temp=${spinstr#?}
    printf " [%c]  " "$spinstr"
    local spinstr=$temp${spinstr%"$temp"}
    sleep $delay
    printf "\b\b\b\b\b\b"
  done
}

progress_bar_step() {
  local progress=$1
  local total=$2
  local percent=$((progress * 100 / total))
  local filled=$((percent / 2))
  local empty=$((50 - filled))
  printf "\r[%-${filled}s%${empty}s] %d%%" "#" "" "$percent"
}

progress_bar_global() {
  local progress=$1
  local total=$2
  local percent=$((progress * 100 / total))
  local filled=$((percent / 2))
  local empty=$((50 - filled))
  printf "\rProgresso total: [%-${filled}s%${empty}s] %d%%" "#" "" "$percent"
}

atualizacoes() {
    log "${YELLOW}[1/12] Verificando atualizações do sistema...${NC}"

    # Atualiza lista de pacotes e salva log temporário
    sudo apt update 2>&1 | tee /tmp/apt_update.log | tee -a "$log_file"

    # Verifica erros comuns de repositórios inválidos
    if grep -q "does not have a Release file" /tmp/apt_update.log || grep -q "404  Not Found" /tmp/apt_update.log; then
        echo -e "\n⚠️  Um ou mais repositórios falharam durante a atualização."
        echo "Deseja desabilitar automaticamente os repositórios inválidos?"
        echo "1) Sim"
        echo "2) Não"
        read -rp "Escolha [1-2]: " opt

        if [[ "$opt" == "1" ]]; then
            for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do
                if [[ -f "$f" ]] && grep -q "greenbone" "$f"; then
                    sudo sed -i 's/^/#DESABILITADO # /' "$f"
                    echo "👉 Repositório $f desabilitado."
                fi
            done
            echo "🔄 Reexecutando atualização com repositórios válidos..."
            sudo apt update | tee -a "$log_file"
        else
            echo "👉 Repositórios inválidos foram ignorados."
        fi
    fi

    # Conta pacotes disponíveis
    UPDATES=$(apt list --upgradable 2>/dev/null | grep -c upgradable)

    if [ "$UPDATES" -gt 0 ]; then
        echo -e "${GREEN}[$UPDATES pacotes disponíveis para atualização]${NC}"
        echo -e "\n📦 ${YELLOW}Pacotes disponíveis:${NC}"
        apt list --upgradable 2>/dev/null | grep upgradable | sed 's/\(upgradable.*\)//' | sed 's/^/   • /'
        echo

        read -rp "Deseja instalar as atualizações agora? (s/n) " choice

        if [[ "$choice" =~ ^[Ss]$ ]]; then
            echo -e "\n1) Upgrade normal (seguro)"
            echo "2) Full-upgrade (atualiza tudo, incluindo substituições de pacotes)"
            read -rp "Escolha o tipo de atualização [1-2]: " upg_choice

            if [[ "$upg_choice" == "1" ]]; then
                log "Iniciando upgrade normal..."
                sudo apt upgrade -y | tee -a "$log_file"
            else
                log "Iniciando full-upgrade..."
                sudo apt full-upgrade -y | tee -a "$log_file"
            fi
            echo -e "\n${GREEN}✅ Atualizações concluídas.${NC}"
        else
            log "Atualização não instalada."
        fi
    else
        echo -e "${GREEN}✅ Sistema já está atualizado.${NC}"
    fi
    echo
    read -rp "Pressione Enter para continuar..."
}




limpeza() {
  log "${YELLOW}[2/12] Limpando pacotes e cache...${NC}"
  etapas=4
  etapa=0

  sudo apt autoremove -y | tee -a "$log_file"
  etapa=$((etapa+1)); progress_bar_step $etapa $etapas

  sudo apt autoclean -y | tee -a "$log_file"
  etapa=$((etapa+1)); progress_bar_step $etapa $etapas

  sudo journalctl --vacuum-time=5d | tee -a "$log_file"
  etapa=$((etapa+1)); progress_bar_step $etapa $etapas

  read -rp "Deseja esvaziar a lixeira? (s/n) " limpar_lixeira
  if [[ "$limpar_lixeira" =~ ^[Ss]$ ]]; then
    rm -rf ~/.local/share/Trash/* 2>/dev/null
    log "Lixeira esvaziada."
  else
    log "Lixeira não foi esvaziada."
  fi
  etapa=$((etapa+1)); progress_bar_step $etapa $etapas

  echo -e "\nLimpeza concluída!"
}

firewall() {
  log "${YELLOW}[3/12] Verificando status do firewall (UFW)...${NC}"
  export PATH=$PATH:/usr/sbin

  # Verifica se o UFW está instalado
  if ! dpkg -l | grep -q '^ii  ufw '; then
    log "${RED}Firewall UFW não encontrado. Instalando...${NC}"
    sudo apt update -y | tee -a "$log_file"
    sudo apt install ufw -y | tee -a "$log_file"
    sudo ufw enable | tee -a "$log_file"
    log "${GREEN}✅ UFW instalado e ativado.${NC}"
  fi

  # Exibe status atual
  sudo ufw status verbose | tee -a "$log_file"

  # Lista de portas suspeitas e serviços relacionados
  declare -A portas=(
    ["22"]="ssh"
    ["25"]="exim4"
    ["631"]="cups"
  )

  for porta in "${!portas[@]}"; do
    if sudo ufw status | grep -qE "^$porta.*ALLOW"; then
      read -rp "[!] Porta $porta (${portas[$porta]}) aberta. Deseja fechá-la? (s/n) " fechar
      if [[ "$fechar" =~ ^[Ss]$ ]]; then
        if systemctl is-active --quiet "${portas[$porta]}"; then
          log "[$porta] Parando serviço ${portas[$porta]}..."
          sudo systemctl stop "${portas[$porta]}"
        fi
        if systemctl is-enabled --quiet "${portas[$porta]}"; then
          log "[$porta] Desabilitando serviço ${portas[$porta]} no boot..."
          sudo systemctl disable "${portas[$porta]}"
        fi
        sudo ufw deny "$porta"
        log "[$porta] 🔒 Porta fechada com sucesso."
      else
        log "[$porta] 🚪 Porta mantida aberta."
      fi
    else
      log "[$porta] Porta não detectada como aberta."
    fi
  done

  log "${GREEN}✅ Firewall processado com sucesso.${NC}"
}


clamav_scan() {
  log "${YELLOW}[4/12] Verificando presença do ClamAV...${NC}"
  if ! command -v clamscan >/dev/null; then
    log "${RED}ClamAV não encontrado. Instalando...${NC}"
    sudo apt install clamav clamav-daemon -y | tee -a "$log_file"
    sudo freshclam | tee -a "$log_file"
  fi
  read -rp "Deseja executar o scan completo de vírus em /home? (s/n) " choice
  if [[ "$choice" =~ ^[Ss]$ ]]; then
    log "Executando varredura básica de vírus em /home (Metasploit será excluído)..."
    (sudo clamscan -r /home --exclude-dir=/home/*/metasploit-framework --bell -i | tee -a "$log_file") &
    spinner $!
    wait
    echo
  else
    log "Scan de vírus pulado."
  fi
}


pacotes_orfaos() {
  log "${YELLOW}[5/12] Verificando pacotes órfãos...${NC}"
  if ! command -v deborphan >/dev/null; then
    sudo apt install deborphan -y
  fi
  ORFAOS=$(deborphan)
  if [[ -n "$ORFAOS" ]]; then
    log "Pacotes órfãos encontrados:\n$ORFAOS"
    read -rp "Deseja removê-los? (s/n) " rm_orfaos
    if [[ "$rm_orfaos" =~ ^[Ss]$ ]]; then
      sudo apt remove --purge -y $ORFAOS
      log "Pacotes órfãos removidos."
    fi
  else
    log "Nenhum pacote órfão."
  fi
}

backup_check() {
  log "${YELLOW}[6/12] Backup...${NC}"
  echo "Escolha tipo de backup: 1) Leve 2) Completo 3) Sem backup"
  read -rp "Opção: " opt
  case $opt in
    1) log "Backup leve: apenas configs /home/$(whoami) e /etc/"; mkdir -p ~/backup_leve; cp -r ~/.* ~/backup_leve 2>/dev/null; cp -r /etc ~/backup_leve 2>/dev/null ;;
    2) log "Backup completo em ~/backup_completo"; mkdir -p ~/backup_completo; cp -r /home ~/backup_completo; cp -r /etc ~/backup_completo ;;
    3) log "Backup ignorado." ;;
    *) log "Opção inválida. Backup ignorado." ;;
  esac
}

usuarios_sudo() {
  log "${YELLOW}[7/12] Verificando usuários com privilégios sudo...${NC}"
  getent group sudo | awk -F: '{print $4}' | tr ',' '\n' | tee -a "$log_file"
}

servicos_ativos() {
  log "${YELLOW}[8/12] Serviços ativos...${NC}"
  black_list=(avahi-daemon exim4 cups cups-browsed ModemManager)
  for svc in "${black_list[@]}"; do
    if systemctl is-active --quiet $svc; then
      read -rp "Serviço $svc ativo. Deseja desativar? (s/n) " ans
      [[ "$ans" =~ ^[Ss]$ ]] && sudo systemctl disable --now $svc && log "$svc desativado."
    fi
  done
  systemctl list-units --type=service --state=running | tee -a "$log_file"
}


espaco_disco() {
  log "${YELLOW}[9/12] Verificando espaço em disco...${NC}"
  df -h | tee -a "$log_file"
}

conexoes_rede() {
  log "${YELLOW}[10/12] Listando conexões de rede ativas...${NC}"
  ss -tulnp | tee -a "$log_file"
}

integridade_sistema() {
  log "${YELLOW}[11/12] Checando integridade de pacotes do sistema...${NC}"
  if command -v debsums >/dev/null; then
    sudo debsums -s | tee -a "$log_file"
  else
    log "${RED}debsums não encontrado. Instalando...${NC}"
    sudo apt install debsums -y | tee -a "$log_file"
    sudo debsums -s | tee -a "$log_file"
  fi
}

sair() {
  log "${GREEN}✅ Verificações concluídas. Relatório salvo em: $log_file${NC}"
  exit 0
}

# === FUNÇÃO PARA EXECUTAR TODOS COM PERGUNTA S/N ===
executar_tudo() {
  funcs=(atualizacoes limpeza firewall clamav_scan pacotes_orfaos backup_check usuarios_sudo servicos_ativos espaco_disco conexoes_rede integridade_sistema)
  total=${#funcs[@]}
  count=0

  for func in "${funcs[@]}"; do
    read -rp "Deseja executar $func? (s/n) " choice
    if [[ "$choice" =~ ^[Ss]$ ]]; then
      $func
    else
      log "$func pulado."
    fi
    ((count++))
    progress_bar_global $count $total
  done
  echo -e "\n${GREEN}✅ Todos os módulos processados.${NC}"
}

# === MENU INTERATIVO ===
while true; do
  clear
  echo -e "${GREEN}=== SysCheck-Up v1.4.1 ===${NC}"
  echo "1) Atualizações do sistema"
  echo "2) Limpeza de pacotes e cache"
  echo "3) Firewall (UFW)"
  echo "4) Scan de vírus (ClamAV)"
  echo "5) Pacotes órfãos"
  echo "6) Diretórios de backup"
  echo "7) Usuários com privilégios sudo"
  echo "8) Serviços ativos"
  echo "9) Espaço em disco"
  echo "10) Conexões de rede"
  echo "11) Integridade de pacotes do sistema"
  echo "12) Executar tudo (com perguntas s/n)"
  echo "13) Sair"
  read -rp "Escolha uma opção: " opt

  case $opt in
    1) atualizacoes ;;
    2) limpeza ;;
    3) firewall ;;
    4) clamav_scan ;;
    5) pacotes_orfaos ;;
    6) backup_check ;;
    7) usuarios_sudo ;;
    8) servicos_ativos ;;
    9) espaco_disco ;;
    10) conexoes_rede ;;
    11) integridade_sistema ;;
    12) executar_tudo ;;
    13) sair ;;
    *) echo -e "${RED}Opção inválida${NC}" ;;
  esac
  pause
done
