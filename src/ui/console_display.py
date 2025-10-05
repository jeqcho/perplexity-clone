"""Rich-based console display utilities for enhanced UX."""

import random
import time
from typing import List, Dict, Any, Optional, Callable
from contextlib import contextmanager
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box
from rich.text import Text

# Create a global console instance
console = Console()


def format_answer_text(response: str) -> Text:
    """Format the answer response with left-aligned headings.

    Rich's Markdown centers h2 headings by default, which is not desired.
    This function manually formats the response with left alignment.
    """
    from rich.console import Group
    from rich.padding import Padding

    lines = response.split('\n')
    formatted = []

    for line in lines:
        if line.startswith('## '):
            # Heading: bold and left-aligned
            heading_text = line[3:].strip()
            formatted.append(Text(heading_text, style="bold cyan"))
        elif line.startswith('- '):
            # Bullet point: preserve indentation
            formatted.append(Text(line))
        elif line.startswith('['):
            # Citation: dim style
            formatted.append(Text(line, style="dim"))
        elif line.strip():
            # Regular text
            formatted.append(Text(line))
        else:
            # Empty line
            formatted.append(Text(""))

    return Group(*formatted)


class Display:
    """Enhanced display utilities using Rich library."""

    @staticmethod
    def header(query: str):
        """Display the query header."""
        console.print()
        console.print(f"[bold cyan]Query:[/bold cyan] {query}", style="white")
        console.print()

    @staticmethod
    def step(step_num: int, total: int, message: str):
        """Display a step indicator."""
        console.print(f"[bold blue][{step_num}/{total}][/bold blue] {message}")

    @staticmethod
    def success(message: str):
        """Display a success message."""
        console.print(f"[green]→[/green] {message}")

    @staticmethod
    def warning(message: str):
        """Display a warning message."""
        console.print(f"[yellow]⚠[/yellow] {message}")

    @staticmethod
    def error(message: str):
        """Display an error message."""
        console.print(f"[red]❌[/red] {message}", style="bold red")

    @staticmethod
    def random_delay(target: float, jitter: float = 0.2, minimum: float = 0.05, maximum: Optional[float] = None) -> float:
        """Return a randomized delay bounded by jitter and optional limits."""
        if target <= 0:
            return max(minimum, 0.0)

        if jitter <= 0:
            low = high = max(minimum, target)
        else:
            low = max(minimum, target - jitter)
            high = target + jitter

        if maximum is not None:
            high = min(high, maximum)

        if high < low:
            high = low

        return random.uniform(low, high)

    @staticmethod
    def pause(
        target: float,
        jitter: float = 0.2,
        minimum: float = 0.05,
        maximum: Optional[float] = None,
        fast_forward: bool = False
    ):
        """Sleep for a randomized amount of time derived from the target delay."""
        if fast_forward:
            return
        time.sleep(Display.random_delay(target, jitter, minimum, maximum))

    @staticmethod
    def search_results_preview(
        search_results: List[Dict[str, Any]],
        sequential_delay: float = 0.5,
        jitter: float = 0.2,
        is_fast_forward: Optional[Callable[[], bool]] = None
    ):
        """Display ALL search results sequentially, one at a time.

        Shows all sources to keep users engaged and reading while agents work.
        This maximizes engagement during the waiting period.

        Args:
            search_results: List of search results
            sequential_delay: Target delay in seconds between showing each source (default: 0.5s)
            jitter: Maximum random variation applied to the sequential delay (default: 0.2s)
            is_fast_forward: Optional callable returning True to skip delays dynamically
        """
        if not search_results:
            return

        console.print()
        console.print("[dim]📚 Sources found:[/dim]")

        # Show ALL results one at a time for maximum engagement
        for i, result in enumerate(search_results, 1):
            fast_forward = is_fast_forward() if is_fast_forward else False
            Display.pause(
                sequential_delay,
                jitter=jitter,
                minimum=0.15,
                fast_forward=fast_forward
            )
            title = result.get('title', 'No title')
            # Truncate long titles
            if len(title) > 70:
                title = title[:67] + "..."
            console.print(f"   [dim cyan]{i}.[/dim cyan] [dim]{title}[/dim]")

        console.print()

    @staticmethod
    def progress_message(
        message: str,
        delay: float = 0.4,
        jitter: float = 0.15,
        is_fast_forward: Optional[Callable[[], bool]] = None
    ):
        """Display a progress message with a delay.

        Args:
            message: The message to display
            delay: Target delay before showing the message (default: 0.4s)
            jitter: Maximum random variation applied to the delay (default: 0.15s)
            is_fast_forward: Optional callable returning True to skip the delay dynamically
        """
        fast_forward = is_fast_forward() if is_fast_forward else False
        Display.pause(delay, jitter=jitter, minimum=0.1, fast_forward=fast_forward)
        console.print(f"[dim cyan]→[/dim cyan] [dim]{message}[/dim]")

    @staticmethod
    @contextmanager
    def spinner(message: str):
        """Context manager for showing an animated spinner with elapsed time.

        This provides visual feedback during long operations, making the UI
        feel reactive instead of stuck.

        Usage:
            with Display.spinner("Processing..."):
                # Do work here
                pass
        """
        start_time = time.time()

        # Create a live display with spinner
        with Live(
            Spinner("dots", text=f"[cyan]{message}[/cyan]"),
            console=console,
            refresh_per_second=10
        ) as live:
            # Track elapsed time in background
            def update_spinner():
                while True:
                    elapsed = time.time() - start_time
                    live.update(
                        Spinner(
                            "dots",
                            text=f"[cyan]{message}[/cyan] [dim]({elapsed:.1f}s)[/dim]"
                        )
                    )
                    time.sleep(0.1)
                    if not live.is_started:
                        break

            # Just yield - the Live context handles the rest
            try:
                yield
            finally:
                # Calculate final elapsed time
                elapsed = time.time() - start_time

    @staticmethod
    def answer(response: str, elapsed_time: float = None):
        """Display the final answer in a visually appealing format.

        Args:
            response: The markdown-formatted response
            elapsed_time: Optional time taken to generate response
        """
        console.print()

        # Format answer with left-aligned headings
        formatted_content = format_answer_text(response)

        # Create a panel for the answer
        panel = Panel(
            formatted_content,
            title="[bold green]ANSWER[/bold green]",
            title_align="left",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(panel)

        # Show timing if provided
        if elapsed_time is not None:
            console.print(
                f"\n[dim]⚡ Answered in {elapsed_time:.1f}s[/dim]",
                style="dim"
            )
        console.print()

    @staticmethod
    def timer_summary(elapsed_time: float):
        """Display timing summary."""
        console.print(f"[dim]⚡ Total time: {elapsed_time:.1f}s[/dim]")
