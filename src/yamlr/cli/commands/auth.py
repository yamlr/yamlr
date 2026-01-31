
"""
Yamlr CLI: Auth Command Handler
------------------------------
Handles 'yamlr auth' subcommands: login, logout, status.
"""

import sys
from yamlr.cli.commands.base import print_custom_header

def handle_auth_command(args, console):
    """
    Executes authentication workflows.
    """
    try:
        from yamlr.pro.auth import auth_device
    except ImportError:
        console.print("[bold red]Error:[/bold red] Authentication features are not available in this build.")
        console.print("Please upgrade to Yamlr Enterprise.")
        return 1

    action = getattr(args, "auth_action", "status") or "status"

    if action == "login":
        console.print("[bold cyan]🔐 Yamlr Enterprise Login[/bold cyan]")
        console.print("Initiating device authentication flow...")
        
        if auth_device.login():
            console.print("\n[bold green]Success![/bold green] You are now authenticated.")
            token = auth_device.get_token()
            # Show a masked snippet of the token
            short_tok = token[:10] + "..." + token[-5:] if token else "N/A"
            console.print(f"[dim]Session Token: {short_tok}[/dim]")
        else:
            console.print("\n[bold red]Login Failed.[/bold red] Please try again.")
            return 1

    elif action == "logout":
        auth_device.logout()
        console.print("[green]Credentials cleared.[/green]")

    elif action in ["status", "whoami"]:
        if auth_device.validate_session():
            console.print("[bold green]✅ Authenticated[/bold green]")
            console.print(f"Token Path: {auth_device.creds_file}")
            
            # Decode token details for fun (Mock)
            token = auth_device.get_token()
            console.print(f"[dim]Token: {token[:15]}...[/dim]")
        else:
            console.print("[yellow]⚠️  Not authenticated[/yellow]")
            console.print("Run [bold white]yamlr auth login[/bold white] to sign in.")
            return 1
            
    return 0
