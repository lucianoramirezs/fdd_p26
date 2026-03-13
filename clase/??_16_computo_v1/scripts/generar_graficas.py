"""
generar_graficas.py
Genera todas las imágenes del módulo 16 de computo.
Requiere: matplotlib, numpy, pandas

Uso:
  python3 clase/16_computo/scripts/generar_graficas.py

Las imágenes se guardan en:
  clase/16_computo/images/
  clase/16_computo/scripts/results/  (intermedios)
"""

import os
import csv
import math
from pathlib import Path

# Intenta importar dependencias y avisa si faltan
try:
    import matplotlib
    matplotlib.use("Agg")  # sin display
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError as e:
    raise SystemExit(f"Falta dependencia: {e}. Instala con: pip install matplotlib numpy")

# Directorios
SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
IMAGES_DIR = SCRIPT_DIR.parent / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Tema Eva01
BG       = "#1a1a2e"
FG       = "#e0e0e0"
ACCENT1  = "#7b2d8b"   # violeta
ACCENT2  = "#00a8cc"   # cian
ACCENT3  = "#e94560"   # rojo coral
ACCENT4  = "#f5a623"   # naranja
ACCENT5  = "#43b581"   # verde
GRID_CLR = "#2a2a4e"

def apply_theme(fig, ax_list):
    """Aplica tema Eva01 a figura y lista de axes."""
    fig.patch.set_facecolor(BG)
    for ax in ax_list:
        ax.set_facecolor(BG)
        ax.tick_params(colors=FG, labelsize=9)
        ax.xaxis.label.set_color(FG)
        ax.yaxis.label.set_color(FG)
        ax.title.set_color(FG)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_CLR)
        ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.7)


# ─────────────────────────────────────────────────────────────────────────────
# 1. gantt_sequential.png
# ─────────────────────────────────────────────────────────────────────────────
def plot_gantt_sequential():
    fig, ax = plt.subplots(figsize=(10, 3))
    apply_theme(fig, [ax])

    tasks = [
        # (name, exec_intervals, wait_intervals, y)
        ("τ₁ (I/O-bound)", [(0, 0.5), (2.0, 2.2)], [(0.5, 2.0)], 2),
        ("τ₂ (CPU-bound)", [(2.2, 4.0)], [], 1),
        ("τ₃ (I/O-bound)", [(4.0, 4.2), (6.5, 6.7)], [(4.2, 6.5)], 0),
    ]

    h = 0.5
    for name, execs, waits, y in tasks:
        for (s, e) in execs:
            ax.barh(y, e - s, left=s, height=h, color=ACCENT2, alpha=0.9, linewidth=0)
        for (s, e) in waits:
            ax.barh(y, e - s, left=s, height=h, color=ACCENT1, alpha=0.5, linewidth=0,
                    hatch="///", edgecolor=FG)
        ax.text(-0.05, y, name, ha="right", va="center", color=FG, fontsize=9)

    ax.set_xlim(-0.1, 7.5)
    ax.set_ylim(-0.5, 2.8)
    ax.set_xlabel("Tiempo (s)", color=FG)
    ax.set_title("M1 — Secuencial: Gantt con periodos idle", color=FG, fontsize=11)
    ax.set_yticks([])

    exec_patch = mpatches.Patch(color=ACCENT2, alpha=0.9, label="exec(τᵢ) — CPU activa")
    wait_patch = mpatches.Patch(color=ACCENT1, alpha=0.5, hatch="///",
                                label="wait(τᵢ) — CPU idle (I/O)")
    ax.legend(handles=[exec_patch, wait_patch], facecolor=BG, labelcolor=FG,
              fontsize=8, loc="upper right")

    fig.tight_layout()
    out = IMAGES_DIR / "gantt_sequential.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. gantt_modelos.png  (M1–M4 comparados)
