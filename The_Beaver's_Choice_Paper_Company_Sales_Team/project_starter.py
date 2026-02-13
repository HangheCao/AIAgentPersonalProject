import pandas as pd
import numpy as np
import os
import time
import dotenv
import ast
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union, Any, Union
from sqlalchemy import create_engine, Engine
from smolagents import (
    ToolCallingAgent,
    OpenAIServerModel,
    tool,
)
from difflib import get_close_matches
from dotenv import load_dotenv
from difflib import get_close_matches

def normalize_ymd(d: Union[str, datetime]) -> str:
    """Return YYYY-MM-DD for inputs like 2025/4/1, 2025-04-01, or datetime."""
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")

    s = str(d).strip()

    # already ISO-ish
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]

    # common non-ISO: 2025/4/1 or 2025/04/01
    for fmt in ("%Y/%m/%d", "%Y/%m/%d", "%Y/%m/%d", "%Y/%m/%d", "%Y/%m/%d"):
        # (keep simple; we'll do robust parsing below)
        pass

    # robust parsing for 2025/4/1 and 2025/04/01
    try:
        dt = datetime.strptime(s, "%Y/%m/%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # fallback: split and zero-pad if it's like Y/M/D
    if "/" in s:
        parts = s.split("/")
        if len(parts) == 3:
            y, m, d2 = parts
            return f"{int(y):04d}-{int(m):02d}-{int(d2):02d}"

    raise ValueError(f"Unrecognized date format: {d!r}")

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]



def resolve_item_name(raw_name: str) -> str:
    items = (
        pd.read_sql("SELECT item_name FROM inventory", db_engine)["item_name"]
        .dropna()
        .astype(str)
        .tolist()
    )

    raw = raw_name.strip()
    if raw in items:
        return raw

    lower_map = {i.lower(): i for i in items}
    if raw.lower() in lower_map:
        return lower_map[raw.lower()]

    matches = get_close_matches(raw, items, n=1, cutoff=0.5)
    if matches:
        return matches[0]

    raise ValueError(f"Item not carried: '{raw_name}'")

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def _to_ymd(date_like) -> str:
    """Accepts str / datetime / pandas Timestamp and returns YYYY-MM-DD."""
    if isinstance(date_like, str):
        s = date_like.strip()
        # if already ISO, keep first 10 chars
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            return s[:10]
        # handle 2025/4/1 etc
        if "/" in s:
            y, m, d = s.split("/")
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        return s  # last resort

    # pandas Timestamp / datetime
    if isinstance(date_like, (pd.Timestamp, datetime)):
        return pd.Timestamp(date_like).strftime("%Y-%m-%d")
    
def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = _to_ymd(date)

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        as_of_date = _to_ymd(as_of_date)

        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE DATE(transaction_date) <= DATE(:as_of_date)",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0

def get_stock_level_helper(item_name: str, as_of_date: Union[str, datetime]) -> int:
    """
    Pure helper (NON-tool). Returns available units as an int.
    - Resolves item name
    - Normalizes date to YYYY-MM-DD
    - Uses the starter DB helper get_stock_level()
    """
    try:
        resolved = resolve_item_name(item_name)
    except ValueError:
        return -1  # not carried

    as_of_date = _to_ymd(as_of_date)
    df = get_stock_level(resolved, as_of_date)

    if df is None or len(df) == 0:
        return 0

    # Your get_stock_level() returns 'current_stock' (per its SQL alias)
    if "current_stock" in df.columns:
        return int(df.iloc[0]["current_stock"])

    # fallback: if it's 1x1
    if df.shape[1] == 1:
        return int(df.iloc[0, 0])

    return 0

def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    as_of_date = _to_ymd(as_of_date)  # keep YYYY-MM-DD even if timestamp

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock = get_stock_level_helper(item["item_name"], as_of_date)
        if stock < 0:
            stock = 0
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND DATE(transaction_date) <= DATE(:date)
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################


# Set up and load your env parameters and instantiate your model.
load_dotenv()

model = OpenAIServerModel(
    model_id="gpt-4o-mini",
    api_key=os.getenv("UDACITY_OPENAI_API_KEY"),
    api_base="https://openai.vocareum.com/v1",
)

"""Set up tools for your agents to use, these should be methods that combine the database functions above
 and apply criteria to them to ensure that the flow of the system is correct."""

