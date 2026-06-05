import os
import json

BASE_DIR   = "."
INDEX_FILE = "index.html"

LANG_EXTENSIONS = {
    "py":   ".py",
    "java": ".java",
    "cs":   ".cs",
    "cpp":  ".cpp",
}

def find_lang_files(folder_path):
    """Scan folder and find any file matching each language extension."""
    files_in_folder = os.listdir(folder_path)
    langs = {}
    for key, ext in LANG_EXTENSIONS.items():
        match = next((f for f in files_in_folder if f.endswith(ext)), None)
        if match:
            langs[key] = os.path.join(folder_path, match).replace("\\", "/")
        else:
            langs[key] = None
    return langs

def find_pdf(folder_path):
    """Find any .pdf file in the folder."""
    files_in_folder = os.listdir(folder_path)
    match = next((f for f in files_in_folder if f.endswith(".pdf")), None)
    if match:
        return os.path.join(folder_path, match).replace("\\", "/")
    return None

def scan_all_problems():
    problems = []
    if not os.path.exists(BASE_DIR):
        print(f"Folder '{BASE_DIR}' not found. Make sure you run this from your repo root.")
        return problems

    for folder in sorted(os.listdir(BASE_DIR)):
        folder_path = os.path.join(BASE_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        info_path = os.path.join(folder_path, "info.json")
        if not os.path.exists(info_path):
            print(f"  Skipping {folder}/ — no info.json found")
            continue

        with open(info_path, "r", encoding="utf-8") as f:
            info = json.load(f)

        langs = find_lang_files(folder_path)
        pdf   = find_pdf(folder_path)

        any_done = any(v is not None for v in langs.values()) or pdf is not None
        status = "Done" if any_done else "Todo"

        problems.append({
            "id":     info.get("id"),
            "name":   info.get("name"),
            "diff":   info.get("difficulty"),
            "topics": info.get("topics", []),
            "langs":  langs,
            "pdf":    pdf,
            "status": status,
        })

        langs_done = sum(1 for v in langs.values() if v)
        print(f"  [{status:4s}] #{info.get('id'):4d} {info.get('name')} — {langs_done}/4 languages, PDF: {'yes' if pdf else 'no'}")

    return problems


def build_html(problems_data):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LeetCode Tracker</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.44.0/tabler-icons.min.css">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f9f9f7; color: #1a1a1a; padding: 2rem; }}
    h1 {{ font-size: 22px; font-weight: 500; margin-bottom: 4px; }}
    .subtitle {{ font-size: 13px; color: #888; margin-bottom: 1.5rem; }}
    .stats {{ display: flex; gap: 10px; margin-bottom: 1rem; flex-wrap: wrap; }}
    .stat {{ background: #fff; border: 0.5px solid #e0dfd8; border-radius: 8px; padding: 10px 18px; text-align: center; min-width: 80px; }}
    .stat-num {{ font-size: 22px; font-weight: 500; }}
    .stat-label {{ font-size: 11px; color: #888; margin-top: 2px; }}
    .progress-bar {{ height: 4px; background: #f0efe8; border-radius: 2px; margin-bottom: 1.5rem; }}
    .progress-fill {{ height: 100%; background: #0F6E56; border-radius: 2px; transition: width .3s; }}
    .filters {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 1.5rem; }}
    .filter-group {{ display: flex; flex-direction: column; gap: 4px; }}
    .filter-group label {{ font-size: 12px; color: #888; }}
    select, input[type=text] {{ font-size: 13px; padding: 7px 10px; border-radius: 8px; border: 0.5px solid #ccc; background: #fff; color: #1a1a1a; outline: none; }}
    select:focus, input:focus {{ border-color: #888; }}
    input[type=text] {{ min-width: 200px; }}
    select {{ min-width: 150px; }}
    .table-wrap {{ background: #fff; border-radius: 12px; border: 0.5px solid #e0dfd8; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; min-width: 700px; }}
    th {{ text-align: left; font-weight: 500; font-size: 12px; color: #888; border-bottom: 0.5px solid #e0dfd8; padding: 10px 14px; }}
    td {{ padding: 10px 14px; border-bottom: 0.5px solid #f0efe8; vertical-align: middle; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #fafaf8; }}
    .badge {{ display: inline-block; font-size: 11px; font-weight: 500; padding: 2px 9px; border-radius: 99px; }}
    .easy   {{ background: #EAF3DE; color: #3B6D11; }}
    .medium {{ background: #FAEEDA; color: #854F0B; }}
    .hard   {{ background: #FCEBEB; color: #A32D2D; }}
    .done   {{ background: #E1F5EE; color: #0F6E56; }}
    .todo   {{ background: #F1EFE8; color: #5F5E5A; }}
    .topic-tag {{ display: inline-block; font-size: 11px; background: #EEEDFE; color: #3C3489; border-radius: 99px; padding: 2px 7px; margin: 1px 2px; }}
    .lang-links {{ display: flex; flex-wrap: wrap; gap: 4px; }}
    .lang-link {{ font-size: 11px; font-weight: 500; padding: 2px 9px; border-radius: 99px; border: 0.5px solid; text-decoration: none; }}
    .lang-py   {{ background: #E6F1FB; color: #185FA5; border-color: #85B7EB; }}
    .lang-java {{ background: #FAEEDA; color: #854F0B; border-color: #EF9F27; }}
    .lang-cs   {{ background: #EEEDFE; color: #534AB7; border-color: #AFA9EC; }}
    .lang-cpp  {{ background: #EAF3DE; color: #3B6D11; border-color: #97C459; }}
    .lang-missing {{ background: #f5f5f3; color: #aaa; border-color: #ddd; }}
    .pdf-link {{ font-size: 11px; font-weight: 500; padding: 2px 9px; border-radius: 99px; background: #FAECE7; color: #993C1D; border: 0.5px solid #F0997B; text-decoration: none; display: inline-flex; align-items: center; gap: 3px; }}
    .pdf-link:hover {{ background: #F5C4B3; }}
    .no-results {{ text-align: center; padding: 3rem; color: #888; font-size: 14px; }}
    .num {{ color: #aaa; font-size: 12px; }}
    .empty-state {{ text-align: center; padding: 4rem 2rem; color: #aaa; }}
    .empty-state p {{ font-size: 14px; margin-top: 8px; }}
  </style>
</head>
<body>
  <h1>LeetCode Tracker</h1>
  <p class="subtitle">Auto-generated by update.py &mdash; run it before pushing to keep this in sync.</p>

  <div class="stats" id="stats"></div>
  <div class="progress-bar"><div class="progress-fill" id="progress"></div></div>

  <div class="filters">
    <div class="filter-group">
      <label>Search</label>
      <input type="text" id="search" placeholder="Problem name or number..." oninput="render()">
    </div>
    <div class="filter-group">
      <label>Difficulty</label>
      <select id="diff" onchange="render()">
        <option value="">All difficulties</option>
        <option>Easy</option><option>Medium</option><option>Hard</option>
      </select>
    </div>
    <div class="filter-group">
      <label>Topic</label>
      <select id="topic" onchange="render()"><option value="">All topics</option></select>
    </div>
    <div class="filter-group">
      <label>Status</label>
      <select id="status" onchange="render()">
        <option value="">All</option>
        <option>Done</option><option>Todo</option>
      </select>
    </div>
    <div class="filter-group">
      <label>Language</label>
      <select id="lang" onchange="render()">
        <option value="">All languages</option>
        <option value="py">Python</option>
        <option value="java">Java</option>
        <option value="cs">C#</option>
        <option value="cpp">C++</option>
      </select>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th><th>Problem</th><th>Difficulty</th>
          <th>Topics</th><th>Solutions</th><th>Notes</th><th>Status</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <div id="no-results" class="no-results" style="display:none">No problems match your filters.</div>
    <div id="empty-state" class="empty-state" style="display:none">
      <b>No problems yet.</b>
      <p>Create a folder inside <code>Leetcode/</code> with an <code>info.json</code>, then run <code>python update.py</code>.</p>
    </div>
  </div>

  <script>
    const problems = {json.dumps(problems_data, indent=2)};

    const langMeta = {{
      py:   {{ label: "Python", cls: "lang-py" }},
      java: {{ label: "Java",   cls: "lang-java" }},
      cs:   {{ label: "C#",     cls: "lang-cs" }},
      cpp:  {{ label: "C++",    cls: "lang-cpp" }},
    }};

    const allTopics = [...new Set(problems.flatMap(p => p.topics))].sort();
    const topicSel = document.getElementById("topic");
    allTopics.forEach(t => {{
      const o = document.createElement("option");
      o.value = t; o.textContent = t; topicSel.appendChild(o);
    }});

    if (problems.length === 0) {{
      document.getElementById("empty-state").style.display = "block";
    }}

    function langBadges(langs) {{
      return Object.entries(langMeta).map(([key, meta]) => {{
        const path = langs[key];
        if (path) return `<a class="lang-link ${{meta.cls}}" href="${{path}}">${{meta.label}}</a>`;
        return `<span class="lang-link lang-missing">${{meta.label}}</span>`;
      }}).join("");
    }}

    function render() {{
      const q = document.getElementById("search").value.toLowerCase();
      const d = document.getElementById("diff").value;
      const t = document.getElementById("topic").value;
      const s = document.getElementById("status").value;
      const l = document.getElementById("lang").value;

      const filtered = problems.filter(p =>
        (!q || p.name.toLowerCase().includes(q) || String(p.id).includes(q)) &&
        (!d || p.diff === d) &&
        (!t || p.topics.includes(t)) &&
        (!s || p.status === s) &&
        (!l || p.langs[l])
      );

      document.getElementById("tbody").innerHTML = filtered.map(p => `
        <tr>
          <td class="num">${{p.id}}</td>
          <td style="font-weight:500">${{p.name}}</td>
          <td><span class="badge ${{p.diff.toLowerCase()}}">${{p.diff}}</span></td>
          <td>${{p.topics.map(t => `<span class="topic-tag">${{t}}</span>`).join("")}}</td>
          <td><div class="lang-links">${{langBadges(p.langs)}}</div></td>
          <td>${{p.pdf
            ? `<a class="pdf-link" href="${{p.pdf}}"><i class="ti ti-file" aria-hidden="true"></i>PDF</a>`
            : `<span style="color:#ccc">—</span>`}}</td>
          <td><span class="badge ${{p.status.toLowerCase()}}">${{p.status}}</span></td>
        </tr>
      `).join("");

      document.getElementById("no-results").style.display =
        (filtered.length === 0 && problems.length > 0) ? "block" : "none";

      const done  = problems.filter(p => p.status === "Done").length;
      const total = problems.length;
      const withPdf = problems.filter(p => p.pdf).length;
      document.getElementById("progress").style.width =
        total > 0 ? Math.round(done / total * 100) + "%" : "0%";
      document.getElementById("stats").innerHTML = `
        <div class="stat"><div class="stat-num">${{total}}</div><div class="stat-label">Total</div></div>
        <div class="stat"><div class="stat-num" style="color:#0F6E56">${{done}}</div><div class="stat-label">Done</div></div>
        <div class="stat"><div class="stat-num" style="color:#854F0B">${{total - done}}</div><div class="stat-label">Todo</div></div>
        <div class="stat"><div class="stat-num" style="color:#993C1D">${{withPdf}}</div><div class="stat-label">With notes</div></div>
        <div class="stat"><div class="stat-num">${{filtered.length}}</div><div class="stat-label">Showing</div></div>
      `;
    }}
    render();
  </script>
</body>
</html>"""


def main():
    print(f"Scanning {BASE_DIR}/...")
    problems = scan_all_problems()

    html = build_html(problems)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    done  = sum(1 for p in problems if p["status"] == "Done")
    total = len(problems)
    print(f"\nDone! {done}/{total} problems completed.")
    print(f"index.html updated.")
    print(f"\nNext: git add . && git commit -m 'Update tracker' && git push origin main")


if __name__ == "__main__":
    main()
