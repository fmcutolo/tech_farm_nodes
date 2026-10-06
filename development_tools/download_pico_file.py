import sys
import ast
import serial


BLOCK_SIZE = 256


def read_until(ser, marker):
    """Read serial data until marker is encountered."""
    data = b""

    while marker not in data:
        chunk = ser.read(1)

        if not chunk:
            raise TimeoutError(
                "Timed out waiting for: {!r}".format(marker)
            )

        data += chunk

    return data


def enter_raw_repl(ser):
    # Interrupt anything currently running.
    ser.write(b"\x03")
    ser.write(b"\x03")

    # Enter raw REPL.
    ser.write(b"\x01")

    read_until(ser, b"raw REPL; CTRL-B to exit\r\n>")


def raw_exec(ser, command):
    """
    Execute a command in raw REPL and return stdout.
    """

    ser.write(command.encode("utf-8"))
    ser.write(b"\x04")

    # MicroPython acknowledges the command with OK.
    response = read_until(ser, b"\x04>")

    if not response.startswith(b"OK"):
        raise RuntimeError(
            "Unexpected raw REPL response: {!r}".format(response)
        )

    # Remove:
    #   OK
    #   final \x04>
    response = response[2:-2]

    # Raw REPL separates stdout and stderr with \x04.
    parts = response.split(b"\x04", 1)

    stdout = parts[0]

    if len(parts) > 1 and parts[1]:
        raise RuntimeError(
            "Pico error:\n{}".format(
                parts[1].decode("utf-8", errors="replace")
            )
        )

    return stdout


def download_file(port, pico_path, local_path):

    print("Pico file : {}".format(pico_path))
    print("Local file: {}".format(local_path))

    ser = serial.Serial(
        port=port,
        baudrate=115200,
        timeout=5
    )

    try:
        # Clear anything already waiting.
        ser.reset_input_buffer()

        enter_raw_repl(ser)

        # Open Pico file once.
        raw_exec(
            ser,
            "__pico_file = open({!r}, 'rb')".format(pico_path)
        )

        total = 0

        with open(local_path, "wb") as output_file:

            while True:

                result = raw_exec(
                    ser,
                    "print(repr(__pico_file.read({})))".format(
                        BLOCK_SIZE
                    )
                )

                # print() adds CR/LF.
                result = result.strip()

                block = ast.literal_eval(
                    result.decode("ascii")
                )

                if not isinstance(block, bytes):
                    raise RuntimeError(
                        "Expected bytes, received {!r}".format(
                            type(block)
                        )
                    )

                output_file.write(block)

                total += len(block)

                print(
                    "\rDownloaded {} bytes".format(total),
                    end=""
                )

                if len(block) < BLOCK_SIZE:
                    break

        raw_exec(ser, "__pico_file.close()")

        print()
        print("Download complete.")

    finally:
        try:
            # Return to friendly REPL.
            ser.write(b"\x02")
        except Exception:
            pass

        ser.close()


def main():

    if len(sys.argv) != 4:
        print(
            "Usage: download_pico_file.py "
            "COM_PORT PICO_FILE LOCAL_FILE"
        )
        sys.exit(1)

    port = sys.argv[1]
    pico_path = sys.argv[2]
    local_path = sys.argv[3]

    download_file(
        port,
        pico_path,
        local_path
    )


if __name__ == "__main__":
    main()