import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fund Split Calculator", layout="centered")
st.title("💰 Fund Split Calculator")

st.markdown("""
Enter your fund allocations below. You can add or remove rows as needed.
- **Fund**: Name of the fund
- **Amount**: Dollar amount
- **Splits**: Percentages for each split (must sum to 100%)
""")

# Session state for dynamic rows
if "rows" not in st.session_state:
    st.session_state.rows = [
        {
            "fund": "",
            "amount": 0.0,
            "Equities": 34,
            "Fixed Inc": 33,
            "Cash": 33
        }
    ]

def add_row():
    st.session_state.rows.append({
        "fund": "",
        "amount": 0.0,
        "Equities": 34,
        "Fixed Inc": 33,
        "Cash": 33
    })

def remove_row(idx):
    if len(st.session_state.rows) > 1:
        st.session_state.rows.pop(idx)

# Split columns
split_names = ["Equities", "Fixed Inc", "Cash"]
# No auto-adjustment: all splits are entered manually by the user.
# The adjust_splits function and related callbacks are removed.

# Input table
st.subheader("Fund Entries")
for idx, row in enumerate(st.session_state.rows):
    cols = st.columns([2, 2] + [1]*len(split_names) + [0.5])
    row["fund"] = cols[0].text_input("Fund", value=row["fund"], key=f"fund_{idx}")
    row["amount"] = float(cols[1].number_input("Amount", min_value=0.0, value=float(row["amount"]), step=0.01, key=f"amount_{idx}", format="%.2f"))

    for sidx, split in enumerate(split_names):
        row[split] = cols[2+sidx].number_input(
            f"{split} %",
            min_value=0,
            max_value=100,
            value=row.get(split, 0),
            step=1,
            key=f"{split}_{idx}"
        )
    if cols[-1].button("🗑️", key=f"remove_{idx}"):
        remove_row(idx)
        st.rerun()

st.button("➕ Add Row", on_click=add_row)

# Validation
valid = True
for row in st.session_state.rows:
    if sum(row[s] for s in split_names) != 100:
        valid = False
        st.warning("Each row's splits must sum to 100%.", icon="⚠️")
        break

if st.button("Calculate", disabled=not valid):
    df = pd.DataFrame(st.session_state.rows)
    for split in split_names:
        df[f"{split}_amt"] = df["amount"] * df[split] / 100

    total_amount = df["amount"].sum()
    split_totals = {split: df[f"{split}_amt"].sum() for split in split_names}

    st.subheader("Summary Table")
    display_cols = ["fund", "amount"] + split_names + [f"{split}_amt" for split in split_names]
    st.dataframe(df[display_cols], use_container_width=True)

    st.markdown(f"**Total Amount:** `${total_amount:,.2f}`")
    for split in split_names:
        st.markdown(f"- Total {split}: `${split_totals[split]:,.2f}` ({split_totals[split]/total_amount*100:.1f}%)")

    # Pie chart
    pie_df = pd.DataFrame({
        "Split": split_names,
        "Amount": [split_totals[split] for split in split_names]
    })
    # Use Plotly's go.Figure for explicit color control
    import plotly.graph_objects as go
    color_list = ["#326171", "#445937", "#C99213"]  # Teal, Green, Mustard

    fig = go.Figure(
        data=[go.Pie(
            labels=pie_df["Split"],
            values=pie_df["Amount"],
            marker=dict(colors=color_list)
        )]
    )
    fig.update_layout(title_text="Overall Split Proportion")
    st.plotly_chart(fig, use_container_width=True)

    st.success("Calculation complete! 🎉")