# ─────────────────────────────────────────────────────────────────────────────
def plot_gantt_modelos():
    """
    Muestra los 4 primeros modelos con el mismo conjunto de 3 tareas I/O-bound.
    Tarea: exec=0.3s, wait=1.2s, exec=0.2s (total=1.7s por tarea)
    """
    fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
    apply_theme(fig, axes)

    E, W = 0.3, 1.2  # exec duration, wait duration
    tasks_base = [(0, E, E + W, E + W + 0.2)]  # (start_exec1, end_exec1, start_exec2, end_exec2)

    def bar(ax, y, s, e, color, alpha=0.9, hatch=None):
        ax.barh(y, e - s, left=s, height=0.5, color=color, alpha=alpha,
                linewidth=0, hatch=hatch, edgecolor=FG if hatch else None)

    labels = ["τ₁", "τ₂", "τ₃"]
    offsets_m1 = [0, 1.7, 3.4]  # secuencial: una tras otra

    # M1 — Secuencial
    ax = axes[0]
    for i, (y, off) in enumerate(zip([2, 1, 0], offsets_m1)):
        bar(ax, y, off, off + E, ACCENT2)
        bar(ax, y, off + E, off + E + W, ACCENT1, 0.4, "///")
        bar(ax, y, off + E + W, off + E + W + 0.2, ACCENT2)
        ax.text(-0.05, y, labels[i], ha="right", va="center", color=FG, fontsize=9)
    ax.set_title("M1 — Secuencial (exec ∩ wait = ∅, sin solapamiento)", color=FG, fontsize=9)
    ax.set_yticks([])

    # M2 — Async no concurrent (await secuencial)
    ax = axes[1]
    for i, (y, off) in enumerate(zip([2, 1, 0], offsets_m1)):
        bar(ax, y, off, off + E, ACCENT2)
        bar(ax, y, off + E, off + E + W, ACCENT1, 0.4, "///")
        bar(ax, y, off + E + W, off + E + W + 0.2, ACCENT2)
        ax.text(-0.05, y, labels[i], ha="right", va="center", color=FG, fontsize=9)
    ax.set_title("M2 — Async no concurrent: await secuencial = M1 (esperas sin explotar)", color=FG, fontsize=9)
    ax.set_yticks([])

    # M3 — Concurrent no async (time-slicing CPU-bound, P=1)
    ax = axes[2]
    q = 0.25  # quantum
    T_total = 4.2
    colors3 = [ACCENT2, ACCENT3, ACCENT4]
    for i, (y, color) in enumerate(zip([2, 1, 0], colors3)):
        t = i * q
        while t < T_total:
            bar(ax, y, t + i * 0.003, t + q - 0.01 + i * 0.003, color, 0.85)
            t += 3 * q  # cada N hilos, cada uno recibe un quantum
        ax.text(-0.05, y, labels[i], ha="right", va="center", color=FG, fontsize=9)
    ax.set_title("M3 — Concurrent no async: time-slicing CPU-bound (GIL → sin speedup)", color=FG, fontsize=9)
    ax.set_yticks([])

    # M4 — Concurrent + async (event loop)
    ax = axes[3]
    # τ₁ inicia primero; τ₂ y τ₃ se intercalan durante sus waits
    start_times = [0, 0, 0]  # todas se crean juntas con gather
    for i, (y, st) in enumerate(zip([2, 1, 0], [0, 0.31, 0.62])):
        bar(ax, y, st, st + E, [ACCENT2, ACCENT3, ACCENT4][i])
        bar(ax, y, st + E, st + E + W, ACCENT1, 0.3, "///")
        bar(ax, y, st + E + W, st + E + W + 0.2, [ACCENT2, ACCENT3, ACCENT4][i])
        ax.text(-0.05, y, labels[i], ha="right", va="center", color=FG, fontsize=9)
    ax.set_title("M4 — Concurrent + async: exec(τⱼ) ∩ wait(τᵢ) ≠ ∅ (event loop explota esperas)", color=FG, fontsize=9)
    ax.set_yticks([])

    for ax in axes:
        ax.set_xlim(-0.1, 5.5)
        ax.set_ylim(-0.5, 2.8)

    axes[-1].set_xlabel("Tiempo (s)", color=FG)

    exec_patch = mpatches.Patch(color=ACCENT2, alpha=0.9, label="exec(τᵢ)")
    wait_patch = mpatches.Patch(color=ACCENT1, alpha=0.4, hatch="///", label="wait(τᵢ) — I/O")
    axes[0].legend(handles=[exec_patch, wait_patch], facecolor=BG, labelcolor=FG,
                   fontsize=8, loc="upper right")

    fig.suptitle("Modelos M1–M4: el mismo conjunto de tareas, distinto comportamiento",
                 color=FG, fontsize=11, y=1.01)
    fig.tight_layout()
    out = IMAGES_DIR / "gantt_modelos.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. event_loop_trace.png
