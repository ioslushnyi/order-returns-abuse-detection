import pandas as pd
import random
import uuid
from datetime import timedelta
import time

def generate_returns(orders, users, products, duplicates=1000, output_path="../data/returns.csv"):
    start = time.time()
    random.seed(42)

    users = pd.read_csv("../data/users.csv")
    orders = pd.read_csv("../data/orders.csv")
    products = pd.read_csv("../data/products.csv")

    # Abuse simulation
    abusive_users = users.sample(frac=0.02, random_state=42)["user_id"].tolist()

    # Inject high-return SKUs (~10%)
    high_return_skus = products.sample(frac=0.1, random_state=99)["sku"].tolist()

    returns = []

    sampled_orders = orders.sample(frac=0.3, random_state=42)

    abusive_reasons = ["no reason", "", None, "didn't work", " hate it", "wrong item", "IDK"]
    normal_reasons = ["too small", "didn't match", "changed mind", "not needed", "wrong size", "delayed"]

    for order in sampled_orders.itertuples(index=False):
        order_date = pd.to_datetime(order.order_date)
        is_abuser = order.user_id in abusive_users
        is_high_return_sku = order.sku in high_return_skus

        # Probability of return based on user type and SKU type
        if is_abuser and is_high_return_sku:
            return_probability = 0.95
        elif is_abuser:
            return_probability = 0.75
        elif is_high_return_sku:
            return_probability = 0.5
        else:
            return_probability = 0.1
        
        # Randomly decide to skip some returns to simulate realistic data
        if random.random() > return_probability:
            continue

        return_days = random.randint(1, 3) if is_abuser else random.randint(5, 30)
        reason = random.choice(abusive_reasons if is_abuser else normal_reasons)

        is_fraud = int(is_abuser and (reason in abusive_reasons or return_days <= 3))

        returns.append({
            "return_id": str(uuid.uuid4()),
            "order_id": order.order_id,
            "user_id": order.user_id,
            "sku": order.sku,
            "return_reason": reason,
            "return_date": order_date + timedelta(days=return_days),
            "is_fraud": is_fraud,
        })

    # Add 1,000 dirty duplicates
    returns += random.sample(returns, duplicates)

    df = pd.DataFrame(returns)
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} returns with {len(abusive_users)} abusive users and {len(high_return_skus)} high-return SKUs and with {sum(df['is_fraud'])} labeled as fraud.")

    end = time.time()
    elapsed = end - start
    print(f"Elapsed time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    generate_returns()
