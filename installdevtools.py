#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os

import os
import subprocess

import os
import subprocess

def detect_shell():
    shell = os.getenv("SHELL")
    if 'bash' in shell:
        return "bash"
    elif 'zsh' in shell:
        return "zsh"
    else:
        print("Shell não suportado.")
        return None

def configure_fnm(shell):
    fnm_env_command = 'eval "$(fnm env --use-on-cd)"'
    
    if shell == "bash":
        profile_file = "~/.bashrc"
    elif shell == "zsh":
        profile_file = "~/.zshrc"
        
    else:
        print(f"Shell {shell} não é suportado para configuração do fnm.")
        return False

    # Adicionando configuração ao arquivo de perfil
    diretorio_usuario = os.path.expanduser('~')
    fnm_prompt = f"source {diretorio_usuario}/.local/share/fnm/fnm_prompt\n"
    add_path_fnm= f"export PATH=\"{diretorio_usuario}/.local/share/fnm:$PATH\""
    command = f"{diretorio_usuario}/.local/share/fnm/fnm completions --shell {shell} > {diretorio_usuario}/.local/share/fnm/fnm_prompt && echo {diretorio_usuario}/.local/share/fnm/fnm_prompt {diretorio_usuario}/{profile_file}"
    result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)

    try:
        with open(os.path.expanduser(profile_file), 'a') as file:
    
            file.write(f"\n#Adicionando PATH para o fnm\n{add_path_fnm}\n")
            file.write(f"\n# Configuração do fnm\n{fnm_env_command}\n")
            file.write(f"\n# Configuração do autocomplet do fnm\n{fnm_prompt}\n")
        print(f"fnm configurado com sucesso no {profile_file}!")
    except Exception as e:
        print(f"Erro ao configurar o fnm no  {profile_file}: {e}")


def run_command(command, shell=False):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=shell)
        print(f"Comando executado com sucesso: {' '.join(command) if isinstance(command, list) else command}\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {' '.join(command) if isinstance(command, list) else command}\nErro: {e.stderr}")
        return False

def install_dependency(dependency):
    """Instala uma dependência."""
    print(f"Instalando {dependency}...")
    return run_command(["sudo", "apt-get", "install", dependency, "-y"])

def validate_tools(tools, parser):
    tools = {
        "chrome",
        "flareget",
        "vscode",
        "sublime3",
        "fnm",
        "spotify",
        "bash_autocomplete",
        "docker",
        "all"
    }
    for tool in tools:
        if tool not in tools:
            print(f"Erro: '{tool}' não é uma ferramenta suportada.")
            parser.print_help()
            return False
    return True


def update_system():
    print("Atualizando sistema...")
    if not run_command(["sudo", "apt-get", "update"]):
        print("Falha ao atualizar a lista de pacotes.")
        return False
    if not run_command(["sudo", "apt-get", "upgrade", "-y"]):
        print("Falha ao atualizar os pacotes.")
        return False
    return True

def purge_libreoffice():
    print("Removendo LibreOffice...")
    if not run_command(["sudo", "apt-get", "purge", "-y", "libreoffice*"]):
        print("Falha ao remover o LibreOffice. Verifique as permissões.")
        return False
    if not run_command(["sudo", "apt-get", "autoremove", "-y"]):
        print("Falha ao executar autoremove após a remoção do LibreOffice.")
        return False
    return True