# ==== TOOLS
# ===== BOOKMARK: INVENTORY AGENT TOOLS =====
@tool
def inventory_snapshot(as_of_date: str) -> Dict[str, Any]:
    """
    Return a snapshot of current inventory as of a given date.

    Args:
        as_of_date: Date for the snapshot in YYYY-MM-DD format.

    Returns:
        A dictionary containing the inventory snapshot.
    """
    return get_all_inventory(as_of_date)

@tool
def stock_level(item_name: str, as_of_date: str) -> int:
    """
    Return stock level of an item as of a given date.

    Rules:
    - If item is not carried in inventory, return -1
    - Otherwise return available stock as an integer

    Args:
        item_name: Name of the inventory item (may be approximate)
        as_of_date: Date in YYYY-MM-DD format

    Returns:
        Stock level as int (or -1 if item not carried)
    """

    # --- Step 1: Resolve item name safely ---
    try:
        item_name = resolve_item_name(item_name)
    except ValueError:
        return -1   # item not carried

    # --- Step 2: Query stock using starter helper ---
    order_date = _to_ymd(as_of_date)
    df = get_stock_level(item_name, as_of_date)

    # --- Step 3: Extract stock value safely ---
    if df is None or len(df) == 0:
        return 0

    # Common column names that might appear
    for col in ["stock_level", "units", "current_stock", "stock", "quantity"]:
        if col in df.columns:
            return int(df.iloc[0][col])

    # If it's a 1x1 dataframe, take the only value
    if df.shape[1] == 1:
        return int(df.iloc[0, 0])

    # Unexpected output → fail safely
    return 0

@tool
def low_stock_items(as_of_date: str) -> List[Dict[str, Any]]:
    """
    List items whose stock level is below their minimum threshold.

    Args:
        as_of_date: Date in YYYY-MM-DD format.

    Returns:
        A list of dicts with item_name, stock_level, min_stock_level.
    """
    inv = pd.read_sql(
        "SELECT item_name, min_stock_level FROM inventory",
        db_engine
    )

    results = []
    for _, row in inv.iterrows():
        item = row["item_name"]
        min_lvl = int(row["min_stock_level"])
        lvl = int(stock_level(item, as_of_date))  # uses transactions
        if lvl < min_lvl:
            results.append({
                "item_name": item,
                "stock_level": lvl,
                "min_stock_level": min_lvl
            })

    # sort from most urgent
    results.sort(key=lambda x: x["stock_level"] - x["min_stock_level"])
    return results

@tool
def inventory_table(as_of_date: str, limit: int = 30) -> List[Dict[str, Any]]:
    """
    Return an inventory table as of a date (limited rows).

    Args:
        as_of_date: Date in YYYY-MM-DD format.
        limit: Max number of rows to return.

    Returns:
        List of dict rows with item_name, stock_level, unit_price, min_stock_level.
    """
    inv = pd.read_sql(
        "SELECT item_name, unit_price, min_stock_level FROM inventory",
        db_engine
    ).head(int(limit))

    rows = []
    for _, row in inv.iterrows():
        item = row["item_name"]
        rows.append({
            "item_name": item,
            "stock_level": int(stock_level(item, as_of_date)),
            "unit_price": float(row["unit_price"]),
            "min_stock_level": int(row["min_stock_level"]),
        })
    return rows

# Tools for quoting agent
# ===== BOOKMARK: QUOTING AGENT TOOLS =====
@tool
def get_unit_price(item_name: str) -> float:
    """
    Return unit price of an item. If not carried, return -1.0.

    Args:
        item_name: Name of the inventory item.

    Returns:
        Unit price as float, or -1.0 if not carried.
    """
    try:
        item_name = resolve_item_name(item_name)
    except ValueError:
        return -1.0

    df = pd.read_sql(
        "SELECT unit_price FROM inventory WHERE item_name = :item_name",
        db_engine,
        params={"item_name": item_name},
    )
    if not len(df):
        return -1.0
    return float(df.iloc[0]["unit_price"])

