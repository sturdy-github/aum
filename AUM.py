import streamlit as st
import hashlib
import time
import json
import pandas as pd

# --- Page Configuration & Glassmorphism CSS ---
st.set_page_config(page_title="AUM Blockchain Explorer", layout="wide", page_icon="💠")

st.markdown("""
<style>
    /* Dark Animated Background */
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.1), transparent 30%),
            radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.1), transparent 30%);
        color: #e2e8f0;
    }
    
    /* Headers and Text */
    h1, h2, h3 { color: #38bdf8 !important; }
    
    /* Glassmorphism Metrics Cards */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stMetricValue"] { color: #10b981 !important; }
    
    /* Glassmorphism Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(139, 92, 246, 0.2)) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        color: white !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    div.stButton > button:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5) !important;
        transform: translateY(-2px);
    }

    /* Form & Inputs */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px;
        padding: 20px;
    }
    
    /* Tabs Styling */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #94a3b8 !important;
        font-size: 1.1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Blockchain Classes ---
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
        return Block(0, "0", time.time(), [{"sender": "System", "recipient": "Genesis", "amount": 50}], 0)

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

# --- Initialize Blockchain in Session State ---
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = AUMBlockchain()

bc = st.session_state.blockchain

# --- Main App Title ---
st.title("💠 AUM Network")
st.caption("Live Sharded Proof-of-Work Demo | Developed by @0xSturdy")

# --- Tabs Navigation ---
tab1, tab2 = st.tabs(["🏦 Wallet & Network Controls", "🔍 AUMscan (Explorer)"])

# ==========================================
# TAB 1: WALLET & NETWORK CONTROLS
# ==========================================
with tab1:
    st.subheader("📊 Tokenomics Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Max Supply", f"{bc.total_supply:,.0f} AUM")
    with col2:
        st.metric("Mined / Circulating", f"{bc.current_supply:,.2f} AUM")
    with col3:
        available = bc.total_supply - bc.current_supply
        st.metric("Available to Mine", f"{available:,.2f} AUM")

    st.divider()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("💸 Send Transaction")
        with st.form(key="tx_form"):
            sender = st.text_input("Sender Wallet", value="0xClientWallet...")
            recipient = st.text_input("Recipient Wallet", value="0xAkshay...")
            amount = st.number_input("Amount (AUM)", value=100.0, min_value=0.1)
            submit_tx = st.form_submit_button("Sign & Send Transaction")
            
            if submit_tx:
                bc.add_transaction(sender, recipient, amount)
                st.success("✅ Transaction added to mempool! Switch to Network Controls to mine.")

    with right_col:
        st.subheader("⛏️ Network Controls")
        st.write(f"**Pending Transactions in Mempool:** {len(bc.pending_transactions)}")
        st.write(f"**Current Network Difficulty:** {bc.difficulty}")
        
        if st.button("⛏️ Mine Pending Blocks (PoW)"):
            with st.spinner("Cryptographic hashing in progress..."):
                result = bc.mine_block()
                st.success(result)
                st.rerun() 
                
        if st.button("🛡️ Validate Ledger Integrity"):
            valid = bc.is_chain_valid()
            if valid:
                st.success("✅ Cryptographic validation passed. Chain is secure.")
            else:
                st.error("🚨 Warning: Chain data has been tampered with!")

        if st.button("🔄 Reset Network"):
            st.session_state.blockchain = AUMBlockchain()
            st.success("Network reset to Genesis Block!")
            st.rerun()


# ==========================================
# TAB 2: AUMscan (BLOCKCHAIN EXPLORER)
# ==========================================
with tab2:
    st.header("🔍 AUMscan")
    
    # Calculate total transactions across the whole chain
    total_txns = sum(len(b.transactions) for b in bc.chain)
    
    # Explorer High-Level Stats
    ex_col1, ex_col2, ex_col3, ex_col4 = st.columns(4)
    ex_col1.metric("Block Height", len(bc.chain) - 1)
    ex_col2.metric("Total Transactions", total_txns)
    ex_col3.metric("Active Shards", bc.shard_count)
    ex_col4.metric("Network Status", "🟢 Online")
    
    st.divider()
    
    # --- Etherscan Style Tables ---
    table_col1, table_col2 = st.columns([1, 1])
    
    with table_col1:
        st.subheader("📦 Latest Blocks")
        # Prepare data for the DataFrame
        block_data = []
        for b in reversed(bc.chain):
            block_data.append({
                "Block": b.index,
                "Age (UTC)": time.strftime('%H:%M:%S', time.gmtime(b.timestamp)),
                "Txn Count": len(b.transactions),
                "Shard": b.shard_id,
                "Hash": b.hash[:12] + "..."
            })
        
        # Display as a clean, index-less table
        df_blocks = pd.DataFrame(block_data)
        st.dataframe(df_blocks, use_container_width=True, hide_index=True)

    with table_col2:
        st.subheader("📝 Latest Transactions")
        tx_data = []
        # Get the latest transactions by iterating backwards through blocks
        for b in reversed(bc.chain):
            for tx in reversed(b.transactions):
                tx_data.append({
                    "Block": b.index,
                    "From": tx['sender'][:12] + "..." if len(tx['sender'])>12 else tx['sender'],
                    "To": tx['recipient'][:12] + "..." if len(tx['recipient'])>12 else tx['recipient'],
                    "Amount": f"{tx['amount']} AUM"
                })
                if len(tx_data) >= 10: # Only show latest 10
                    break
            if len(tx_data) >= 10:
                break
                
        df_txs = pd.DataFrame(tx_data)
        st.dataframe(df_txs, use_container_width=True, hide_index=True)

    st.divider()
    
    # --- Search / Inspect Specific Block ---
    st.subheader("🔎 Inspect Block Details")
    search_block = st.number_input("Search by Block Number", min_value=0, max_value=len(bc.chain)-1, value=len(bc.chain)-1)
    
    selected_block = bc.chain[search_block]
    
    st.markdown(f"**Block Height:** `{selected_block.index}`")
    st.markdown(f"**Timestamp:** `{time.ctime(selected_block.timestamp)}`")
    st.markdown(f"**Shard ID:** `{selected_block.shard_id}`")
    st.markdown(f"**Nonce:** `{selected_block.nonce}`")
    st.markdown(f"**Block Hash:** `{selected_block.hash}`")
    st.markdown(f"**Parent Hash:** `{selected_block.previous_hash}`")
    
    with st.expander("View Raw Transaction Data (JSON)"):
        st.json(selected_block.transactions)
