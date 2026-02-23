import streamlit as st
import hashlib
import time
import json
import pandas as pd
import random

# --- Page Configuration & Glassmorphism CSS ---
st.set_page_config(page_title="AUM Blockchain Explorer", layout="wide", page_icon="💠")

st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.1), transparent 30%),
            radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.1), transparent 30%);
        color: #e2e8f0;
    }
    h1, h2, h3 { color: #38bdf8 !important; }
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
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px;
        padding: 20px;
    }
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
        self.current_supply = 500 

    def create_genesis_block(self):
        return Block(0, "0", time.time(), [{"sender": "System", "recipient": "Genesis_Vault", "amount": 500, "type": "Genesis"}], 0)

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, amount):
        tx = {
            "sender": sender,
            "recipient": recipient,
            "amount": float(amount),
            "type": "Transfer"
        }
        self.pending_transactions.append(tx)

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
                if self.current_supply + reward <= self.total_supply:
                    self.current_supply += reward
                    new_block.transactions.insert(0, {"sender": "Network", "recipient": "Miner_Reward", "amount": reward, "type": "Reward"})

                while new_block.hash[:self.difficulty] != '0' * self.difficulty:
                    new_block.nonce += 1
                    new_block.hash = new_block.calculate_hash()

                self.chain.append(new_block)
                mined_count += 1

        self.pending_transactions = []
        # Dynamic difficulty adjustment based on chain length
        self.difficulty = min(max(self.difficulty + (len(self.chain) % 5 == 0), 2), 5)
        return f"Mined {mined_count} blocks across shards in {time.time() - start_time:.2f}s."

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.hash != current.calculate_hash() or current.previous_hash != previous.hash:
                return False
        return True

# --- Initialize Session State ---
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = AUMBlockchain()
bc = st.session_state.blockchain

# --- Main App Title ---
st.title("💠 AUM Network")
st.caption("Live Sharded Proof-of-Work Demo | Developed by @0xSturdy")

# --- Tokenomics Dashboard (Always Visible) ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Max Supply", f"{bc.total_supply:,.0f} AUM")
col2.metric("Mined / Circulating", f"{bc.current_supply:,.2f} AUM")
col3.metric("Available to Mine", f"{(bc.total_supply - bc.current_supply):,.2f} AUM")
st.divider()

# --- Tabs Navigation ---
tab1, tab2, tab3 = st.tabs(["🏦 Transact & Stress Test", "📜 Tokenize Assets", "🔍 AUMscan Explorer"])

# ==========================================
# TAB 1: TRANSACT & STRESS TEST
# ==========================================
with tab1:
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.subheader("💸 Send Transaction")
        with st.form(key="tx_form"):
            sender = st.text_input("Sender Name / Wallet", value="Client_Enterprise")
            recipient = st.text_input("Recipient Name / Wallet", value="Akshay_Wallet")
            amount = st.number_input("Amount (AUM)", value=100.0, min_value=0.1)
            submit_tx = st.form_submit_button("Send Transaction")
            
            if submit_tx:
                bc.add_transaction(sender, recipient, amount)
                st.success("✅ Transaction successfully added to the mempool!")

        st.markdown("---")
        st.subheader("🚀 Network Stress Test")
        st.write("Simulate massive network traffic to demonstrate AUM's sharding capabilities.")
        if st.button("Generate 100 Random Transactions"):
            with st.spinner("Flooding mempool with traffic..."):
                for _ in range(100):
                    bc.add_transaction(f"0xUser_{random.randint(1000, 9999)}", f"0xUser_{random.randint(1000, 9999)}", round(random.uniform(0.1, 50.0), 2))
            st.success("✅ 100 transactions injected! Switch to Network Controls to mine them.")

    with right_col:
        st.subheader("⛏️ Network Controls")
        st.info(f"**Pending Transactions in Mempool:** {len(bc.pending_transactions)}\n\n**Current Network Difficulty:** {bc.difficulty}")
        
        if st.button("⛏️ Mine Pending Blocks (PoW)"):
            with st.spinner("Cryptographic hashing in progress..."):
                result = bc.mine_block()
                st.success(result)
                st.rerun() 
                
        if st.button("🛡️ Validate Ledger Integrity"):
            valid = bc.is_chain_valid()
            if valid:
                st.success("✅ Cryptographic validation passed. Immutable chain is secure.")
            else:
                st.error("🚨 Warning: Chain data has been tampered with!")

        if st.button("🔄 Reset Network"):
            st.session_state.blockchain = AUMBlockchain()
            st.success("Network reset to Genesis Block!")
            st.rerun()

