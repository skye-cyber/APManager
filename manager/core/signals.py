import signal
import sys
import os
from typing import Optional


class SignalHandler:
    def __init__(self):
        self.original_handlers = {}
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Setup signal handlers for the application."""
        signals = {
            signal.SIGINT: self.handle_signal,
            signal.SIGUSR1: self.handle_signal,
            signal.SIGUSR2: self.handle_signal
        }

        for sig, handler in signals.items():
            self.original_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, handler)

    def handle_signal(self, signum, frame):
        """Handle signals received by the application."""
        if signum in (signal.SIGINT, signal.SIGUSR1):
            self.clean_exit()
        elif signum == signal.SIGUSR2:
            self.die()

    def cleanup(self):
        """Perform cleanup operations."""
        pass  # Implement cleanup logic

    def clean_exit(self, message: Optional[str] = None):
        """Handle clean exits."""
        if message:
            print(message)

        if os.getpid() != os.getppid():
            os.kill(os.getppid(), signal.SIGUSR2)

        self.restore_handlers()
        self.cleanup()
        sys.exit(0)

    def die(self, message: Optional[str] = None):
        """Handle fatal errors and exit."""
        if message:
            print(f"\nERROR: {message}\n", file=sys.stderr)

        if os.getpid() != os.getppid():
            pass  # os.kill(os.getppid(), signal.SIGUSR2)

        self.restore_handlers()
        self.cleanup()
        sys.exit(1)

    def restore_handlers(self):
        """Restore original signal handlers."""
        for sig, handler in self.original_handlers.items():
            signal.signal(sig, handler)
