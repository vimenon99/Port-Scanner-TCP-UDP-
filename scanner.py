
import socket
from datetime import datetime
import threading
import argparse


# Function to scan a single port
def scan_port(target_ip, port, timeout):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout
        sock.settimeout(timeout)

        # Try to connect to the target IP and port
        result = sock.connect_ex((target_ip, port))

        # If the result is 0, the port is open
        if result == 0:
            try:
                # Get the service name for the port
                service = socket.getservbyport(port, 'tcp')
            except:
                # If the service name cannot be found, set it to 'Unknown'
                service = 'Unknown'

            # Try to grab the banner
            sock.send(b'HEAD / HTTP/1.1\r\n\r\n')
            banner = sock.recv(1024).decode().strip()

            # Print the result
            print(f"Port {port}: Open ({service}) - {banner}")
            return (port, service, banner)

        # Close the socket
        sock.close()

    except KeyboardInterrupt:
        # Handle keyboard interrupt
        print("\nExiting program.")
        exit()

    except socket.gaierror:
        # Handle hostname resolution error
        print("\nHostname could not be resolved.")
        exit()

    except socket.error:
        # Handle general socket error
        print("\nCouldn't connect to server.")
        exit()

    return None


# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Advanced Port Scanner')
    parser.add_argument('target', help='Target IP address or hostname')
    parser.add_argument('start_port', type=int, help='Starting port number')
    parser.add_argument('end_port', type=int, help='Ending port number')
    parser.add_argument('-t', '--timeout', type=float, default=1.0,
                        help='Timeout for each port scan (default: 1.0 seconds)')
    parser.add_argument('-o', '--output', help='Output file to save the scan results')
    args = parser.parse_args()

    target = args.target
    start_port = args.start_port
    end_port = args.end_port
    timeout = args.timeout
    output_file = args.output

    # Resolve the target to an IP address
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print("Hostname could not be resolved.")
        exit()

    # Display the target information
    print(f"\nScanning target: {target_ip}")
    print(f"Scanning ports from {start_port} to {end_port}")
    print("-" * 50)

    # Get the start time
    start_time = datetime.now()

    # Create a list to hold threads
    threads = []

    # List to store results
    results = []

    # Function to run the scan and store results
    def threaded_scan(target_ip, port, timeout):
        result = scan_port(target_ip, port, timeout)
        if result:
            results.append(result)

    # Scan ports in the specified range using threads
    for port in range(start_port, end_port + 1):
        # Create a thread for each port scan
        thread = threading.Thread(target=threaded_scan, args=(target_ip, port, timeout))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Get the end time
    end_time = datetime.now()

    # Calculate and display the total scan time
    total_time = end_time - start_time
    print(f"\nScanning completed in: {total_time}")

    # Save results to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            for result in results:
                f.write(f"Port {result[0]}: Open ({result[1]}) - {result[2]}\n")
        print(f"\nResults saved to {output_file}")


# Entry point of the script
if __name__ == "__main__":
    main()