@tool
def check_inventory(item_name: str, quantity: int, as_of_date: str) -> bool:
    """
    Check whether sufficient stock is available.

    Args:
        item_name: Name of the inventory item.
        quantity: Requested quantity.
        as_of_date: Date in YYYY-MM-DD format.

    Returns:
        True if sufficient stock exists, otherwise False.
    """
    current_stock = int(stock_level(item_name, as_of_date))
    return current_stock >= quantity

@tool
def calculate_quote(item_name: str, quantity: int, markup: float = 0.2) -> float:
    """
    Calculate total quote price.

    Args:
        item_name: Name of the inventory item.
        quantity: Number of units requested.
        markup: Profit margin percentage (default 0.2 = 20%).

    Returns:
        Total quoted price as a float.
    """
    unit_price = get_unit_price(item_name)
    base_cost = unit_price * quantity
    total_price = base_cost * (1 + markup)
    return round(total_price, 2)

@tool
def generate_quote_explanation(item_name: str, quantity: int, markup: float) -> str:
    """
    Generate explanation for quote pricing.

    Args:
        item_name: Name of the inventory item.
        quantity: Number of units requested.
        markup: Profit margin applied.

    Returns:
        Explanation string describing pricing logic.
    """
    unit_price = get_unit_price(item_name)
    base_cost = unit_price * quantity
    total = base_cost * (1 + markup)

    return (
        f"The base unit price is ${unit_price:.2f}. "
        f"For {quantity} units, the base cost is ${base_cost:.2f}. "
        f"A {markup*100:.0f}% markup was applied, "
        f"bringing the total quote to ${total:.2f}."
    )

@tool
def get_quote_request(request_id: int) -> Dict[str, Any]:
    """
    Fetch a quote request record by id.

    Args:
        request_id: ID of the quote request.

    Returns:
        A dictionary of the quote request fields.
    """
    df = pd.read_sql(
        "SELECT * FROM quote_requests WHERE id = :id",
        db_engine,
        params={"id": int(request_id)},
    )
    if not len(df):
        raise ValueError(f"No quote request found with id={request_id}")
    return df.iloc[0].to_dict()

@tool
def compute_quote(item_name: str, quantity: int, as_of_date: str, markup: float = 0.2) -> Dict[str, Any]:
    """
    Compute a quote for an item including availability and total price.

    Args:
        item_name: Name of the inventory item.
        quantity: Units requested.
        as_of_date: Date in YYYY-MM-DD format used for stock check.
        markup: Markup fraction (0.2 = 20%).

    Returns:
        Dict with availability, pricing, and explanation.
        If item is not carried, returns is_carried=False with message.
    """
    if markup is None:
        markup = 0.2

    unit_price = get_unit_price(item_name)
    available_units = int(stock_level(item_name, as_of_date))

    # not carried case
    if unit_price < 0:
        return {
            "item_name": item_name,
            "quantity": int(quantity),
            "as_of_date": as_of_date,
            "is_carried": False,
            "is_available": False,
            "message": f"We do not carry '{item_name}'.",
        }

    base_cost = float(unit_price) * int(quantity)
    total_price = round(base_cost * (1 + float(markup)), 2)
    is_available = available_units >= int(quantity)

    return {
        "item_name": item_name,
        "quantity": int(quantity),
        "as_of_date": as_of_date,
        "is_carried": True,
        "available_units": available_units,
        "is_available": bool(is_available),
        "unit_price": float(unit_price),
        "base_cost": round(base_cost, 2),
        "markup": float(markup),
        "total_price": float(total_price),
        "explanation": (
            f"Unit price ${unit_price:.2f}; base ${base_cost:.2f}; "
            f"markup {markup*100:.0f}% → total ${total_price:.2f}. "
            f"Stock as of {as_of_date}: {available_units}."
        ),
    }

@tool
def save_quote(request_id: int, total_amount: float, quote_explanation: str, order_date: str) -> str:
    """
    Save a generated quote to the quotes table.

    Args:
        request_id: Quote request id.
        total_amount: Total quoted amount.
        quote_explanation: Explanation text.
        order_date: Date in YYYY-MM-DD format.

    Returns:
        Confirmation message.
    """
    row = pd.DataFrame([{
        "request_id": int(request_id),
        "total_amount": float(total_amount),
        "quote_explanation": str(quote_explanation),
        "order_date": str(order_date),
        "job_type": "",
        "order_size": "",
        "event_type": "",
    }])
    row.to_sql("quotes", db_engine, if_exists="append", index=False)
    return f"Saved quote for request_id={request_id}."