# ─────────────────────────────────────────────────────────────────────────────
def plot_event_loop_trace():
    fig, ax = plt.subplots(figsize=(10, 3.5))
    apply_theme(fig, [ax])

    # Traza de 3 coroutines con el event loop
    # timeline: qué coroutine está activa en cada momento
    events = [
        # (t_start, t_end, coroutine_id, type)  type: exec o wait
        (0.00, 0.10, 1, "exec"),
        (0.10, 1.40, 1, "wait"),
        (0.10, 0.20, 2, "exec"),
        (0.20, 1.50, 2, "wait"),
        (0.20, 0.30, 3, "exec"),
        (0.30, 1.60, 3, "wait"),
        (1.40, 1.55, 1, "exec"),
        (1.50, 1.65, 2, "exec"),
        (1.60, 1.75, 3, "exec"),
    ]

    colors_exec = {1: ACCENT2, 2: ACCENT3, 3: ACCENT4}
    ys = {1: 2, 2: 1, 3: 0}

    for (ts, te, cid, typ) in events:
        y = ys[cid]
        color = colors_exec[cid] if typ == "exec" else ACCENT1
        alpha = 0.9 if typ == "exec" else 0.35
        hatch = None if typ == "exec" else "///"
        ax.barh(y, te - ts, left=ts, height=0.45, color=color, alpha=alpha,
                linewidth=0, hatch=hatch, edgecolor=FG if hatch else None)

    for cid, y in ys.items():
        ax.text(-0.02, y, f"coro {cid}", ha="right", va="center", color=FG, fontsize=9)

    # Marcar puntos de transferencia
    for t in [0.10, 0.20, 0.30, 1.40, 1.50, 1.60]:
        ax.axvline(t, color=FG, alpha=0.2, linewidth=0.8, linestyle=":")

    ax.set_xlim(-0.05, 1.9)
    ax.set_ylim(-0.5, 2.7)
    ax.set_xlabel("Tiempo (s)", color=FG)
    ax.set_title("Event Loop — traza temporal: qué coroutine ejecuta en cada instante", color=FG, fontsize=10)
    ax.set_yticks([])

    exec_patch = mpatches.Patch(color=ACCENT2, alpha=0.9, label="exec(τᵢ)")
    wait_patch = mpatches.Patch(color=ACCENT1, alpha=0.35, hatch="///", label="wait(τᵢ) — GIL liberado")
    ax.legend(handles=[exec_patch, wait_patch], facecolor=BG, labelcolor=FG, fontsize=8)

    fig.tight_layout()
    out = IMAGES_DIR / "event_loop_trace.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. amdahl_speedup.png
# ─────────────────────────────────────────────────────────────────────────────
def plot_amdahl():
    fig, ax = plt.subplots(figsize=(8, 5))
    apply_theme(fig, [ax])

    P = np.linspace(1, 16, 200)
    s_values = [0.1, 0.25, 0.5, 0.9]
    colors_th = [ACCENT2, ACCENT4, ACCENT3, ACCENT5]

    for s, color in zip(s_values, colors_th):
        speedup = 1 / (s + (1 - s) / P)
        ax.plot(P, speedup, color=color, linewidth=2, label=f"S={s} (máx {1/s:.1f}×)")
        ax.axhline(1 / s, color=color, linewidth=0.8, linestyle="--", alpha=0.4)

    # Puntos medidos del CSV
    measured = {1: 0.93, 2: 1.80, 4: 3.34, 8: 4.52}  # n_workers -> speedup (multiprocessing)
    p_vals = list(measured.keys())
    sp_vals = list(measured.values())
    ax.scatter(p_vals, sp_vals, color=FG, zorder=5, s=50, label="Medido (ProcessPoolExecutor)")

    ax.set_xlabel("Número de cores (P)", color=FG)
    ax.set_ylabel("Speedup", color=FG)
    ax.set_title("Ley de Amdahl: Speedup(P) = 1 / (S + (1−S)/P)", color=FG, fontsize=11)
    ax.set_xlim(1, 16)
    ax.set_ylim(0.5, 11)
    ax.legend(facecolor=BG, labelcolor=FG, fontsize=8)

    # Anotación del overhead
    ax.annotate("Los puntos medidos quedan\nbajo la curva S=0.1 por\noverhead de serialización",
                xy=(8, 4.52), xytext=(9.5, 3.0),
                color=FG, fontsize=8,
                arrowprops=dict(arrowstyle="->", color=FG, lw=0.8))

    fig.tight_layout()
    out = IMAGES_DIR / "amdahl_speedup.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. benchmark_io_bound.png
