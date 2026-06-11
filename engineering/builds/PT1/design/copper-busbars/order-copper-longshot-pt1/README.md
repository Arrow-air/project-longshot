# Longshot PT1 Copper Busbar Order

These DXF files are the locked copper busbar designs for the Longshot PT1 build. Julius marked these parts as ordered on 2026-06-11, so this directory is intended to preserve the exact manufacturing/order geometry used for PT1.

## Contents

| File | Qty | Copper thickness | SHA-256 |
| --- | ---: | --- | --- |
| `10X_0.2mm_copper_PW-BUS-001-N_Terminal.dxf` | 10 | 0.2mm | `970ad2e5a983f069d3ff543b70fd3756b3dd4cc0a46865a815befa38f23c7237` |
| `10X_0.2mm_copper_PW-BUS-002-P_Terminal.dxf` | 10 | 0.2mm | `a7c3b03e964ea35fc89ada2bd65f9c2f5140897dc5ea4c5303841f19a1deef13` |
| `40X_0.2mm_copper_PW-BUS-003-Bridge_1.dxf` | 40 | 0.2mm | `f8d6f4bbec5d25a08af1b8afe2b8f208ac60896fad28136cf3f5e82c3edbb539` |
| `5X_0.2mm_copper_PW-BUS-004-Bridge_2.dxf` | 5 | 0.2mm | `4fa45a2d4734e6f5ba65785158b096da8a2e360971641d4d2286237f4f1c7a4f` |
| `5X_6mm_copper_PW-BUS-005-Screw_Terminal_Negative.dxf` | 5 | 6mm | `cd6a26158be28e358cc48663c9117fa22360210fa504df3a6daa502f0b72ee06` |
| `5X_6mm_copper_PW-BUS-006-Screw_Terminal_Positive.dxf` | 5 | 6mm | `47d5d5a4e84d7aa15a8e09ab287292bbfa5e6b20095b28e57c7b768a735ce261` |

## Supplier quotation

Source: redacted Supro Manufacturing quotation shared by Julius in `#project-longshot-general` on 2026-06-11.

Price term: DDU by air. Currency: USD. Validity: 15 days from quotation date.

| Quoted file / service | Quoted material | Quoted qty | Unit price | Line total |
| --- | --- | ---: | ---: | ---: |
| `5X_0.2mm_copper_PW-BUS-004-Bridge_2.dxf` | Brass H62 | 5 | $6.80 | $34.00 |
| `5X_6mm_copper_PW-BUS-005-Screw_Terminal_Negative.dxf` | Copper C101 | 5 | $11.30 | $56.50 |
| `5X_6mm_copper_PW-BUS-006-Screw_Terminal_Positive.dxf` | Copper C101 | 5 | $10.20 | $51.00 |
| `10X_0.2mm_copper_PW-BUS-001-N_Terminal.dxf` | Brass H62 | 10 | $3.40 | $34.00 |
| `10X_0.2mm_copper_PW-BUS-002-P_Terminal.dxf` | Brass H62 | 10 | $3.40 | $34.00 |
| `40X_0.2mm_copper_PW-BUS-003-Bridge_1.dxf` | Brass H62 | 40 | $3.40 | $136.00 |
| Shipping | — | — | — | $98.00 |

Quoted parts subtotal: $345.50. Quoted total with shipping: $443.50.

## Per-prototype busbar estimate

Julius noted the quoted order is material for approximately three batteries. One prototype battery needs:

| Part | Prototype qty | Quoted unit price | Prototype line cost |
| --- | ---: | ---: | ---: |
| `PW-BUS-001-N_Terminal.dxf` | 1 | $3.40 | $3.40 |
| `PW-BUS-002-P_Terminal.dxf` | 1 | $3.40 | $3.40 |
| `PW-BUS-003-Bridge_1.dxf` | 12 | $3.40 | $40.80 |
| `PW-BUS-004-Bridge_2.dxf` | 1 | $6.80 | $6.80 |
| `PW-BUS-005-Screw_Terminal_Negative.dxf` | 1 | $11.30 | $11.30 |
| `PW-BUS-006-Screw_Terminal_Positive.dxf` | 1 | $10.20 | $10.20 |

Estimated per-prototype parts subtotal: $75.90.

With shipping spread over three prototype batteries, estimated per-prototype delivered cost is $108.57.

For a simple order-total allocation, $443.50 divided by three batteries is $147.83 per battery, including the extra quoted spares/overage.

## Notes

- Source files: Discord upload `Order_Copper_Longshot_PT1.7z` from Julius in `#project-longshot-general`.
- Source quotation: Discord upload `Supro_Quotation_geschwarzt.pdf` from Julius in `#project-longshot-general`.
- Files are stored unpacked instead of as a compressed archive so they can be reviewed and versioned directly in GitHub.
- Treat these as PT1 build record artifacts. Future copper revisions should go in a new revision/build directory rather than modifying these files in place.
