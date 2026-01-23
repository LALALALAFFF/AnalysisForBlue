def apriori(transactions, min_support=0.2, min_confidence=0.5):
    """
    transactions: list of list，例如
        [
            ["A", "B", "C"],
            ["A", "C"],
            ["B", "C"],
        ]
    """

    # 1. 计算项集支持度
    def get_support(itemset):
        count = sum(1 for t in transactions if itemset.issubset(t))
        return count / len(transactions)

    # 2. 生成频繁1项集
    items = set()
    for t in transactions:
        items.update(t)
    items = [frozenset([i]) for i in items]

    L = []  # freq itemsets
    Lk = []

    # 处理 1 项集
    for item in items:
        support = get_support(item)
        if support >= min_support:
            Lk.append((item, support))
    L.append(Lk)

    # 3. 生成 k 项集
    while True:
        candidates = []
        prev_itemsets = [itemset for itemset, _ in Lk]

        # 连接生成候选
        for i in range(len(prev_itemsets)):
            for j in range(i + 1, len(prev_itemsets)):
                union = prev_itemsets[i] | prev_itemsets[j]
                if len(union) == len(prev_itemsets[0]) + 1:
                    candidates.append(union)

        # 去重
        candidates = list(set(candidates))

        Lk = []
        for c in candidates:
            support = get_support(c)
            if support >= min_support:
                Lk.append((c, support))

        if not Lk:
            break

        L.append(Lk)

    # 4. 生成关联规则
    rules = []
    for Lk in L:
        for itemset, support in Lk:
            if len(itemset) < 2:
                continue

            for a in itemset:
                A = frozenset([a])
                B = itemset - A
                conf = get_support(itemset) / get_support(A)

                if conf >= min_confidence:
                    rules.append({
                        "A": list(A),
                        "B": list(B),
                        "support": round(support, 4),
                        "confidence": round(conf, 4)
                    })

    return {
        "frequent_itemsets": [
            {
                "itemset": list(itemset),
                "support": support
            }
            for Lk in L
            for itemset, support in Lk
        ],
        "rules": rules
    }