@tool
def is_item_carried(item_name: str) -> bool:
    """
    Check whether an item exists in the inventory catalog.

    Args:
        item_name: Item name from the request.

    Returns:
        True if the item can be found/resolved in inventory, else False.
    """
    try:
        _ = resolve_item_name(item_name)  # your helper
        return True
    except ValueError:
        return False

# Tools for ordering agent
# ===== BOOKMARK: ORDERING AGENT TOOLS =====
@tool
def get_cash_balance_tool(as_of_date: str) -> float:
    """Return cash balance as of a given date.

    Args:
        as_of_date (str): Date cutoff (inclusive) in YYYY-MM-DD format.

    Returns:
        float: Cash balance.
    """
    as_of_date = _to_ymd(as_of_date)
    return round(float(get_cash_balance(as_of_date)), 2)

@tool
def place_sales_order(item_name: str, quantity: int, total_price: float, order_date: str) -> int:
    """
    Record a customer sale order as a transaction, after verifying inventory.

    Args:
        item_name: Name of the inventory item.
        quantity: Number of units sold.
        total_price: Total price charged to the customer.
        order_date: Date of the sale in YYYY-MM-DD format.

    Returns:
        The inserted transaction id.
    """
    order_date = _to_ymd(order_date)
    available = stock_level(item_name, order_date)
    if available < quantity:
        raise ValueError(
            f"Insufficient stock for '{item_name}' on {order_date}. "
            f"Requested {quantity}, available {available}."
        )

    # Starter helper you showed: create_transaction(...)
    txn_id = create_transaction(
        item_name=item_name,
        transaction_type="sales",
        quantity=quantity,
        price=float(total_price),
        date=order_date,
    )
    return int(txn_id)

@tool
def place_stock_order(item_name: str, quantity: int, order_date: str) -> int:
    """
    Place a stock reorder for an item (records a stock_orders transaction).

    Args:
        item_name: Name of the inventory item.
        quantity: Number of units to order.
        order_date: Date of the order in YYYY-MM-DD format.

    Returns:
        The inserted transaction id.
    """
    
    order_date = str(order_date)[:10]
    order_date = _to_ymd(order_date)
    # normalize / validate name
    name = resolve_item_name(item_name)

    unit_price = float(get_unit_price(name))
    total_cost = float(unit_price * int(quantity))

    cash = float(get_cash_balance(order_date))
    if cash < total_cost:
        raise ValueError(
            f"Insufficient cash to reorder '{name}'. "
            f"Need ${total_cost:.2f}, have ${cash:.2f}."
        )

    txn_id = create_transaction(
        item_name=name,
        transaction_type="stock_orders",
        quantity=int(quantity),
        price=total_cost,
        date=order_date,
    )
    return int(txn_id)

@tool
def reorder_if_below_min(item_name: str, order_date: str, target_level: int = 600) -> str:
    """
    If item stock is below minimum level, place a stock order up to target_level.

    Safe behavior (prevents agent infinite retries):
    - If item is not carried / cannot be resolved -> return a message (no exception)
    - If item exists but no reorder needed -> return a message
    - If not enough cash -> return a message (no exception)

    Args:
        item_name: Name from the request (may be approximate)
        order_date: YYYY-MM-DD
        target_level: desired stock level after reorder

    Returns:
        Human-readable message describing result.
    """
    # 1) Resolve item name
    try:
        name = resolve_item_name(item_name)
    except ValueError:
        return f"REJECTED: '{item_name}' is not carried, so no reorder was placed."

    # 2) Pull inventory row
    inv = pd.read_sql(
        "SELECT min_stock_level, unit_price FROM inventory WHERE item_name = :item_name",
        db_engine,
        params={"item_name": name},
    )
    if not len(inv):
        # This should be rare if resolve_item_name is correct, but keep safe anyway
        return f"REJECTED: '{name}' not found in inventory table; no reorder placed."

    min_level = int(inv.iloc[0]["min_stock_level"])

    # 3) Compute current stock as of date (uses transactions)
    current = int(stock_level(name, order_date))
    if current < 0:
        return f"REJECTED: '{name}' not carried; no reorder placed."

    if current >= min_level:
        return f"No reorder needed for '{name}'. Stock {current} >= min {min_level}."

    qty_to_order = max(0, int(target_level) - current)
    if qty_to_order <= 0:
        return f"Below min for '{name}', but target_level ({target_level}) <= current ({current}); no reorder placed."

    # 4) Try to place stock order (catch cash failures)
    try:
        txn_id = place_stock_order(name, qty_to_order, order_date)
        return f"Reorder placed for '{name}': ordered {qty_to_order} units (txn_id={txn_id})."
    except ValueError as e:
        return f"FAILED to reorder '{name}': {str(e)}"