# ─────────────────────────────────────────────────────────────────────────────
def read_csv(path):
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def plot_benchmark_io():
    rows = read_csv(RESULTS_DIR / "io_bound_benchmark.csv")
    methods = ["sequential", "asyncio", "threading"]
    colors = {"sequential": ACCENT1, "asyncio": ACCENT2, "threading": ACCENT4}

    data = {m: {"n": [], "speedup": []} for m in methods}
    for row in rows:
        m = row["method"]
        data[m]["n"].append(int(row["n_tasks"]))
        data[m]["speedup"].append(float(row["speedup"]))

    fig, ax = plt.subplots(figsize=(8, 5))
    apply_theme(fig, [ax])

    for method in methods:
        ax.plot(data[method]["n"], data[method]["speedup"],
                color=colors[method], marker="o", markersize=5, linewidth=2,
                label=method)

    # Línea ideal
    ns = sorted(data["sequential"]["n"])
    ax.plot(ns, ns, color=FG, linewidth=1, linestyle="--", alpha=0.4, label="ideal (N×)")

    ax.set_xlabel("N tareas I/O-bound (cada una: sleep 1s)", color=FG)
    ax.set_ylabel("Speedup vs secuencial", color=FG)
    ax.set_title("I/O-bound: asyncio y threading escalan ~N, secuencial no", color=FG, fontsize=10)
    ax.legend(facecolor=BG, labelcolor=FG, fontsize=9)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)

    fig.tight_layout()
    out = IMAGES_DIR / "benchmark_io_bound.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. benchmark_cpu_bound.png
# ─────────────────────────────────────────────────────────────────────────────
def plot_benchmark_cpu():
    rows = read_csv(RESULTS_DIR / "cpu_bound_benchmark.csv")
    methods = ["threading", "multiprocessing", "joblib"]
    colors = {"threading": ACCENT3, "multiprocessing": ACCENT2, "joblib": ACCENT5}

    data = {m: {"n": [], "speedup": []} for m in methods}
    for row in rows:
        m = row["method"]
        if m == "sequential":
            continue
        data[m]["n"].append(int(row["n_workers"]))
        data[m]["speedup"].append(float(row["speedup"]))

    fig, ax = plt.subplots(figsize=(8, 5))
    apply_theme(fig, [ax])

    for method in methods:
        ax.plot(data[method]["n"], data[method]["speedup"],
                color=colors[method], marker="o", markersize=5, linewidth=2,
                label=method)

    # Ideal
    ns = [1, 2, 4, 8]
    ax.plot(ns, ns, color=FG, linewidth=1, linestyle="--", alpha=0.4, label="ideal (P×)")
    ax.axhline(1.0, color=ACCENT1, linewidth=1, linestyle=":", alpha=0.6, label="threading (GIL ~1×)")

    ax.set_xlabel("N workers", color=FG)
    ax.set_ylabel("Speedup vs secuencial", color=FG)
    ax.set_title("CPU-bound: multiprocessing/joblib escalan, threading se queda en ~1× (GIL)", color=FG, fontsize=10)
    ax.legend(facecolor=BG, labelcolor=FG, fontsize=9)

    fig.tight_layout()
    out = IMAGES_DIR / "benchmark_cpu_bound.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. pool_size_vs_throughput.png
# ─────────────────────────────────────────────────────────────────────────────
def plot_pool_size():
    rows = read_csv(RESULTS_DIR / "pool_size_benchmark.csv")

    cpu_n, cpu_t = [], []
    io_n, io_t = [], []
    for row in rows:
        n = int(row["n_workers"])
        t = float(row["throughput_tasks_per_sec"])
        if row["method"] == "cpu_bound":
            cpu_n.append(n)
            cpu_t.append(t)
        else:
            io_n.append(n)
            io_t.append(t)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    apply_theme(fig, [ax1, ax2])

    ax1.plot(cpu_n, cpu_t, color=ACCENT2, marker="o", markersize=5, linewidth=2)
    ax1.axvline(8, color=ACCENT3, linewidth=1.5, linestyle="--", alpha=0.8,
                label="os.cpu_count()=8")
    ax1.set_xlabel("Pool size (workers)", color=FG)
    ax1.set_ylabel("Throughput (tareas/s)", color=FG)
    ax1.set_title("CPU-bound: óptimo en os.cpu_count()", color=FG, fontsize=10)
    ax1.legend(facecolor=BG, labelcolor=FG, fontsize=8)

    ax2.plot(io_n, io_t, color=ACCENT4, marker="o", markersize=5, linewidth=2)
    ax2.set_xlabel("Pool size (workers / coroutines)", color=FG)
    ax2.set_ylabel("Throughput (tareas/s)", color=FG)
    ax2.set_title("I/O-bound: escala mucho más allá de cpu_count()", color=FG, fontsize=10)
    ax2.set_xscale("log", base=2)

    fig.suptitle("Pool size vs Throughput: CPU-bound tiene óptimo, I/O-bound escala más",
                 color=FG, fontsize=10)
    fig.tight_layout()
    out = IMAGES_DIR / "pool_size_vs_throughput.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generando imágenes en: {IMAGES_DIR}")
    plot_gantt_sequential()
    plot_gantt_modelos()
    plot_event_loop_trace()
    plot_amdahl()
    plot_benchmark_io()
    plot_benchmark_cpu()
    plot_pool_size()
    print("\nListo. Verifica las imágenes en clase/16_computo/images/")
