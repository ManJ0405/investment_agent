# Equity Research Notes

Learn to write one real note first. Then freeze the report structure. Then map each section to a tool. Do not design the agent module until one company note exists.

Regular review: after each new 10-K / 10-Q, update numbers and what changed. Do not reread the whole filing from scratch.

---

## Four questions a note must answer

1. What is the business? (how they make money, customers, segments)
2. What do the financials say? (growth, margins, cash, leverage — trend over years)
3. What is management doing, and what can go wrong? (strategy, capital allocation, risks)
4. What is the stock pricing in, and what is worth watching? (now vs a simple future case — not a buy/sell call)

Also write: what would change my mind.

For the assistant later: evidence + method + open questions. The user decides. No target price as advice.

---

## Draft report structure (freeze after the first handwritten note)

Use this when you write the first 10-K note. After that note, trim or rename sections before coding.

1. **Business** — what they sell, who pays, why they win or lose
2. **Financial snapshot** — 3-year table (revenue, GP, operating income, NI, OCF, capex, FCF, debt, equity, share count) + 4–5 ratios
3. **MD&A takeaways** — why results moved; what management says is next
4. **Risks that matter** — company-specific, not the generic legal list
5. **News / catalysts** — what changed after the filing date
6. **What to watch next** — 3–5 measurable items (margin, capex, a segment, a customer concentration)
7. **Valuation sanity (optional in v1)** — what the current price implies; one simple case. Label as practice.
8. **Sources** — 10-K items, statement period, news URLs

---

## 10-K: what to read, and in what order

SEC item names (US annual report):

| Order | Item | Why |
| --- | --- | --- |
| 1 | Item 1 Business | Model, segments, competition. Read the latest year in full. Skim prior years only for what changed (new segment, M&A, geography). |
| 2 | Item 8 — face statements | Income statement, balance sheet, cash flow. Build the 3-year table before reading the story. |
| 3 | Item 8 — notes | Revenue recognition, segments, debt, stock-based compensation, leases. Read notes that the statements or MD&A point to. |
| 4 | Item 7 MD&A | Why the year looked like that; liquidity; known trends. Compare to last year’s MD&A. |
| 5 | Item 1A Risk factors | Legal laundry list. Keep 3–5 that are specific to this company. Cross-check with MD&A. |
| Optional v1 | Item 7A, auditor opinion | Market risk; whether the audit is clean. |

10-Q is the quarterly update: statements + shorter MD&A + new risks. Use it between 10-Ks.

---

## First research: how to do one 10-K

