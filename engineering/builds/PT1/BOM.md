# Longshot PT1 BOM and Cost Notes

This page records the ordered PT1 prototype materials where supplier quote/order data is available.

## Battery cells

Source: redacted Alibaba receipt `L_001.pdf` shared by Julius in `#project-longshot-general` on 2026-06-11.

| Field | Value |
| --- | --- |
| Supplier | Shenzhen Vapcell Technology Co., Ltd. |
| Marketplace | Alibaba.com |
| Ordered cell | BAK 21700 65E cylindrical Li-ion cell |
| Listing description | New Arrivals Battery 2026 Brand BAK 21700 65E 6500mAh Cylindrical Lithium Ion Batteries 25A 3.6V for Ebike Drones |
| Nominal capacity | 6500mAh |
| Nominal voltage | 3.6V |
| Continuous discharge rating | 25A |
| PT1 pack configuration | 14S 9P |
| Cells used in pack | 126 |
| Cells ordered | 140 |
| Spare/overage cells | 14 |

### Cell order cost

Receipt currency: EUR. Contract currency shown on receipt: USD.

| Cost item | EUR | USD |
| --- | ---: | ---: |
| Cell subtotal, 140 pcs | €662.17 | — |
| Shipping | €145.13 | — |
| Logistics insurance | €24.22 | — |
| Order total before payment fee | €831.51 | $951.10 |
| Payment processing fee | €24.88 | — |
| Amount paid / landed order total | €856.39 | $979.55 |

Per ordered cell landed cost: **€6.12/cell** (about **$7.00/cell**, using the receipt totals).

Allocated to the 126 cells installed in the 14S 9P PT1 pack: **€770.75** (about **$881.60**).

The remaining 14 cells represent **€85.64** (about **$97.96**) of spares/overage from the order.

### Cell selection rationale

The BAK 65E cells were relatively expensive for this PT1 order, but Julius selected them because they were in stock and close to the best-performing 21700 cells available at order time. Julius initially tried to source Reliance RH60 cells, which were around $3/cell, but those were only available at the end of June.

Julius shared the following 10A discharge comparison, measured as energy delivered to 2.8V:

| Cell | Energy to 2.8V at 10A |
| --- | ---: |
| BAK 65E | 20.18Wh |
| Reliance RS60 | 19.25Wh |
| Linkdata 60P | 18.69Wh |
| Reliance RH60 | 18.56Wh |
| FEB 21700G (58E) | 18.53Wh |
| Vapcell F63 | 18.19Wh |
| Amprius INR21700/65 (SA112) | 18.16Wh |
| EVE 58E | 17.88Wh |
| Vapcell F60 | 17.86Wh |
| Samsung 58E | 17.56Wh |
| LG M58T | 17.22Wh |

## Copper busbars

Source: redacted Supro Manufacturing quotation shared by Julius in `#project-longshot-general` on 2026-06-11. Detailed quote and per-part breakdown are in [`design/copper-busbars/order-copper-longshot-pt1/`](design/copper-busbars/order-copper-longshot-pt1/).

| Cost basis | USD |
| --- | ---: |
| One-prototype parts subtotal from required PT1 quantities | $75.90 |
| One-prototype delivered estimate with shipping spread over 3 batteries | $108.57 |
| Simple quoted-order allocation including spares/overage, $443.50 / 3 | $147.83 |

## Current known PT1 material cost

These totals include only the ordered cells and copper busbars documented above. They do not include PCBs, printed/structural parts, enclosure hardware, connectors, labor, or tooling.

| Cost basis | Known PT1 material cost |
| --- | ---: |
| Installed cells + busbar delivered estimate | about $990.17 |
| Full cell order + busbar simple allocation including spares/overage | about $1,127.38 |

Keep currencies explicit when adding new line items; use the supplier receipt currency first and add converted totals only when the source document provides an exchange rate or USD total.
