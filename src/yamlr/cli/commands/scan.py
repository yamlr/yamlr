"""
SCAN COMMAND
------------
Audits manifests for logical issues (read-only).
"""
import os
import sys
import json
import time
from yamlr.core.engine import YamlrEngine
from yamlr.cli.commands.base import get_console
from yamlr.ui.reporters import JSONReporter, SARIFReporter

def handle_scan_command(args, engine, formatter):
    """
    Handles 'scan' subcommand execution.
    """
    extensions = [e.strip() for e in args.ext.split(",")]
    
    # Scan implies dry-run heal
    is_dry = True 

    start_time = time.time()
    
    start_time = time.time()
    
    # Collect results from all targets
    job_results = []
    
    # Handle implicit "." if list is empty (should be caught by validation, but safe usage)
    targets = args.path if args.path else ["."]
    if args.path == [] and not sys.stdin.isatty():
         # If no args but piped input, treat as stdin
         targets = ["-"]

    for target in targets:
        if target == "-":
            # STDIN Mode
            content = sys.stdin.read()
            job_results.append(engine.audit_stream(content, source_name="<stdin>"))
        elif os.path.isfile(target):
            result = engine.audit_and_heal_file(target, dry_run=is_dry)
            job_results.append(result)
        elif os.path.isdir(target):
            batch_results = engine.batch_heal(
                root_path=target, 
                extensions=extensions, 
                max_depth=args.max_depth,
                dry_run=is_dry
            )
            job_results.extend(batch_results)
        else:
            console = get_console()
            console.print(f"[red]❌ File not found: {target}[/red]")
            # Create a dummy result to force failure exit code
            job_results.append({"success": False, "file_path": target, "status": "FILE_NOT_FOUND", "findings": [{"message": "File not found"}]})

    # Handle Output Formats
    output_fmt = getattr(args, 'output', 'text')
    
    if output_fmt in ["json", "sarif"]:
        # Prepare data for reporters
        duration = time.time() - start_time
        data = {
            "processed_files": job_results,
            "healed_count": sum(1 for r in job_results if r.get("written") or r.get("healed_content")),
            "success_count": sum(1 for r in job_results if r.get("success"))
        }

        if output_fmt == "json":
            print(JSONReporter().generate(data, duration))
        elif output_fmt == "sarif":
             print(SARIFReporter().generate(data))
             
    else:
        # Standard Text/Table Output
        
        # Heuristic: If we only have 1 result, show detailed view
        if len(job_results) == 1:
             result = job_results[0]
             formatter.display_report(result, verbose=getattr(args, 'verbose', False))
             
             # Support --diff
             if getattr(args, 'diff', False):
                 from yamlr.ui.diff import DiffEngine
                 if result.get("healed_content") and result.get("raw_content") != result.get("healed_content"):
                     DiffEngine.render_diff(
                        result.get("raw_content", ""), 
                        result.get("healed_content", ""), 
                        result.get("file_path", "Unknown")
                     )

        else:
             summary_mode = getattr(args, 'summary_only', False)
             formatter.print_final_table(job_results, summary_only=summary_mode)
             
             # Support --diff for Batch Scan
             if getattr(args, 'diff', False):
                 from yamlr.ui.diff import DiffEngine
                 console = get_console()
                 changed_jobs = [j for j in job_results if j.get("healed_content") and j.get("raw_content") != j.get("healed_content")]
                 
                 if changed_jobs:
                    console.print(f"\n[bold yellow]Found {len(changed_jobs)} files with proposed repairs:[/bold yellow]")
                    for job in changed_jobs:
                        DiffEngine.render_diff(
                            job.get("raw_content", ""), 
                            job.get("healed_content", ""), 
                            job.get("file_path", "Unknown")
                        )
                 else:
                    if not summary_mode: # Don't double print if table shows it
                        console.print("\n[green]No changes proposed (files are healthy).[/green]")
            
    # Calculate Exit Code
    files_with_issues = [j for j in job_results if not j.get("success") or (j.get("healed_content") and j.get("raw_content") != j.get("healed_content"))]
    exit_code = 1 if files_with_issues else 0

    if exit_code != 0 and output_fmt == "text":
        console = get_console()
        
        # Check if stdin was used
        is_stdin = (args.path == []) and (not sys.stdin.isatty())
        if not is_stdin and "-" not in args.path:
            # Construct a helpful heal command string
            # If explicit paths provided, try to reuse them if short
            if args.path and len(args.path) <= 3:
                # Join simple paths
                path_str = " ".join(args.path)
                heal_cmd = f"Yamlr heal {path_str}"
            else:
                heal_cmd = "Yamlr heal <paths>"

            console.print(f"\n[bold]💡 Tip:[/bold] Run [cyan]{heal_cmd}[/cyan] to fix {len(files_with_issues)} detected issues.\n")
        else:
            console.print(f"\n[bold yellow]⚠️  Found {len(files_with_issues)} issues in input stream.[/bold yellow]\n")

    return exit_code
