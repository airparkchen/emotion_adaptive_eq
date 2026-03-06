# EQ Tree Snapshot

## Band Mapping
b1:200.0Hz, b2:280.0Hz, b3:400.0Hz, b4:550.0Hz, b5:770.0Hz, b6:1000.0Hz, b7:2000.0Hz, b8:4000.0Hz, b9:8000.0Hz, b10:16000.0Hz

## Tree
- `root` (stage=root, candidates=12)
  - presets: HF_enhance, HLF_cut, LF_enhance, bright_monitor, harman, lo-fi, mid_cut, mid_focus, mid_presence, mid_warm, v_shape, vocal_enhance
  - `high:boost` (stage=coarse, candidates=4)
    - presets: HF_enhance, bright_monitor, mid_cut, v_shape
    - delta: b8(4000.0Hz) +4.7dB, b9(8000.0Hz) +4.7dB, b10(16000.0Hz) +4.7dB
    - `b3_4:+2.0` (stage=medium, candidates=1)
      - presets: v_shape
      - delta: b3(400.0Hz) +1.5dB, b4(550.0Hz) +1.5dB
    - `b3_4:+0.0` (stage=medium, candidates=1)
      - presets: mid_cut
      - delta: b3(400.0Hz) +0.2dB, b4(550.0Hz) +0.2dB
    - `b3_4:-2.0` (stage=medium, candidates=2)
      - presets: HF_enhance, bright_monitor
      - delta: b3(400.0Hz) -1.4dB, b4(550.0Hz) -1.4dB
      - `b1:-2.0` (stage=fine, candidates=1)
        - presets: HF_enhance
        - delta: b1(200.0Hz) -2.0dB
      - `b1:-3.0` (stage=fine, candidates=1)
        - presets: bright_monitor
        - delta: b1(200.0Hz) -3.0dB
  - `high:neutral` (stage=coarse, candidates=4)
    - presets: HLF_cut, LF_enhance, harman, mid_presence
    - delta: b8(4000.0Hz) -0.5dB, b9(8000.0Hz) -0.5dB, b10(16000.0Hz) -0.5dB
    - `b5_6:+4.0` (stage=medium, candidates=1)
      - presets: mid_presence
      - delta: b5(770.0Hz) +3.8dB, b6(1000.0Hz) +3.8dB
    - `b5_6:+0.0` (stage=medium, candidates=1)
      - presets: LF_enhance
      - delta: b5(770.0Hz) +0.5dB, b6(1000.0Hz) +0.5dB
    - `b5_6:-4.0` (stage=medium, candidates=1)
      - presets: HLF_cut
      - delta: b5(770.0Hz) -5.0dB, b6(1000.0Hz) -5.0dB
    - `b5_6:-6.0` (stage=medium, candidates=1)
      - presets: harman
      - delta: b5(770.0Hz) -5.2dB, b6(1000.0Hz) -5.2dB
  - `high:cut` (stage=coarse, candidates=4)
    - presets: lo-fi, mid_focus, mid_warm, vocal_enhance
    - delta: b8(4000.0Hz) -1.8dB, b9(8000.0Hz) -1.8dB, b10(16000.0Hz) -1.8dB
    - `b1_2:+4.0` (stage=medium, candidates=1)
      - presets: lo-fi
      - delta: b1(200.0Hz) +3.2dB, b2(280.0Hz) +3.2dB
    - `b1_2:+2.0` (stage=medium, candidates=1)
      - presets: mid_warm
      - delta: b1(200.0Hz) +2.4dB, b2(280.0Hz) +2.4dB
    - `b1_2:-2.0` (stage=medium, candidates=1)
      - presets: vocal_enhance
      - delta: b1(200.0Hz) -1.8dB, b2(280.0Hz) -1.8dB
    - `b1_2:-4.0` (stage=medium, candidates=1)
      - presets: mid_focus
      - delta: b1(200.0Hz) -3.2dB, b2(280.0Hz) -3.2dB