@tool
def place_sales_orders_batch(order_date: str, items: List[Dict], markup: float = 0.2) -> Dict[str, Any]:
    """
    Place multiple sales orders in one call.

    Args:
        order_date: Date of the sales order in YYYY-MM-DD format.
        items: List of dictionaries where each dictionary contains:
            - item_name: Name of the inventory item.
            - quantity: Number of units to sell.
        markup: Markup fraction applied to unit price (default 0.2).

    Returns:
        A summary string describing which orders were placed or rejected.
    """

    results = []
    total_charged = 0.0

    for it in items:
        raw_name = str(it.get("item_name", "")).strip()
        qty = int(it.get("quantity", 0))

        if not raw_name or qty <= 0:
            results.append(f"- Skipped invalid line item: {it}")
            continue

        # Resolve / validate item name
        try:
            name = resolve_item_name(raw_name)
        except Exception:
            results.append(f"- REJECTED: '{raw_name}' not carried.")
            continue

        # Stock check
        available = int(stock_level(name, order_date))
        if available < qty:
            results.append(f"- REJECTED: {name} (need {qty}, have {available}).")
            continue

        # Price rule: unit_price * qty * (1+markup)
        unit_price = float(get_unit_price(name))
        line_total = round(unit_price * qty * (1 + float(markup)), 2)

        txn_id = create_transaction(
            item_name=name,
            transaction_type="sales",
            quantity=qty,
            price=line_total,
            date=order_date,
        )

        total_charged += line_total
        results.append(f"- PLACED: {qty} x {name} (${line_total:.2f}) txn_id={int(txn_id)}")

    return "BATCH RESULT\n" + "\n".join(results) + f"\nTotal charged: ${total_charged:.2f}"

# ===== BOOKMARK: ORCHESTRATION AGENT TOOL =====

@tool
def ask_inventory_agent(question: str) -> str:
    """
    Ask the inventory agent a question and return its response.

    Args:
        question: The question to ask inventory agent.

    Returns:
        The inventory agent's response as text.
    """
    return str(inventory_agent.run(question))


@tool
def ask_quoting_agent(question: str) -> str:
    """
    Ask the quoting agent a question and return its response.

    Args:
        question: The question to ask quoting agent.

    Returns:
        The quoting agent's response as text.
    """
    return str(quoting_agent.run(question))


@tool
def ask_ordering_agent(question: str) -> str:
    """
    Ask the ordering agent a question and return its response.

    Args:
        question: The question to ask ordering agent.

    Returns:
        The ordering agent's response as text.
    """
    return str(ordering_agent.run(question))


