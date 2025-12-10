#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SysCheck-Up v1.0 – Python Edition (com menu estendido)
# Autor: Luciano Valadão
# Objetivo: Portar funcionalidades do SysCheck-Up v1.4.1 para Python (Linux/Windows)

import os
import subprocess
import platform
import shutil
import tempfile
import datetime
import time
from pathlib import Path

# ====== CORES ======
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"

# ====== LOGGING ======
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "Logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"syscheckup_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log"

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def pause():
    input("Pressione Enter para continuar...")

def run_cmd(cmd, sudo=False):
    """Executa comando shell e retorna (stdout, stderr, exitcode)."""
    try:
        # no Windows, evitar shell=True com comandos compostos problemáticos
        proc = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        return proc.stdout.strip(), proc.stderr.strip(), proc.returncode
    except Exception as e:
        return "", str(e), 1

def is_linux():
    return platform.system() == "Linux"

def is_windows():
    return platform.system() == "Windows"

def spinner(text, duration=0.8):
    chars = "|/-\\"
    end = time.time() + duration
    while time.time() < end:
        for c in chars:
            print(f"\r[{c}] {text}", end="", flush=True)
            time.sleep(0.08)
    print("\r", end="")

# ====== MÓDULOS ======

def atualizacoes():
    log(f"{YELLOW}[1/12] Verificando atualizações do sistema...{NC}")
    if is_linux():
        # captura saída do apt update em arquivo temporário
        stdout, stderr, rc = run_cmd("sudo apt update 2>&1 | tee /tmp/apt_update.log")
        # lê o /tmp/apt_update.log para analisar
        try:
            with open("/tmp/apt_update.log", "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = stdout + "\n" + stderr

        if "does not have a Release file" in content or "404  Not Found" in content:
            log("⚠️  Um ou mais repositórios falharam durante a atualização.")
            opt = input("Deseja desabilitar automaticamente os repositórios inválidos? (1) Sim (2) Não : ")
            if opt.strip() == "1":
                # exemplo: desabilitar linhas contendo 'greenbone' (conforme original)
                for p in ["/etc/apt/sources.list"] + list(Path("/etc/apt/sources.list.d").glob("*.list")):
                    try:
                        txt = p.read_text(encoding="utf-8", errors="ignore")
                        if "greenbone" in txt:
                            new = ""
                            for line in txt.splitlines():
                                if "greenbone" in line and not line.strip().startswith("#"):
                                    new += "#DESABILITADO # " + line + "\n"
                                else:
                                    new += line + "\n"
                            p.write_text(new, encoding="utf-8")
                            log(f"👉 Repositório {p} desabilitado (linhas contendo 'greenbone').")
                    except Exception as e:
                        log(f"Erro ao processar {p}: {e}")
                log("🔄 Reexecutando atualização com repositórios válidos...")
                run_cmd("sudo apt update | tee -a " + str(LOG_FILE))
            else:
                log("👉 Repositórios inválidos foram ignorados.")
        # conta upgrades
        out, err, _ = run_cmd("apt list --upgradable 2>/dev/null | grep -c upgradable")
        try:
            updates = int(out.strip()) if out.strip().isdigit() else 0
        except:
            updates = 0

        if updates > 0:
            log(f"{GREEN}[{updates} pacotes disponíveis para atualização]{NC}")
            out, err, _ = run_cmd("apt list --upgradable 2>/dev/null | grep upgradable || true")
            if out:
                for line in out.splitlines():
                    pretty = line.split(" ")[0]
                    print(f"   • {pretty}")
            choice = input("Deseja instalar as atualizações agora? (s/n) ")
            if choice.lower().startswith("s"):
                print("1) Upgrade normal (seguro)")
                print("2) Full-upgrade (atualiza tudo, incluindo substituições de pacotes)")
                upg_choice = input("Escolha o tipo de atualização [1-2]: ")
                if upg_choice.strip() == "2":
                    log("Iniciando full-upgrade...")
                    run_cmd("sudo apt full-upgrade -y | tee -a " + str(LOG_FILE))
                else:
                    log("Iniciando upgrade normal...")
                    run_cmd("sudo apt upgrade -y | tee -a " + str(LOG_FILE))
                log(f"{GREEN}✅ Atualizações concluídas.{NC}")
            else:
                log("Atualização não instalada.")
        else:
            log(f"{GREEN}✅ Sistema já está atualizado.{NC}")
    elif is_windows():
        log("Atualizações (Windows) via Chocolatey (se instalado).")
        if shutil.which("choco"):
            out, err, rc = run_cmd("choco upgrade all -y")
            if rc == 0:
                log(f"{GREEN}✅ Atualizações concluídas (choco).{NC}")
            else:
                log(f"{RED}Erro ao atualizar via choco: {err}{NC}")
        else:
            log(f"{YELLOW}Chocolatey não encontrado. Atualizações automáticas não disponíveis.{NC}")
    pause()

def limpeza():
    log(f"{YELLOW}[2/12] Limpando pacotes e cache...{NC}")
    etapas = 4
    etapa = 0
    if is_linux():
        run_cmd("sudo apt autoremove -y | tee -a " + str(LOG_FILE))
        etapa += 1; print_progress_step(etapa, etapas)
        run_cmd("sudo apt autoclean -y | tee -a " + str(LOG_FILE))
        etapa += 1; print_progress_step(etapa, etapas)
        run_cmd("sudo journalctl --vacuum-time=5d")
        etapa += 1; print_progress_step(etapa, etapas)
        limpar_lixeira = input("Deseja esvaziar a lixeira? (s/n) ")
        if limpar_lixeira.lower().startswith("s"):
            run_cmd("rm -rf ~/.local/share/Trash/*")
            log("Lixeira esvaziada.")
        else:
            log("Lixeira não foi esvaziada.")
        etapa += 1; print_progress_step(etapa, etapas)
    elif is_windows():
        # limpa temp
        temp_dir = tempfile.gettempdir()
        etapa += 1; print_progress_step(etapa, etapas)
        for item in os.listdir(temp_dir):
            path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
            except Exception:
                pass
        etapa += 1; print_progress_step(etapa, etapas)
        # limpar Windows Update cache? apenas nota
        log("Arquivos temporários limpos.")
        etapa += 1; print_progress_step(etapa, etapas)
        # lixeira no Windows - esvaziar via powershell
        limpar_lixeira = input("Deseja esvaziar a lixeira? (s/n) ")
        if limpar_lixeira.lower().startswith("s"):
            if is_windows():
                run_cmd('powershell -Command "Clear-RecycleBin -Force"')
                log("Lixeira esvaziada.")
            else:
                pass
        etapa += 1; print_progress_step(etapa, etapas)

    log("Limpeza concluída!")
    pause()

def print_progress_step(progress, total):
    percent = int(progress * 100 / total)
    filled = int(percent / 2)
    empty = 50 - filled
    bar = "#" * filled + " " * empty
    print(f"\r[ {bar} ] {percent}%")
    # pequena pausa visual
    time.sleep(0.05)

def firewall():
    log(f"{YELLOW}[3/12] Verificando status do firewall (UFW/netsh)...{NC}")
    if is_linux():
        if not shutil.which("ufw"):
            log(f"{RED}UFW não encontrado. Instalando...{NC}")
            run_cmd("sudo apt update -y")
            run_cmd("sudo apt install ufw -y")
            run_cmd("sudo ufw enable")
            log(f"{GREEN}✅ UFW instalado e ativado.{NC}")
        out, err, rc = run_cmd("sudo ufw status verbose")
        log(out if out else err)
        portas = {"22":"ssh","25":"exim4","631":"cups"}
        for porta, svc in portas.items():
            out, err, rc = run_cmd(f"sudo ufw status | grep -E '^{porta} .*ALLOW' || true")
            if out:
                fechar = input(f"[!] Porta {porta} ({svc}) aberta. Deseja fechá-la? (s/n) ")
                if fechar.lower().startswith("s"):
                    # parar e desabilitar serviço se existir
                    run_cmd(f"sudo systemctl stop {svc} || true")
                    run_cmd(f"sudo systemctl disable {svc} || true")
                    run_cmd(f"sudo ufw deny {porta}")
                    log(f"[{porta}] 🔒 Porta fechada e serviço {svc} desativado.")
                else:
                    log(f"[{porta}] 🚪 Mantida aberta.")
            else:
                log(f"[{porta}] Porta não detectada como aberta.")
    elif is_windows():
        out, err, rc = run_cmd("netsh advfirewall show allprofiles")
        log(out if out else err)
        log("No Windows, recomenda-se revisar as regras via Windows Defender Firewall GUI ou PowerShell.")
    pause()

def clamav_scan():
    log(f"{YELLOW}[4/12] Verificando presença do ClamAV...{NC}")
    if is_linux():
        if not shutil.which("clamscan"):
            log(f"{RED}ClamAV não encontrado. Instalando...{NC}")
            run_cmd("sudo apt install clamav clamav-daemon -y")
            run_cmd("sudo freshclam")
        choice = input("Deseja executar scan completo em /home? (s/n) ")
        if choice.lower().startswith("s"):
            log("Executando varredura (pode demorar)...")
            # executa em foreground para simplicidade
            os.system("sudo clamscan -r /home --exclude-dir=/home/*/metasploit-framework --bell -i | tee -a " + str(LOG_FILE))
        else:
            log("Scan pulado.")
    elif is_windows():
        # tenta atualizar definitions do Windows Defender
        defender = r'"%ProgramFiles%\\Windows Defender\\MpCmdRun.exe"'
        out, err, rc = run_cmd(r'%ProgramFiles%\Windows Defender\MpCmdRun.exe -SignatureUpdate')
        if rc == 0:
            log("Definições do Windows Defender atualizadas.")
        else:
            log("Não foi possível atualizar o Defender automaticamente (verifique permissões).")
    pause()

def pacotes_orfaos():
    log(f"{YELLOW}[5/12] Verificando pacotes órfãos...{NC}")
    if is_linux():
        if not shutil.which("deborphan"):
            log("deborphan não encontrado. Instalando...")
            run_cmd("sudo apt install deborphan -y")
        out, err, rc = run_cmd("deborphan || true")
        if out.strip():
            log("Pacotes órfãos encontrados:")
            print(out)
            choice = input("Deseja removê-los? (s/n) ")
            if choice.lower().startswith("s"):
                run_cmd("sudo apt purge -y " + out.replace("\n"," "))
                log("Orfãos removidos.")
        else:
            log("Nenhum pacote órfão encontrado.")
    elif is_windows():
        log("Operação de pacotes órfãos não aplicável no Windows.")
    pause()

def backup_check():
    log(f"{YELLOW}[6/12] Backup...{NC}")
    print("Escolha tipo de backup: 1) Leve 2) Completo 3) Sem backup")
    opt = input("Opção: ").strip()
    if is_linux():
        if opt == "1":
            dest = str(Path.home() / "backup_leve")
            Path(dest).mkdir(parents=True, exist_ok=True)
            run_cmd(f"rsync -a --exclude='*/.cache' {str(Path.home() / 'Documents')} {dest} || true")
            run_cmd(f"rsync -a --exclude='*/.cache' {str(Path.home() / '.config')} {dest} || true")
            run_cmd(f"rsync -a /etc {dest} || true")
            log(f"Backup leve salvo em: {dest}")
        elif opt == "2":
            dest = str(Path.home() / "backup_completo")
            Path(dest).mkdir(parents=True, exist_ok=True)
            run_cmd(f"sudo rsync -a --exclude='*/.cache' /home {dest} || true")
            run_cmd(f"sudo rsync -a /etc {dest} || true")
            log(f"Backup completo salvo em: {dest}")
        else:
            log("Backup ignorado.")
    elif is_windows():
        dest = input("Caminho destino do backup (ex: D:\\Backups\\syscheck): ").strip()
        if not dest:
            log("Backup ignorado.")
        else:
            Path(dest).mkdir(parents=True, exist_ok=True)
            if opt == "1":
                srcs = [str(Path.home() / "Documents"), str(Path.home() / "AppData\\Roaming")]
                for s in srcs:
                    try:
                        shutil.copytree(s, os.path.join(dest, Path(s).name))
                    except Exception:
                        pass
                log(f"Backup leve (Windows) salvo em: {dest}")
            elif opt == "2":
                try:
                    shutil.copytree(str(Path.home()), os.path.join(dest, "home_backup"))
                except Exception as e:
                    log(f"Erro ao copiar: {e}")
                log(f"Backup completo (Windows) salvo em: {dest}")
    pause()

def usuarios_sudo():
    log(f"{YELLOW}[7/12] Verificando usuários com privilégios sudo/administradores...{NC}")
    if is_linux():
        out, err, rc = run_cmd("getent group sudo | awk -F: '{print $4}'")
        print(out)
    elif is_windows():
        out, err, rc = run_cmd("net localgroup Administradores")
        print(out)
    pause()

def servicos_ativos():
    log(f"{YELLOW}[8/12] Listando serviços ativos...{NC}")
    black_list = ["avahi-daemon", "exim4", "cups", "cups-browsed", "ModemManager"]
    if is_linux():
        for svc in black_list:
            out, err, rc = run_cmd(f"systemctl is-active {svc} || true")
            if out.strip() == "active":
                choice = input(f"Serviço {svc} ativo. Deseja desativar? (s/n) ")
                if choice.lower().startswith("s"):
                    run_cmd(f"sudo systemctl disable --now {svc}")
                    log(f"{svc} desativado.")
        out, err, rc = run_cmd("systemctl list-units --type=service --state=running")
        print(out)
    elif is_windows():
        out, err, rc = run_cmd("sc query state= all | findstr /I RUNNING")
        print(out)
    pause()

def espaco_disco():
    log(f"{YELLOW}[9/12] Verificando espaço em disco...{NC}")
    if is_linux():
        out, err, rc = run_cmd("df -h")
        print(out)
    elif is_windows():
        out, err, rc = run_cmd("wmic logicaldisk get size,freespace,caption")
        print(out)
    pause()

def conexoes_rede():
    log(f"{YELLOW}[10/12] Listando conexões de rede ativas...{NC}")
    if is_linux():
        out, err, rc = run_cmd("ss -tulnp")
        print(out)
    elif is_windows():
        out, err, rc = run_cmd("netstat -ano")
        print(out)
    pause()

def integridade_sistema():
    log(f"{YELLOW}[11/12] Checando integridade de pacotes/sistema...{NC}")
    if is_linux():
        if not shutil.which("debsums"):
            log("debsums não encontrado. Instalando...")
            run_cmd("sudo apt install debsums -y")
        out, err, rc = run_cmd("sudo debsums -s || true")
        if out.strip():
            log("Verificações de integridade encontraram problemas (listados abaixo):")
            print(out)
        else:
            log(f"{GREEN}✅ Verificações concluídas (sem erros relatados).{NC}")
    elif is_windows():
        log("Executando 'sfc /scannow' (pode pedir privilégios de administrador).")
        out, err, rc = run_cmd("sfc /scannow")
        print(out if out else err)
    pause()

def executar_tudo():
    log(f"{YELLOW}[12/12] Executar todos os módulos (pergunta s/n para cada)...{NC}")
    funcs = [
        ("Atualizações", atualizacoes),
        ("Limpeza", limpeza),
        ("Firewall", firewall),
        ("Scan ClamAV", clamav_scan),
        ("Pacotes órfãos", pacotes_orfaos),
        ("Backup", backup_check),
        ("Usuários sudo/admin", usuarios_sudo),
        ("Serviços ativos", servicos_ativos),
        ("Espaço em disco", espaco_disco),
        ("Conexões de rede", conexoes_rede),
        ("Integridade do sistema", integridade_sistema),
    ]
    total = len(funcs)
    count = 0
    for name, fn in funcs:
        ans = input(f"Deseja executar '{name}'? (s/n) ")
        if ans.lower().startswith("s"):
            fn()
        else:
            log(f"{name} pulado.")
        count += 1
        print_progress_global(count, total)
    log(f"{GREEN}✅ Todos os módulos processados (ou pulados conforme escolha).{NC}")
    pause()

def print_progress_global(progress, total):
    percent = int(progress * 100 / total)
    filled = int(percent / 2)
    empty = 50 - filled
    bar = "#" * filled + " " * empty
    print(f"\rProgresso total: [ {bar} ] {percent}%")
    time.sleep(0.05)

def sair():
    log(f"{GREEN}✅ Verificações concluídas. Relatório salvo em: {LOG_FILE}{NC}")
    exit(0)

# ====== MENU PRINCIPAL (com as entradas extras pedidas) ======
def menu():
    while True:
        os.system("cls" if is_windows() else "clear")
        print(f"{GREEN}=== SysCheck-Up v2.1 ==={NC}")
        print("1) Atualizações do sistema")
        print("2) Limpeza de pacotes e cache")
        print("3) Firewall (UFW / Firewall do sistema)")
        print("4) Scan de vírus (ClamAV / Defender)")
        print("5) Pacotes órfãos")
        print("6) Diretórios de backup")
        print("7) Usuários com privilégios sudo / administradores")
        print("8) Serviços ativos")
        print("9) Espaço em disco")
        print("10) Conexões de rede")
        print("11) Integridade de pacotes do sistema")
        print("12) Executar tudo (com perguntas s/n)")
        print("13) Sair")
        opt = input("Escolha uma opção: ").strip()
        mapping = {
            "1": atualizacoes,
            "2": limpeza,
            "3": firewall,
            "4": clamav_scan,
            "5": pacotes_orfaos,
            "6": backup_check,
            "7": usuarios_sudo,
            "8": servicos_ativos,
            "9": espaco_disco,
            "10": conexoes_rede,
            "11": integridade_sistema,
            "12": executar_tudo,
            "13": sair,
        }
        fn = mapping.get(opt)
        if fn:
            fn()
        else:
            print(f"{RED}Opção inválida{NC}")
            pause()

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nSaindo...")


