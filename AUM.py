import streamlit as st

import hashlib

import time

import json



# Blockchain Classes (same as before)

class Block:

    def __init__(self, index, previous_hash, timestamp, transactions, shard_id=0, nonce=0):

        self.index = index

        self.previous_hash = previous_hash

        self.timestamp = timestamp

        self.transactions = transactions

        self.shard_id = shard_id

        self.nonce = nonce

        self.hash = self.calculate_hash()



    def calculate_hash(self):

        block_string = json.dumps({

            "index": self.index,

            "previous_hash": self.previous_hash,

            "timestamp": self.timestamp,

            "transactions": self.transactions,

            "shard_id": self.shard_id,

            "nonce": self.nonce

        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()



class AUMBlockchain:

    def __init__(self):

        self.chain = [self.create_genesis_block()]

        self.pending_transactions = []

        self.difficulty = 4

        self.shard_count = 4

        self.total_supply = 21000000

        self.current_supply = 50



    def create_genesis_block(self):

        return Block(0, "0", time.time(), ["Genesis Transaction: AUM Blockchain Launched"], 0)



    def get_latest_block(self):

        return self.chain[-1]



    def add_transaction(self, sender, recipient, amount):

        self.pending_transactions.append({

            "sender": sender,

            "recipient": recipient,

            "amount": float(amount)

        })



    def mine_block(self):

        if not self.pending_transactions:

            return "No transactions to mine."

        

        sharded_tx = [[] for _ in range(self.shard_count)]

        for i, tx in enumerate(self.pending_transactions):

            shard = i % self.shard_count

            sharded_tx[shard].append(tx)



        mined_count = 0

        start_time = time.time()

        for shard_id, tx_list in enumerate(sharded_tx):

            if tx_list:

                previous_hash = self.get_latest_block().hash

                new_block = Block(len(self.chain), previous_hash, time.time(), tx_list, shard_id)

                

                reward = 50 / (2 ** (len(self.chain) // 210000))

                if self.current_supply + reward > self.total_supply:

                    continue

                self.current_supply += reward

                new_block.transactions.insert(0, {"sender": "Network", "recipient": "Miner", "amount": reward})



                while new_block.hash[:self.difficulty] != '0' * self.difficulty:

                    new_block.nonce += 1

                    new_block.hash = new_block.calculate_hash()



                self.chain.append(new_block)

                mined_count += 1



        self.pending_transactions = []

        self.difficulty = min(max(self.difficulty + (len(self.chain) % 5 == 0), 2), 6)

        

        elapsed = time.time() - start_time

        return f"Mined {mined_count} blocks in {elapsed:.2f}s."



    def is_chain_valid(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]

            previous = self.chain[i-1]

            if current.hash != current.calculate_hash() or current.previous_hash != previous.hash:

                return False

        return True



    def get_chain_display(self):

        display = ""

        for block in self.chain:

            display += f"**Block {block.index} (Shard {block.shard_id})**\n"

            display += f"Hash: {block.hash}\n"

            display += f"Previous Hash: {block.previous_hash}\n"

            display += f"Transactions: {json.dumps(block.transactions, indent=2)}\n"

            display += f"Timestamp: {time.ctime(block.timestamp)}\n\n"

        return display



# Streamlit GUI

st.title("AUM Blockchain Demo (@0xSturdy)")



if 'blockchain' not in st.session_state:

    st.session_state.blockchain = AUMBlockchain()



bc = st.session_state.blockchain



# Transaction Form

with st.form(key="tx_form"):

    sender = st.text_input("Sender", value="Investor")

    recipient = st.text_input("Recipient", value="Akshay")

    amount = st.number_input("Amount", value=100.0)

    submit_tx = st.form_submit_button("Add Transaction")

    if submit_tx:

        bc.add_transaction(sender, recipient, amount)

        st.success("Transaction added!")



# Buttons

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("Mine Blocks"):

        result = bc.mine_block()

        st.info(result)

with col2:

    if st.button("Validate Chain"):

        valid = bc.is_chain_valid()

        st.success(f"Chain is {'valid' if valid else 'invalid'}!")

with col3:

    if st.button("Reset Chain"):

        st.session_state.blockchain = AUMBlockchain()

        st.success("Chain reset!")



# Display Chain

st.subheader("Blockchain Ledger")

st.markdown(bc.get_chain_display())