def check_dependency_installed(dependency):
    """Verifica se uma dependência está instalada usando `which`."""
    try:
        result = subprocess.run(["which", dependency], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout:
            print(f"{dependency} já está instalado.")
            return True
        else:
            print(f"{dependency} não está instalado.")
            return False
    except subprocess.CalledProcessError:
        # O comando falhou, o que significa que a dependência não foi encontrada
        print(f"{dependency} não está instalado.")
        return False

def install_tool(tool_name):
    tool_install_commands = {
        "chrome": "wget -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && sudo apt install /tmp/google-chrome-stable_current_amd64.deb -y && rm /tmp/google-chrome-stable_current_amd64.deb",
        "flareget": "wget -O /tmp/flareget_5.0-1_amd64.deb https://dl.flareget.com/downloads/files/flareget/debs/amd64/flareget_5.0-1_amd64.deb && sudo apt install /tmp/flareget_5.0-1_amd64.deb -y && rm /tmp/flareget_5.0-1_amd64.deb",
        "vscode": "wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo apt-key add - && sudo add-apt-repository \"deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main\" -y && sudo apt-get update && sudo apt-get install code -y",
        "sublime3": "wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add - && echo \"deb https://download.sublimetext.com/ apt/stable/\" | sudo tee /etc/apt/sources.list.d/sublime-text.list && sudo apt-get update && sudo apt-get install sublime-text -y",
        "fnm": "curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell",
        "spotify": "curl -sS https://download.spotify.com/debian/pubkey_6224F9941A8AA6D1.gpg | sudo gpg --dearmor --yes -o /etc/apt/trusted.gpg.d/spotify.gpg | echo  \"deb http://repository.spotify.com stable non-free\" | sudo tee /etc/apt/sources.list.d/spotify.list && sudo apt-get update && sudo apt-get install spotify-client -y",
        "bash_autocomplete": "sudo apt-get install bash-completion -y && echo \"source /etc/bash_completion\" >> ~/.bashrc",
        "docker": "sudo apt-get update && sudo apt-get install apt-transport-https ca-certificates curl software-properties-common -y && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && sudo add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" -y && sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io -y"


    }
    
    if tool_name in tool_install_commands:
        print(f"Instalando {tool_name}...")
        if not run_command(tool_install_commands[tool_name], shell=True):
            print(f"Falha ao instalar {tool_name}.")
            return False

        if tool_name == "fnm":
            shell = detect_shell()
            if shell and configure_fnm(shell):
                print(f"{tool_name} instalado e configurado com sucesso.")
            else:
                return False
        else:
            print(f"{tool_name} instalado com sucesso.")
        return True
    else:
        print(f"Ferramenta {tool_name} desconhecida.")
        return False
 
    

def check_tool_dependecy(tool):
    dependencies = {
        "chrome": "wget",
        "flareget": "wget",
        "vscode": "wget",
        "sublime3": "wget",
        "fnm": "curl",
        "bash_autocomplete": "",
        "docker": "",
        "spotify": "curl",  # Adicionando `curl` como dependência para o Spotify
    }

    if tool not in dependencies:
        print(f"Ferramenta {tool} desconhecida.")
        return False  # Caso a ferramenta não seja reconhecida

    dependency = dependencies[tool]

    # Caso a ferramenta não tenha dependências diretas, retorna True
    if not dependency:
        print(f"{tool} não tem dependências ou elas já estão satisfeitas.")
        install_tool(tool)
    else :
    # Verifica e instala dependências se necessário
        dependency_installed = check_dependency_installed(dependency)
        if not dependency_installed:
            success = install_dependency(dependency)
            install_tool(tool)
            if not success:
                return False
        else:
            print(f"{dependency} já está instalado.")
            install_tool(tool)

def main():
    parser = argparse.ArgumentParser(description='Configurador de Ambiente de Desenvolvimento para Ubuntu - Otimizado para Ubuntu 23.10')

    # Definindo os argumentos
    parser.add_argument('-i', '--install', nargs='*', choices=['vscode', 'docker','flareget', 'fnm', 'sublime3', 'chrome', 'spotify', 'bash_autocomplete', 'all'])
    parser.add_argument('-p', '--purge', action='store_true', help='Executa a remoção completa do LibreOffice, liberando espaço no sistema.')
    parser.add_argument('-u', '--upgrade', action='store_true', help='Atualiza o sistema e suas aplicações para as últimas versões disponíveis.')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)  # Exibe a mensagem de ajuda
        sys.exit(1)  # Sai do script com um código de erro

    if args.install:
        for tool in args.install:
            if not validate_tools(args.install, parser):
                sys.exit(1)
            if tool == "all":
            # Especifica a ordem de instalação das ferramentas
                for tool in ["fnm", "chrome", "flareget", "sublime3", "vscode", "bash_autocomplete", "docker","spotify"]:
                    check_tool_dependecy(tool)
            else:
                check_tool_dependecy(tool)

    if args.purge and not purge_libreoffice():
        return

    if args.upgrade and not update_system():
        return


if __name__ == "__main__":
    main()