@tool
def process_request(
    request_id: int,
    as_of_date: str,
    markup: float = 0.2,
    auto_reorder: bool = True,
) -> Dict[str, Any]:
    """
    End-to-end processing of a quote request (supports multi-item requests).

    Steps:
    1) Fetch request row
    2) Extract line items (quantity + item_name) from request text
    3) For each item: quote + (sell if possible) + optional reorder
    4) Return summary with fulfilled/partial/rejected breakdown

    Args:
        request_id: Quote request id.
        as_of_date: Date for stock checks / ordering in YYYY-MM-DD format.
        markup: Markup fraction to apply to quote (default 0.2).
        auto_reorder: Whether to attempt a small reorder for shortfalls.

    Returns:
        Dict summary of actions taken.
    """
    req = get_quote_request(int(request_id))

    # --- Find the free-text request field ---
    request_text = (
        req.get("request")
        or req.get("request_text")
        or req.get("message")
        or req.get("details")
        or ""
    )
    request_text = str(request_text)

    if not request_text.strip():
        return {
            "request_id": int(request_id),
            "status": "rejected_no_request_text",
            "request": req,
            "items": [],
            "note": "No request text found in quote_requests row."
        }

    # --- Extract items: patterns like "500 sheets of colorful poster paper" ---
    # Accepts: "500 sheets of X", "300 rolls of Y", "200 balloons"
    pattern = re.compile(
        r"(\d{1,6})\s*(?:sheets?|reams?|rolls?|packs?|packets?|boxes?|units?)?\s*(?:of\s+)?([^,\n]+)",
        flags=re.IGNORECASE,
    )
    matches = pattern.findall(request_text)

    # If regex is too greedy, at least fallback to single-item attempt
    line_items: List[Dict[str, Any]] = []
    for qty_str, name_str in matches:
        qty = int(qty_str)
        name = name_str.strip().strip(".").strip()
        if qty > 0 and len(name) >= 2:
            line_items.append({"raw_item_name": name, "quantity": qty})

    # De-duplicate obvious repeats
    seen = set()
    cleaned = []
    for it in line_items:
        key = (it["raw_item_name"].lower(), int(it["quantity"]))
        if key not in seen:
            seen.add(key)
            cleaned.append(it)
    line_items = cleaned

    if not line_items:
        # fallback to old logic if your table actually has item_name/quantity
        item_name = req.get("item_name") or req.get("paper_type") or req.get("product") or req.get("item")
        quantity = req.get("quantity") or req.get("units") or req.get("qty")
        if item_name is None or quantity is None:
            return {
                "request_id": int(request_id),
                "status": "rejected_parse_failed",
                "request": req,
                "items": [],
                "note": "Could not extract any line items from request text."
            }
        line_items = [{"raw_item_name": str(item_name), "quantity": int(quantity)}]

    results = {
        "request_id": int(request_id),
        "as_of_date": as_of_date,
        "request": req,
        "items": [],
        "status": None,
        "total_charged": 0.0,
    }

    any_fulfilled = False
    any_rejected = False

    for it in line_items:
        raw_name = it["raw_item_name"]
        qty = int(it["quantity"])

        item_result = {
            "raw_item_name": raw_name,
            "resolved_item_name": None,
            "quantity": qty,
            "quote": None,
            "sale_transaction_id": None,
            "reorder_result": None,
            "status": None,
            "reason": None,
        }

        # Resolve carried
        try:
            resolved = resolve_item_name(raw_name)
            item_result["resolved_item_name"] = resolved
        except ValueError:
            item_result["status"] = "rejected_not_carried"
            item_result["reason"] = "Item not carried"
            any_rejected = True
            results["items"].append(item_result)
            continue

        # Quote
        quote = compute_quote(item_name=resolved, quantity=qty, as_of_date=as_of_date, markup=float(markup))
        item_result["quote"] = quote

        if not quote["is_available"] and auto_reorder:
            # Try a small reorder policy (your reorder tool already cash-caps now)
            item_result["reorder_result"] = reorder_if_below_min(resolved, as_of_date, target_level=600)
            # Re-quote after reorder attempt
            quote = compute_quote(item_name=resolved, quantity=qty, as_of_date=as_of_date, markup=float(markup))
            item_result["quote"] = quote

        if not quote["is_available"]:
            item_result["status"] = "rejected_insufficient_stock"
            item_result["reason"] = f"Insufficient stock as of {as_of_date}"
            any_rejected = True
            results["items"].append(item_result)
            continue

        # Place sale
        sale_id = place_sales_order(
            item_name=resolved,
            quantity=qty,
            total_price=float(quote["total_price"]),
            order_date=as_of_date,
        )
        item_result["sale_transaction_id"] = int(sale_id)
        item_result["status"] = "fulfilled"
        any_fulfilled = True

        results["total_charged"] += float(quote["total_price"])
        results["items"].append(item_result)

    results["total_charged"] = round(results["total_charged"], 2)

    if any_fulfilled and any_rejected:
        results["status"] = "partial_fulfilled"
    elif any_fulfilled:
        results["status"] = "fulfilled"
    else:
        results["status"] = "rejected"

    return results

@tool
def financial_report(as_of_date: str) -> dict:
    """
    Return a financial report snapshot as of a given date.

    Args:
        as_of_date: Date in YYYY-MM-DD format.

    Returns:
        Dict containing cash_balance and inventory_value, etc.
    """
    return generate_financial_report(as_of_date)

