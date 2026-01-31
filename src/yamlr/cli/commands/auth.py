
import os
from pathlib import Path
from yamlr.core.bridge import YamlrBridge, ProStatus

def handle_auth_command(args, console):
    """
    Manages Yamlr Enterprise authentication.
    """
    
    # 1. Login Mode
    if args.login:
        license_key = args.login.strip()
        if not license_key:
            console.print("[red]❌ Error: License key cannot be empty.[/red]")
            return 1
            
        try:
            # Create ~/.Yamlr/license.key
            config_dir = Path.home() / ".Yamlr"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            key_file = config_dir / "license.key"
            key_file.write_text(license_key, encoding="utf-8")
            
            console.print(f"[green]✅ License key saved to {key_file}[/green]")
            console.print("[dim]Use 'Yamlr auth' to verify status.[/dim]")
            return 0
            
        except Exception as e:
            console.print(f"[red]❌ Failed to save license:[/red] {e}")
            return 1

    # 2. Status Mode (Default)
    status, message = YamlrBridge.check_pro_status()
    console.print("\n[bold]Yamlr Enterprise Status[/bold]")
    console.print("--------------------------")
    
    badge, msg, color = YamlrBridge.get_pro_status_display()
    console.print(f"Status: [{color}]{badge}[/{color}]")
    console.print(f"Detail: {msg}")
    
    if status == ProStatus.NOT_INSTALLED:
        console.print("\n[dim]To upgrade:[/dim]")
        console.print("  1. pip install Yamlr-pro")
        console.print("  2. Yamlr auth --login <YOUR_KEY>")
    
    return 0
