# mydocs

Documentation and analysis reports for photonic SerDes link characterisation.

## Repository Structure

```
mydocs/
├── colossus/                          # Colossus ASIC
│   ├── link/
│   │   ├── channel_characterization/  # Channel characterisation reports & figures
│   │   ├── receceiver/
│   │   ├── transceiver/
│   │   └── transmitter/
│   └── stab/
└── caribou/                           # Caribou ASIC (in progress)
    ├── link/
    │   ├── channel_characterization/
    │   ├── receceiver/
    │   ├── transceiver/
    │   └── transmitter/
    └── stab/
```

## Reports

- [Colossus Channel Characterisation](colossus/link/channel_characterization/report.md) — 212.5 Gb/s PAM4 optical SerDes link, pkctrl3 dataset
- [Colossus Channel Characterisation — 150 ns](colossus/link/channel_characterization/colossus_150ns/report.md) — 150 ns PRBS15, 6-sweep dataset
- [Ranjit Channel Characterisation](colossus/link/channel_characterization/ranjit/report.md) — PRBS12, 106 250 UI
- [Point 0007 Channel Characterisation](colossus/link/channel_characterization/point_0007_report.md) — point_0007 dataset