# ==========================================
# TAB 2: TOKENIZE ASSETS
# ==========================================
with tab2:
    st.header("📜 Tokenize Real-World Assets")
    st.write("AUM isn't just for currency. Use the blockchain as an immutable ledger to register real estate, supply chain items, or intellectual property.")
    
    with st.form(key="asset_form"):
        asset_owner = st.text_input("Owner Wallet", value="Client_Holdings_LLC")
        asset_name = st.text_input("Asset Name", value="Manhattan Commercial Property Deed")
        asset_data = st.text_area("Asset Metadata / Contract Details", value="Registry ID: 9982-A.\nAppraised Value: $12.5M.\nCoordinates: 40.7128° N, 74.0060° W")
        
        mint_asset = st.form_submit_button("Mint Asset to Blockchain")
        
        if mint_asset:
            tx = {
                "sender": "System_Smart_Contract",
                "recipient": asset_owner,
                "amount": 0.0,
                "type": "Asset Registration",
                "asset_name": asset_name,
                "metadata": asset_data
            }
            bc.pending_transactions.append(tx)
            st.success(f"✅ '{asset_name}' securely queued for immutable registration! Mine a block to finalize.")

# ==========================================
# TAB 3: AUMscan (EXPLORER)
# ==========================================
with tab3:
    st.header("🔍 AUMscan Analytics")
    total_txns = sum(len(b.transactions) for b in bc.chain)
    
    # Live Chart
    st.subheader("📈 Network Analytics: Transactions per Block")
    tx_counts = [len(b.transactions) for b in bc.chain]
    st.line_chart(tx_counts, use_container_width=True)
    
    ex_col1, ex_col2, ex_col3, ex_col4 = st.columns(4)
    ex_col1.metric("Block Height", len(bc.chain) - 1)
    ex_col2.metric("Total Transactions", total_txns)
    ex_col3.metric("Active Shards", bc.shard_count)
    ex_col4.metric("Network Status", "🟢 Online")
    st.divider()
    
    table_col1, table_col2 = st.columns([1, 1])
    with table_col1:
        st.subheader("📦 Latest Blocks")
        block_data = [{"Block": b.index, "Age (UTC)": time.strftime('%H:%M:%S', time.gmtime(b.timestamp)), "Txns": len(b.transactions), "Shard": b.shard_id, "Hash": b.hash[:12] + "..."} for b in reversed(bc.chain)]
        st.dataframe(pd.DataFrame(block_data), use_container_width=True, hide_index=True)

    with table_col2:
        st.subheader("📝 Latest Activity")
        tx_data = []
        for b in reversed(bc.chain):
            for tx in reversed(b.transactions):
                tx_data.append({
                    "Block": b.index,
                    "Type": tx.get('type', 'Transfer'),
                    "From": tx['sender'][:10] + "..." if len(tx['sender'])>10 else tx['sender'],
                    "To": tx['recipient'][:10] + "..." if len(tx['recipient'])>10 else tx['recipient'],
                    "Details": tx.get('asset_name', f"{tx.get('amount', 0)} AUM")
                })
                if len(tx_data) >= 10: break
            if len(tx_data) >= 10: break
        st.dataframe(pd.DataFrame(tx_data), use_container_width=True, hide_index=True)
        
    st.divider()
    st.subheader("🔎 Inspect Block Details")
    search_block = st.number_input("Search by Block Number", min_value=0, max_value=max(0, len(bc.chain)-1), value=max(0, len(bc.chain)-1))
    
    selected_block = bc.chain[search_block]
    st.markdown(f"**Block Hash:** `{selected_block.hash}`")
    st.markdown(f"**Parent Hash:** `{selected_block.previous_hash}`")
    
    with st.expander("View Raw JSON Data"):
        st.json(selected_block.transactions)
