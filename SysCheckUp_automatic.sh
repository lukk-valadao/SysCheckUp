#!/bin/bash

# Ferramenta: SysCheck-Up v1.0-auto
# Descrição: Versão automática do SysCheck-Up para execução via cron ou systemd
# Autor: Luciano Valadão

# === CORES PARA TERMINAL ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Diretório do script e logs
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$BASE_DIR/Logs"
mkdir -p "$LOG_DIR"
log_file="$LOG_DIR/syscheckup_auto_$(date +%F_%H-%M-%S).log"
echo "[+] LOG INICIADO: $log_file"

log() {
  echo -e "$1" | tee -a "$log_file"
}

# === FUNÇÕES ===

atualizacoes() {
  log "${YELLOW}[1/11] Atualizando sistema...${NC}"
  sudo apt update && sudo apt upgrade -y | tee -a "$log_file"
}

limpeza() {
  log "${YELLOW}[2/11] Limpando pacotes e cache...${NC}"
  sudo apt autoremove -y | tee -a "$log_file"
  sudo apt autoclean -y | tee -a "$log_file"
  sudo journalctl --vacuum-time=5d | tee -a "$log_file"
  rm -rf ~/.cache/thumbnails/* ~/.local/share/Trash/* ~/.thumbnails/* 2>/dev/null
}

firewall() {
  log "${YELLOW}[3/11] Verificando firewall (UFW)...${NC}"
  export PATH=$PATH:/usr/sbin
  if ! dpkg -l | grep -q '^ii  ufw '; then
      log "${RED}UFW não instalado, instalando...${NC}"
      sudo apt update
      sudo apt install ufw -y | tee -a "$log_file"
      sudo ufw enable | tee -a "$log_file"
  fi
  sudo ufw status verbose | tee -a "$log_file"
}

clamav_scan() {
  log "${YELLOW}[4/11] Verificando ClamAV...${NC}"
  if ! command -v clamscan >/dev/null; then
    log "${RED}ClamAV não instalado, instalando...${NC}"
    sudo apt install clamav clamav-daemon -y | tee -a "$log_file"
    sudo freshclam | tee -a "$log_file"
  fi
  log "Executando scan automático em /home (excluindo Metasploit)..."
  sudo clamscan -r /home --exclude-dir=/home/*/metasploit-framework --bell -i | tee -a "$log_file"
}

pacotes_orfaos() {
  log "${YELLOW}[5/11] Verificando pacotes órfãos...${NC}"
  if ! command -v deborphan >/dev/null; then
    sudo apt install deborphan -y | tee -a "$log_file"
  fi
  deborphan | tee -a "$log_file"
}

backup_check() {
  log "${YELLOW}[6/11] Verificando backups...${NC}"
  for dir in /mnt/backup /backup ~/backup; do
    if [ -d "$dir" ]; then
      log "Backup detectado: $dir"
    else
      log "${RED}Backup NÃO encontrado: $dir${NC}"
    fi
  done
}

usuarios_sudo() {
  log "${YELLOW}[7/11] Usuários com privilégios sudo...${NC}"
  getent group sudo | awk -F: '{print $4}' | tr ',' '\n' | tee -a "$log_file"
}

servicos_ativos() {
  log "${YELLOW}[8/11] Serviços ativos...${NC}"
  systemctl list-units --type=service --state=running | tee -a "$log_file"
}

espaco_disco() {
  log "${YELLOW}[9/11] Espaço em disco...${NC}"
  df -h | tee -a "$log_file"
}

conexoes_rede() {
  log "${YELLOW}[10/11] Conexões de rede ativas...${NC}"
  ss -tulnp | tee -a "$log_file"
}

integridade_sistema() {
  log "${YELLOW}[11/11] Verificando integridade de pacotes...${NC}"
  if ! command -v debsums >/dev/null; then
    sudo apt install debsums -y | tee -a "$log_file"
  fi
  sudo debsums -s | tee -a "$log_file"
}

# === EXECUÇÃO AUTOMÁTICA ===
log "${GREEN}=== Iniciando SysCheck-Up automático v1.3 ===${NC}"

atualizacoes
limpeza
firewall
clamav_scan
pacotes_orfaos
backup_check
usuarios_sudo
servicos_ativos
espaco_disco
conexoes_rede
integridade_sistema

log "${GREEN}✅ SysCheck-Up automático concluído. Log salvo em: $log_file${NC}"
exit 0

