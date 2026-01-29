
import sys
import argparse
from typing import Dict, List

# Powershell value completer template
# Powershell value completer template
POWERSHELL_TEMPLATE = """
$Script:AkesoCompleter = {
    param($commandName, $wordToComplete, $cursorPosition)
    
    $commands = 'scan', 'heal', 'init', 'explain', 'catalog', 'version', 'auth', 'completion'
    
    # Flags definitions
    $flags = @{
        'scan' = @('--path', '--output', '--ext', '--max-depth', '--diff', '--help', '--version', '--kube-version', '--catalog', '--summary-only')
        'heal' = @('--path', '--dry-run', '--yes', '--yes-all', '--harden', '--ext', '--max-depth', '--help', '--version', '--kube-version', '--catalog')
        'init' = @('--help')
        'explain' = @('--help')
        'catalog' = @('update', 'list', 'status', '--help', '--kube-version')
        'completion' = @('powershell', 'bash', 'zsh', '--help')
        'auth' = @('--login', '--help')
    }

    $text = $wordToComplete.ToString()

    # If previous argument was a command, suggest flags for that command
    # Simple heuristic: find the last known command in the args
    # $fakeArgs = $MyInvocation.Line.Split(' ') | Where-Object { $_ -ne '' }
    
    # If starting a flag
    if ($text.StartsWith('-')) {
        # Check context? simpler: just return all flags for now or generic globals
        return $flags.GetEnumerator() | ForEach-Object { 
             $_.Value | Where-Object { $_ -like "$text*" } | ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', $_) }
        }
    }
    
    # If standard command
    return $commands | Where-Object { $_ -like "$text*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'Command', $_)
    }
}
# Register for both aliases
Register-ArgumentCompleter -Native -CommandName akeso -ScriptBlock $Script:AkesoCompleter
Register-ArgumentCompleter -Native -CommandName kubecuro -ScriptBlock $Script:AkesoCompleter
Write-Host "Akeso/Kubecuro PowerShell completion loaded." -ForegroundColor Green
"""

BASH_TEMPLATE = """
_akeso_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Top level commands
    commands="scan heal init explain catalog version auth completion"
    
    # Flags per command
    case "${prev}" in
        scan)
            opts="--output --ext --max-depth --diff --help --kube-version --catalog --summary-only"
            ;;
        heal)
            opts="--dry-run --yes --yes-all --harden --ext --max-depth --help --kube-version --catalog"
            ;;
        catalog)
            opts="update list status --help --kube-version"
            ;;
        completion)
            opts="powershell bash zsh --help"
            ;;
        init|explain|auth|version)
            opts="--help"
            ;;
        *)
            opts="$commands"
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _akeso_completion akeso
complete -F _akeso_completion kubecuro
"""

def handle_completion_command(args, parser: argparse.ArgumentParser, console):
    """
    Outputs the shell completion script.
    """
    shell = args.shell.lower()
    
    # In a full comprehensive implementation, we would extract these dynamically from 'parser'
    # For now, we use the static templates which cover the Phase 4 features accurately.
    
    if not shell:
         console.print("[bold]Autocompletion Generator[/bold]")
         console.print("Please specify a shell to generate the script for:\n")
         console.print("  [cyan]akeso completion powershell[/cyan]")
         console.print("  [cyan]akeso completion bash[/cyan]")
         console.print("  [cyan]akeso completion zsh[/cyan]")
         return 1

    shell = shell.lower()

    if shell == "powershell":
        print(POWERSHELL_TEMPLATE.strip())
        # Print usage to stderr so it doesn't corrupt the pipe
        print("\n# Usage: akeso completion powershell | Out-String | Invoke-Expression", file=sys.stderr)
    elif shell == "bash":
        print(BASH_TEMPLATE.strip())
        print("\n# Usage: source <(akeso completion bash)", file=sys.stderr)
        print("# Add to ~/.bashrc for persistence.", file=sys.stderr)
    elif shell == "zsh":
        # Zsh can reuse bash completion if bashcompinit is enabled
        print(BASH_TEMPLATE.strip())
        print("\n# Usage (Mac/Zsh):", file=sys.stderr)
        print("# 1. Add this to ~/.zshrc: autoload -U +X bashcompinit && bashcompinit", file=sys.stderr)
        print("# 2. Then run: source <(akeso completion zsh)", file=sys.stderr)
    else:
        console.print(f"[red]Unsupported shell: {shell}[/red]")
        return 1
        
    return 0
