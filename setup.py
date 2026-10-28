"""Day 1 실습 재료 만들기: python setup.py
- bss.db   : 통신사 BSS를 흉내 낸 SQLite DB (고객·상품·가입·청구)
- app.log  : 셸(grep·pipe) 연습용 가상 로그
모두 가상 데이터입니다. 표준 라이브러리만 씁니다.
"""
import random, sqlite3, datetime as dt, os

random.seed(42)
if os.path.exists("bss.db"):
    os.remove("bss.db")
con = sqlite3.connect("bss.db")
cur = con.cursor()
cur.executescript("""
CREATE TABLE customer (
  cust_id   INTEGER PRIMARY KEY,
  name      TEXT,
  cust_type TEXT,      -- 개인 / 법인
  status    TEXT,      -- ACTIVE / SUSPENDED / TERMINATED
  join_date TEXT
);
CREATE TABLE product (
  prod_code TEXT PRIMARY KEY,
  prod_name TEXT,
  category  TEXT,      -- 5G / LTE / 인터넷
  monthly_fee INTEGER,
  on_sale   INTEGER    -- 1 판매중 / 0 판매중지
);
CREATE TABLE subscription (
  sub_id    INTEGER PRIMARY KEY,
  cust_id   INTEGER REFERENCES customer(cust_id),
  prod_code TEXT REFERENCES product(prod_code),
  sub_status TEXT,     -- 개통완료 / 개통대기 / 해지
  sub_date  TEXT,
  open_date TEXT       -- 개통일 (대기면 NULL)
);
CREATE TABLE bill (
  bill_id   INTEGER PRIMARY KEY,
  sub_id    INTEGER REFERENCES subscription(sub_id),
  bill_month TEXT,
  amount    INTEGER,
  paid      INTEGER    -- 1 납부 / 0 미납
);
""")
products = [
    ("5GP", "5G 프리미엄", "5G", 89000, 1),
    ("5GS", "5G 슬림", "5G", 55000, 1),
    ("5GY", "5G Y틴", "5G", 47000, 0),
    ("LTE1", "LTE 데이터ON", "LTE", 49000, 1),
    ("LTE2", "LTE 표준", "LTE", 33000, 0),
    ("NET5", "인터넷 500M", "인터넷", 38500, 1),
    ("NET1", "인터넷 1G", "인터넷", 44000, 1),
]
cur.executemany("INSERT INTO product VALUES (?,?,?,?,?)", products)

last = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
first = ["민준", "서연", "도윤", "하은", "지호", "수아", "예준", "지우", "현우", "서윤"]
base = dt.date(2023, 1, 1)
customers = []
for i in range(1, 61):
    ctype = "법인" if i % 7 == 0 else "개인"
    name = (f"(주)케이{i:02d}상사" if ctype == "법인"
            else random.choice(last) + random.choice(first))
    status = random.choices(["ACTIVE", "SUSPENDED", "TERMINATED"], [80, 10, 10])[0]
    jd = base + dt.timedelta(days=random.randint(0, 1000))
    customers.append((i, name, ctype, status, jd.isoformat()))
cur.executemany("INSERT INTO customer VALUES (?,?,?,?,?)", customers)

subs, sid = [], 1
for c in customers:
    if c[0] % 13 == 0:          # 가입이 하나도 없는 고객 (LEFT JOIN 연습용)
        continue
    for _ in range(random.choice([1, 1, 2, 3])):
        p = random.choice(products)
        sd = dt.date.fromisoformat(c[4]) + dt.timedelta(days=random.randint(0, 200))
        st = random.choices(["개통완료", "개통대기", "해지"], [75, 12, 13])[0]
        od = None if st == "개통대기" else (sd + dt.timedelta(days=random.randint(0, 5))).isoformat()
        subs.append((sid, c[0], p[0], st, sd.isoformat(), od))
        sid += 1
cur.executemany("INSERT INTO subscription VALUES (?,?,?,?,?,?)", subs)

bills, bid = [], 1
fee = {p[0]: p[3] for p in products}
for s in subs:
    if s[3] != "개통완료":
        continue
    for m in ["2026-07", "2026-08", "2026-09"]:
        paid = 0 if random.random() < 0.08 else 1
        bills.append((bid, s[0], m, fee[s[2]], paid))
        bid += 1
cur.executemany("INSERT INTO bill VALUES (?,?,?,?,?)", bills)
con.commit()
con.close()

# 셸 연습용 로그
levels = ["INFO"] * 14 + ["WARN"] * 4 + ["ERROR"] * 2
msgs = {
    "INFO": ["개통 요청 수신", "청구 배치 완료", "고객 조회 성공", "요금제 변경 처리"],
    "WARN": ["응답 지연 3000ms 초과", "재시도 1회", "캐시 미스"],
    "ERROR": ["DB 연결 실패 ORA-12541", "개통 실패 code=RF09", "청구 금액 음수 감지"],
}
svcs = ["order-svc", "billing-svc", "crm-svc"]
t = dt.datetime(2026, 10, 27, 9, 0, 0)
with open("app.log", "w", encoding="utf-8") as f:
    for _ in range(300):
        t += dt.timedelta(seconds=random.randint(1, 120))
        lv = random.choice(levels)
        f.write(f"{t:%Y-%m-%d %H:%M:%S} {lv:<5} [{random.choice(svcs)}] "
                f"{random.choice(msgs[lv])} cust_id={random.randint(1,60)}\n")

print(f"bss.db 생성: 고객 {len(customers)} · 상품 {len(products)} · 가입 {len(subs)} · 청구 {len(bills)}")
print("app.log 생성: 300줄")