from collections import defaultdict
from itertools import combinations

from player.models import ActionLog


# =====================================================
#  主函数：从 ActionLog 中读取 → Apriori → 返回结果
# =====================================================
def apriori(min_support=0.2, min_confidence=0.5):
    transactions = load_transactions_from_actionlog()

    frequent_itemsets, support_data = find_frequent_itemsets(
        transactions,
        min_support
    )

    rules = generate_rules(
        frequent_itemsets,
        support_data,
        min_confidence
    )

    return {
        "frequent_itemsets": frequent_itemsets,
        "rules": rules
    }


# =====================================================
#  Step 1: 从数据库读取事务
# =====================================================
def load_transactions_from_actionlog():
    """
    使用 session_id 分组，每个 session = 一条事务
    每个事务包含去重的 event_type
    """
    sessions = defaultdict(set)

    # 只关心 event_type
    queryset = ActionLog.objects.values("session_id", "event_type")

    for row in queryset:
        sid = row["session_id"]
        event = row["event_type"]
        sessions[sid].add(event)

    return list(sessions.values())


# =====================================================
#  Step 2: 生成频繁项集
# =====================================================
def find_frequent_itemsets(transactions, min_support):
    support_data = {}
    frequent_itemsets = []

    # 所有单项 C1
    C1 = set()
    for t in transactions:
        for item in t:
            C1.add(frozenset([item]))

    # L1
    L1, support_1 = filter_itemsets(C1, transactions, min_support)
    frequent_itemsets.extend(L1)
    support_data.update(support_1)

    k = 2
    Lk = L1

    # 继续生成更大的项集
    while Lk:
        Ck = generate_candidates(Lk, k)
        Lk, support_k = filter_itemsets(Ck, transactions, min_support)

        support_data.update(support_k)
        frequent_itemsets.extend(Lk)
        k += 1

    # 格式转换
    frequent_itemsets_output = [
        {"itemset": list(fs), "support": support_data[fs]}
        for fs in frequent_itemsets
    ]

    return frequent_itemsets_output, support_data


def filter_itemsets(candidates, transactions, min_support):
    counts = {c: 0 for c in candidates}
    total = len(transactions)

    for t in transactions:
        for c in candidates:
            if c.issubset(t):
                counts[c] += 1

    L = []
    support = {}

    for c in candidates:
        sup = counts[c] / total
        if sup >= min_support:
            L.append(c)
            support[c] = sup

    return L, support


def generate_candidates(Lk, k):
    Lk_list = list(Lk)
    candidates = []

    for i in range(len(Lk_list)):
        for j in range(i + 1, len(Lk_list)):
            a = sorted(list(Lk_list[i]))
            b = sorted(list(Lk_list[j]))

            if a[:k - 2] == b[:k - 2]:
                candidates.append(frozenset(Lk_list[i] | Lk_list[j]))

    return candidates


# =====================================================
#  Step 3: 生成关联规则
# =====================================================
def generate_rules(frequent_itemsets, support_data, min_confidence):
    rules = []

    for item in frequent_itemsets:
        items = item["itemset"]
        if len(items) < 2:
            continue

        itemset_f = frozenset(items)

        for i in range(1, len(items)):
            for A in combinations(items, i):
                A = frozenset(A)
                B = itemset_f - A

                conf = support_data[itemset_f] / support_data[A]
                if conf >= min_confidence:
                    rules.append({
                        "A": list(A),
                        "B": list(B),
                        "confidence": conf,
                        "support": support_data[itemset_f]
                    })

    return rules
