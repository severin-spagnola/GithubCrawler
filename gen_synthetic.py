"""
Generate synthetic sensitivity_list and port_mismatch examples for Polaris-Classifier V5.
Uses claude-haiku-4-5-20251001.
"""
import os
import json
import time
import anthropic

API_KEY = "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"
OUTPUT_DIR = "/Users/severinspagnola/Desktop/GithubCrawler/training_data/examples"
MODEL = "claude-haiku-4-5-20251001"

client = anthropic.Anthropic(api_key=API_KEY)

SENSITIVITY_LIST_PROMPT = """Generate {n} diverse Verilog/SystemVerilog code examples showing sensitivity list bugs and their fixes.

Each example must have:
- before_code: Verilog/SystemVerilog with an incomplete sensitivity list bug
- after_code: The fixed version
- patch: unified diff string (--- a/file.v / +++ b/file.v format)

Sensitivity list bugs include:
- always @(a) should be always @(a or b or c) — missing combinational signals
- always @(clk) missing reset: should be always @(posedge clk or negedge rst_n)
- Using explicit sensitivity list instead of always @(*) or always_comb
- Missing data signals in combinational always block
- VHDL: process(a) missing b, should be process(a, b)

Make each example DIFFERENT: vary signal names, module names, bit widths (8-bit, 16-bit, 32-bit, 64-bit), logic complexity, coding style.

Return a JSON array of exactly {n} objects with these fields:
- patch: unified diff string (must start with --- a/ and +++ b/)
- before_code: full Verilog/VHDL code with the bug
- after_code: full Verilog/VHDL code fixed
- language: "verilog" or "vhdl"
- bug_category: "sensitivity_list"
- is_synthetic: true
- synthetic: true

Return ONLY the JSON array, no other text."""

PORT_MISMATCH_PROMPT = """Generate {n} diverse Verilog/SystemVerilog code examples showing port mismatch bugs and their fixes.

Each example must have:
- before_code: Verilog/SystemVerilog with a port mismatch bug
- after_code: The fixed version
- patch: unified diff string (--- a/file.v / +++ b/file.v format)

Port mismatch bugs include:
- Module instantiation uses wrong port name (e.g., .data_in when module has .din)
- Wrong port width in instantiation (connecting 8-bit wire to 16-bit port)
- Missing port in instantiation (forgot to connect a required port)
- Swapped input/output direction in module definition
- Extra/wrong ports in instantiation

Make each example DIFFERENT: vary module names, port names, bit widths (4-bit, 8-bit, 16-bit, 32-bit), logic complexity.

Return a JSON array of exactly {n} objects with these fields:
- patch: unified diff string (must start with --- a/ and +++ b/)
- before_code: full Verilog/SystemVerilog code with the bug
- after_code: full Verilog/SystemVerilog code fixed
- language: "verilog" or "systemverilog"
- bug_category: "port_mismatch"
- is_synthetic: true
- synthetic: true

Return ONLY the JSON array, no other text."""


def generate_batch(prompt_template, n=5, label="sensitivity_list", attempt=0):
    prompt = prompt_template.format(n=n)
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        text = msg.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3].rstrip()
        examples = json.loads(text)
        if not isinstance(examples, list):
            print(f"  [WARN] Response is not a list, skipping")
            return []
        return examples
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON parse error on batch: {e}")
        return []
    except anthropic.RateLimitError:
        print(f"  [WARN] Rate limit hit, sleeping 60s...")
        time.sleep(60)
        return []
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []


def save_example(example, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(example, f, indent=2)


def generate_sensitivity_list(total=200, batch_size=5):
    print(f"\n=== Generating {total} sensitivity_list examples ===")
    saved = 0
    batch_num = 0
    while saved < total:
        batch_num += 1
        remaining = total - saved
        n = min(batch_size, remaining)
        print(f"  Batch {batch_num}: requesting {n} examples (saved so far: {saved})")
        examples = generate_batch(SENSITIVITY_LIST_PROMPT, n=n, label="sensitivity_list")
        for ex in examples:
            if saved >= total:
                break
            # Ensure required fields
            ex["bug_category"] = "sensitivity_list"
            ex["is_synthetic"] = True
            ex["synthetic"] = True
            if "language" not in ex or not ex["language"]:
                ex["language"] = "verilog"
            filename = f"synth_sensitivity_list_{saved:04d}.json"
            save_example(ex, filename)
            saved += 1
        if not examples:
            print(f"  [WARN] Empty batch, retrying after 5s...")
            time.sleep(5)
        else:
            time.sleep(0.5)  # small delay to avoid rate limits
    print(f"  Done: saved {saved} sensitivity_list examples")
    return saved


def generate_port_mismatch(total=150, batch_size=5):
    print(f"\n=== Generating {total} port_mismatch examples ===")
    saved = 0
    batch_num = 0
    while saved < total:
        batch_num += 1
        remaining = total - saved
        n = min(batch_size, remaining)
        print(f"  Batch {batch_num}: requesting {n} examples (saved so far: {saved})")
        examples = generate_batch(PORT_MISMATCH_PROMPT, n=n, label="port_mismatch")
        for ex in examples:
            if saved >= total:
                break
            ex["bug_category"] = "port_mismatch"
            ex["is_synthetic"] = True
            ex["synthetic"] = True
            if "language" not in ex or not ex["language"]:
                ex["language"] = "verilog"
            filename = f"synth_port_mismatch_{saved:04d}.json"
            save_example(ex, filename)
            saved += 1
        if not examples:
            print(f"  [WARN] Empty batch, retrying after 5s...")
            time.sleep(5)
        else:
            time.sleep(0.5)
    print(f"  Done: saved {saved} port_mismatch examples")
    return saved


if __name__ == "__main__":
    sl_count = generate_sensitivity_list(total=200, batch_size=5)
    pm_count = generate_port_mismatch(total=150, batch_size=5)
    print(f"\n=== Generation complete ===")
    print(f"sensitivity_list: {sl_count}")
    print(f"port_mismatch: {pm_count}")
    print(f"Total new examples: {sl_count + pm_count}")