Pick one US company you already ingest (e.g. NVDA). Work on paper / this folder, not in the agent. Link of NVDA (https://d18rn0p25nwr6d.cloudfront.net/CIK-0001045810/e361e58a-7483-44f5-bc62-a9080ae6ec72.pdf)

1. **Item 1 (60–90 min)**  
   Write 8–12 sentences: products, customers, segments, how revenue is earned, main cost lines, competition. If you cannot explain it without jargon, you do not understand it yet.

2. **Copy a 3-year table from Item 8 (45 min)**  
   Same lines every year so YoY is visible. Include share count (dilution).

3. **Compute ratios yourself (30 min)**  
   - Growth: revenue YoY  
   - Margins: gross, operating, net  
   - Cash: OCF, capex, FCF = OCF − capex (state this definition)  
   - Leverage: total debt, equity, net debt if you have cash; D/E as a description, not a pass/fail rule  
   - Quality: OCF vs net income (cash earning vs accounting earning)

4. **MD&A (45–60 min)**  
   For each big move in the table, write the reason management gives. Note what they say about next year. Separate fact from outlook.

5. **Item 1A filter (20 min)**  
   Drop generic risks (“stock price may be volatile”). Keep risks that would actually change the business (customer, product cycle, regulation, supply, litigation).

6. **Write the note with the eight sections above.**  
   Every claim about the business or numbers needs a source (item + year). If you cannot cite it, delete it.

7. **Optional: one valuation sanity check**  
   Example: price / earnings, or EV / revenue, vs growth. Write “this is what the market is paying,” not “fair value is X.”

Timebox the first pass to one weekend. Depth comes on the second read of the same company.

---

## Financial statements

Identity: **Assets = Liabilities + Stockholders’ equity**. The balance sheet is a snapshot on one date. Book value is not the market value of the company.

### Balance sheet

**Assets**  
 Resources the company controls (cash, receivables, inventory, PP&E, intangibles). Most items are recorded at historical cost or other accounting rules, not “what the firm is worth today.”

**Liabilities**  
 Obligations to others (payables, deferred revenue, debt). Borrowing can fund the business, but it is not an asset. It must be repaid or otherwise settled. Deferred revenue means cash arrived before the work was done.

**Stockholders’ equity**  
 Residual: assets minus liabilities on the books. It is the accounting claim of owners, not a promise of what you recover in bankruptcy. In a failure, equity is often worth little. For a going concern, you care more about future cash than liquidation math.

**Leverage**  
 Debt/equity (and net debt / EBITDA later) describes how the firm is financed. High D/E is normal in banks, utilities, some industrials; many software firms sit near zero. Do not screen “D/E > 1” or “< 1” as good/bad. Ask: can they service the debt from operating cash flow, and is the leverage typical for the industry?

### Income statement (over a period)

Order of the story:

1. **Revenue** — sales. Not profit.
2. **Cost of revenue (COGS)** → **Gross profit** = revenue − COGS. Gross margin = GP / revenue. Says how much is left after the direct cost of delivering the product.
3. **Operating expenses** (R&D, SG&A, etc.) → **Operating income** = gross profit − operating expenses (before interest and tax, on a standard presentation). If revenue rises while operating income falls, margins are compressing — find out why in MD&A.
4. **Interest, other, tax** → **Net income** — accounting profit after those items. This is the bottom of the income statement. It is also the usual starting line of the cash flow statement (indirect method). Net income is not cash.

Watch share count: net income can grow while earnings per share does not, if the company issues a lot of stock.

### Cash flow statement (over the same period)

Three buckets. They explain why cash on the balance sheet moved.

- **Operating (OCF)** — cash from running the business. Compare to net income. If NI is strong and OCF is weak, ask about working capital or one-offs.
- **Investing** — capex, acquisitions, purchases/sales of investments. Heavy capex can be growth or a treadmill; MD&A should say which.
- **Financing** — debt issued/repaid, dividends, buybacks, stock issuance.

**Free cash flow (simple definition for v1)**  
FCF ≈ OCF − capital expenditure.  
This is cash after spending to maintain/grow the operating asset base. It can go to cash on the balance sheet, debt reduction, dividends, or buybacks. It is not a dedicated “rainy day fund.” Always write the formula you used; people define FCF differently (some subtract only maintenance capex, some include M&A).

---

## After the first note (not before)

Only then map tools:

| Report section | Data you already have | Tool / job |
| --- | --- | --- |
| Business | RAG Item 1 chunks | Retrieve + cite; do not invent |
| Financial snapshot | Yahoo statements | Compute table + ratios in code |
| MD&A / risks | RAG Item 7 / 1A | Retrieve + cite |
| News | Yahoo headlines | Store titles/dates; do not count-only |
| What to watch | From the note template | LLM drafts from evidence only |
| Valuation | Price + statements | Optional later; never a buy/sell |

Until the handwritten NVDA (or chosen ticker) note exists, do not implement a new equity-research graph node.



My researach for 10-K (NVDA)
Item1:
Acclerated computing (GPU), it is data coentre for AI infra now. They have CUDA platform for their own GPU that is for developement as framework, software developement, algo, SDKs, APIs, etc.  It is used for AI model training (ML and DL), data analysis, scientific computing, robotics and 3D graphics. There are many developers using their ecosystem and platform, it can increase the value of the platform for their customers. Omniverse (software for physkical AI applications)

Their target market: Data Center, Gaming, Professional Visualization, and Automotive

Computing and Network segment; Graphics segment gaming and PC

For data center, the customer is cloud provider, AI model maker, enterprises and startups

Providing computing platform, and GPU to earn money

competitors: 
hardware-AMD, Huawai and Intel; 

customers:
cloud services- alibaba, Amazon, Baidu, etc

Summary

NDVA is a company that sell GPU, and computing and networking platforms and AI solutions and software, and Automotiveplatforms and autonomous and electric vehicle solutions including software. There are two segements, Computing and Network segment and Graphics segment. For GPU, it used in gamming, data analysis, scientific computing, robotics, 3D graphics and AI model training. For computing platform, they have Nvdia enterpise, which is a cloud solution for production grade AI applicaiton. There are four target market, Data Center, Gaming, Professional Visualization, and Automotive. Because of their acclerated computing and CUDA, these computing and networking platform and ecosystem increased the value of their products, also keep customer stay. Their main competitors are hardware-AMD, Huawai and Intel. Their main customers are PC user, AI company, model lab, data center, etc.
