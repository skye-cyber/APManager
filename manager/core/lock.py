import os
import fcntl
import atexit


class LockManager:
    def __init__(self):
        self.LOCK_FILE = "/tmp/create_ap.all.lock"
        self.COUNTER_LOCK_FILE = f"/tmp/ap_manager.{os.getpid()}.lock"
        self.lock_fd = None
        self.counter_lock_fd = None

        # Initialize on creation
        if not self.__init_lock__():
            print("Failed to initialize lock manager")

        # Clean up on exit
        atexit.register(self.cleanup_lock)

    def __init_lock__(self):
        """Initialize the lock file with proper permissions"""
        old_umask = os.umask(0o022)  # Allow group/other read, only owner write

        try:
            # Clean up any existing counter lock for this process
            self.cleanup_counter_lock()

            # Open/create the global lock file
            try:
                # Try to open existing file
                self.lock_fd = os.open(self.LOCK_FILE, os.O_RDWR)
            except FileNotFoundError:
                # Create if doesn't exist
                self.lock_fd = os.open(self.LOCK_FILE, os.O_RDWR | os.O_CREAT, 0o644)
                # Set owner to root if not root
                if os.geteuid() != 0:
                    try:
                        os.chown(self.LOCK_FILE, 0, 0)
                    except PermissionError:
                        pass  # Ignore if we can't chown

            # Create counter lock file for this process
            self.counter_lock_fd = os.open(
                self.COUNTER_LOCK_FILE,
                os.O_RDWR | os.O_CREAT | os.O_TRUNC,
                0o644
            )
            # Initialize counter to 0
            os.write(self.counter_lock_fd, b'0')
            os.lseek(self.counter_lock_fd, 0, os.SEEK_SET)

            return True
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
        finally:
            os.umask(old_umask)

    def cleanup_counter_lock(self):
        """Clean up only the counter lock file for this process"""
        try:
            if os.path.exists(self.COUNTER_LOCK_FILE):
                os.remove(self.COUNTER_LOCK_FILE)
        except OSError:
            pass

    def cleanup_lock(self):
        """Clean up all lock files"""
        self.cleanup_counter_lock()

        # Only clean global lock if we're the last process
        try:
            if self.lock_fd is not None:
                os.close(self.lock_fd)
            # Note: Don't remove global lock file as other processes may be using it
        except OSError:
            pass

    def mutex_lock(self):
        """Recursive mutex lock for all processes"""
        if self.counter_lock_fd is None or self.lock_fd is None:
            print("Lock not initialized")
            return False

        try:
            # Lock the counter file for this process
            fcntl.flock(self.counter_lock_fd, fcntl.LOCK_EX)

            # Read current counter value
            os.lseek(self.counter_lock_fd, 0, os.SEEK_SET)
            data = os.read(self.counter_lock_fd, 10)
            counter = int(data.decode().strip()) if data else 0

            # Lock global mutex if this is the first lock
            if counter == 0:
                fcntl.flock(self.lock_fd, fcntl.LOCK_EX)

            # Increment counter
            counter += 1

            # Write back new counter value
            os.lseek(self.counter_lock_fd, 0, os.SEEK_SET)
            os.write(self.counter_lock_fd, str(counter).encode())
            os.fsync(self.counter_lock_fd)

            # Unlock counter file (we keep global lock if counter > 0)
            fcntl.flock(self.counter_lock_fd, fcntl.LOCK_UN)

            return True
        except Exception as e:
            print(f"Failed to lock mutex: {e}")
            return False

    def mutex_unlock(self):
        """Recursive mutex unlock for all processes"""
        if self.counter_lock_fd is None or self.lock_fd is None:
            print("Lock not initialized")
            return False

        try:
            # Lock the counter file for this process
            fcntl.flock(self.counter_lock_fd, fcntl.LOCK_EX)

            # Read current counter value
            os.lseek(self.counter_lock_fd, 0, os.SEEK_SET)
            data = os.read(self.counter_lock_fd, 10)
            counter = int(data.decode().strip()) if data else 0

            # Decrement counter if positive
            if counter > 0:
                counter -= 1

                # Unlock global mutex if this is the last unlock
                if counter == 0:
                    fcntl.flock(self.lock_fd, fcntl.LOCK_UN)

            # Write back new counter value
            os.lseek(self.counter_lock_fd, 0, os.SEEK_SET)
            os.write(self.counter_lock_fd, str(counter).encode())
            os.fsync(self.counter_lock_fd)

            # Unlock counter file
            fcntl.flock(self.counter_lock_fd, fcntl.LOCK_UN)

            return True
        except Exception as e:
            print(f"Failed to unlock mutex: {e}")
            return False


lock = LockManager()


# Example usage
if __name__ == "__main__":
    lock = LockManager()

    if lock.mutex_lock():
        print("Successfully locked mutex")
        # Do your critical section work here

        if lock.mutex_unlock():
            print("Successfully unlocked mutex")
        else:
            print("Failed to unlock mutex")
    else:
        print("Failed to lock mutex")