@tool
def supplier_delivery_date(item_name: str, order_date: str) -> str:
    """
    Return supplier estimated delivery date for an item ordered on a given date.

    Args:
        item_name: Item name.
        order_date: Date in YYYY-MM-DD format.

    Returns:
        Delivery date string (YYYY-MM-DD).
    """
    item = resolve_item_name(item_name)
    return str(get_supplier_delivery_date(item, order_date))

@tool
def quote_history(query: str) -> str:
    """
    Search quote history and return matching results.

    Args:
        query: Search string (customer/job/event keywords).

    Returns:
        Text summary of matches.
    """
    return str(search_quote_history(query))

# Set up your agents and create an orchestration agent that will manage them.

#inventory agent
# ===== BOOKMARK: INVENTORY AGENT =====
inventory_model = OpenAIServerModel(model_id="gpt-4o-mini")
for t in [stock_level, inventory_snapshot, low_stock_items, inventory_table]:
    print(getattr(t, "__name__", str(t)), "->", type(t))
inventory_agent = ToolCallingAgent(
    tools=[stock_level, inventory_snapshot, low_stock_items, inventory_table],
    model=inventory_model,
    name="inventory_agent",
    description=(
        "You are the Inventory Agent for Munder Difflin. "
        "You answer questions about stock levels and inventory status. "
        "Use tools to compute exact stock as of a given date, and identify low-stock items."
    ),
)

#quoting agent
# ===== BOOKMARK: QUOTING AGENT =====
quote_model = OpenAIServerModel(model_id="gpt-4o-mini")

quoting_agent = ToolCallingAgent(
    tools=[get_quote_request, is_item_carried, get_unit_price, compute_quote],
    model=quote_model,
    name="quoting_agent",
    description=(
        "You are the Quoting Agent. You generate customer quotes using inventory availability "
        "and unit prices. Always check stock using tools, compute a clear total price, and provide "
        "a short explanation. If asked, save the quote to the database."
    ),
)

#ordering agent
# ===== BOOKMARK: ORDERING AGENT =====
order_model = OpenAIServerModel(model_id="gpt-4o-mini")

ordering_agent = ToolCallingAgent(
    tools=[place_sales_orders_batch, reorder_if_below_min],  # or just batch
    model=order_model,
    name="ordering_agent",
    description=(
        "You are the Ordering Agent. "
        "To place customer sales, ALWAYS use place_sales_orders_batch in a single call. "
        "Do NOT call other tools for pricing or stock. "
        "Only use reorder_if_below_min if explicitly asked to reorder inventory."
    )
)
# Orchestration agent
# ===== BOOKMARK: ORCHESTRATOR AGENT =====
orch_model = OpenAIServerModel(model_id="gpt-4o-mini")

orchestrator_agent = ToolCallingAgent(
    tools=[
        ask_inventory_agent,
        ask_quoting_agent,
        ask_ordering_agent,
        process_request,   # end-to-end: given quote request id, run pipeline
    ],
    model=orch_model,
    name="orchestrator_agent",
    description=(
        "You are the Orchestrator Agent. "
        "You coordinate the inventory, quoting, and ordering agents.\n"
        "Rules:\n"
        "1) If the user provides a quote request id (or asks to process a request), use process_request.\n"
        "2) If the user asks about stock / inventory, call ask_inventory_agent.\n"
        "3) If the user asks for a quote, call ask_quoting_agent.\n"
        "4) If the user asks to place an order or reorder stock, call ask_ordering_agent.\n"
        "Return a short, final response to the user."
    ),
)

# Run your test scenarios by writing them here. Make sure to keep track of them.

def run_test_scenarios():
    
    print("Initializing Database...")
    init_database(db_engine, seed=137)
    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request
        request_with_date = f"{row['request']} (Date of request: {request_date})"

        ############
        ############
        ############
        # USE YOUR MULTI AGENT SYSTEM TO HANDLE THE REQUEST
        ############
        ############
        ############

        # response = call_your_multi_agent_system(request_with_date)
        response = orchestrator_agent.run(
            f"Handle this customer request end-to-end.\n"
            f"Request date: {request_date}\n"
            f"Request: {row['request']}"
        )
        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": response,
            }
        )

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()
