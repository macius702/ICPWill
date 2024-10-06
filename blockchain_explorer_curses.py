import curses
import subprocess
import json

# Function to get block information
def get_block_info(block_height):
    try:
        # Get block hash
        block_hash = subprocess.check_output(
            ['bitcoin-cli', '-conf=/bitcoin_replica_daemon/bitcoin-27.0/bitcoin.conf', 'getblockhash', block_height]
        ).decode('utf-8').strip()

        # Get block details
        block_details = subprocess.check_output(
            ['bitcoin-cli', '-conf=/bitcoin_replica_daemon/bitcoin-27.0/bitcoin.conf', 'getblock', block_hash, 'true']
        ).decode('utf-8')

        return json.loads(block_details)
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

# Function to get transaction information
def get_transaction_info(txid):
    try:
        # Get transaction details
        transaction_details = subprocess.check_output(
            ['bitcoin-cli', '-conf=/bitcoin_replica_daemon/bitcoin-27.0/bitcoin.conf', 'getrawtransaction', txid, 'true']
        ).decode('utf-8')

        return json.dumps(json.loads(transaction_details), indent=4)
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

# Main application using curses
def main(stdscr):
    # Clear the screen
    stdscr.clear()
    curses.curs_set(0)  # Hide cursor

    current_mode = "block"  # Mode can be 'block' or 'transaction'
    input_prompt = "Enter Block Height: " if current_mode == "block" else "Enter Transaction ID: "
    user_input = ""
    output_text = ""
    transaction_ids = []
    selected_index = 0

    while True:
        stdscr.clear()

        # Display instructions
        stdscr.addstr(0, 0, "Bitcoin Blockchain Explorer - Curses")
        stdscr.addstr(1, 0, "Press 'B' to switch to Block mode, 'T' for Transaction mode, 'Q' to quit")
        stdscr.addstr(2, 0, "Current mode: " + ("Block" if current_mode == "block" else "Transaction"))

        # Display input prompt
        stdscr.addstr(4, 0, input_prompt + user_input)

        # Handle output display based on mode
        if current_mode == "block" and transaction_ids:
            # Display transaction list with selectable highlighting
            max_y, _ = stdscr.getmaxyx()
            for idx, txid in enumerate(transaction_ids):
                if 6 + idx < max_y - 1:  # Check if within display area
                    if idx == selected_index:
                        stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(6 + idx, 0, txid)
                    if idx == selected_index:
                        stdscr.attroff(curses.A_REVERSE)
        else:
            # Display output (paged view)
            lines = output_text.splitlines()
            max_y, max_x = stdscr.getmaxyx()
            for i, line in enumerate(lines[:max_y - 6]):
                stdscr.addstr(6 + i, 0, line[:max_x - 1])

        # Get user input
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == ord('b'):
            current_mode = "block"
            input_prompt = "Enter Block Height: "
            user_input = ""
            output_text = ""
            transaction_ids = []
            selected_index = 0
        elif key == ord('t'):
            current_mode = "transaction"
            input_prompt = "Enter Transaction ID: "
            user_input = ""
            output_text = ""
            transaction_ids = []
            selected_index = 0
        elif key in (curses.KEY_BACKSPACE, 127):  # Handle backspace
            user_input = user_input[:-1]
        elif key == curses.KEY_ENTER or key in [10, 13]:  # Handle Enter key
            if current_mode == "block" and user_input.isdigit():
                block_info = get_block_info(user_input)
                if isinstance(block_info, dict) and 'tx' in block_info:
                    transaction_ids = block_info['tx']
                    output_text = f"Block {user_input} Transactions:\n" + "\n".join(transaction_ids)
                else:
                    output_text = block_info  # Display error or block details
            elif current_mode == "transaction" and user_input:
                output_text = get_transaction_info(user_input)
            elif current_mode == "block" and transaction_ids:
                # Entering on a selected transaction in the list
                txid = transaction_ids[selected_index]
                output_text = get_transaction_info(txid)
                current_mode = "transaction"
            user_input = ""
            selected_index = 0
        elif key < 256:  # Handle other characters
            user_input += chr(key)
        elif current_mode == "block" and transaction_ids:
            if key == curses.KEY_UP and selected_index > 0:
                selected_index -= 1
            elif key == curses.KEY_DOWN and selected_index < len(transaction_ids) - 1:
                selected_index += 1

        # Refresh the screen
        stdscr.refresh()

# Initialize the curses application
curses.wrapper(main)
