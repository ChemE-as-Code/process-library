# Your section: S3c of ammonia-1
Branch: stage/basic-pids-loop (checked out). Earlier sections are merged on main.

## S3a / S3b / S3c P&IDs (branches stage/basic-pids-front, -mid, -loop)
Draft complete P&IDs (DEXPI 2.0.1, skills `pid-draft`, `pid-design-*`, `dexpi-xml`) from the
simulated PFD, `cheme validate` clean at error level, lists updated with every sheet:
- S3a (front): feed gas, desulphurisation, primary and secondary reforming, waste-heat recovery,
  HT/LT shift.
- S3b (mid): aMDEA CO2 removal, methanation, synthesis-gas compression.
- S3c (loop): synthesis loop, converter, refrigeration, ammonia separation and storage interface,
  purge-gas recovery, steam and BFW system and the main utilities headers.
Off-page connectors consistent across sheets; render and look at each sheet; gates pids-exist,
pids-valid, drawing-clean, process-basic, process-links.


Your part: **S3c (loop)** only; the other parts are separate sections.
