"""
generar_graficas.py
Genera todas las imágenes del módulo 18 (Intro a APIs).

Requiere: matplotlib, numpy
Uso:
  python3 clase/18_intro_a_apis/scripts/generar_graficas.py

Las imágenes se guardan en:
  clase/18_intro_a_apis/images/
"""

from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError as e:
    raise SystemExit(f"Falta dependencia: {e}. Instala con: pip install matplotlib numpy")

SCRIPT_DIR = Path(__file__).parent
IMAGES_DIR = SCRIPT_DIR.parent / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ── Tema Eva01 ────────────────────────────────────────────────────────────────
BG       = "#1a1a2e"
FG       = "#e0e0e0"
ACCENT1  = "#7b2d8b"   # violeta
ACCENT2  = "#00a8cc"   # cian
ACCENT3  = "#e94560"   # rojo coral
ACCENT4  = "#f5a623"   # naranja
ACCENT5  = "#43b581"   # verde
ACCENT6  = "#a855f7"   # púrpura claro
GRID_CLR = "#2a2a4e"

PALETTE = [ACCENT2, ACCENT5, ACCENT3, ACCENT4, ACCENT1, ACCENT6]


# ── Helpers ───────────────────────────────────────────────────────────────────
def apply_theme(fig, ax_list):
    """Aplica el tema Eva01 a la figura y ejes."""
    fig.patch.set_facecolor(BG)
    for ax in ax_list:
        ax.set_facecolor(BG)
        ax.tick_params(colors=FG, labelsize=10)
        ax.xaxis.label.set_color(FG)
        ax.yaxis.label.set_color(FG)
        ax.title.set_color(FG)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_CLR)


def save(fig, name):
    """Guarda la figura como PNG."""
    out = IMAGES_DIR / name
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out}")


# ── 1. Payload por paradigma ─────────────────────────────────────────────────
def gen_bench_payload():
    print("Generando bench_payload.png ...")

    paradigmas = ["REST/JSON", "GraphQL", "gRPC/Protobuf", "SOAP/XML"]
    payloads   = [480, 320, 82, 850]
    colores    = [ACCENT2, ACCENT5, ACCENT3, ACCENT4]

    fig, ax = plt.subplots(figsize=(10, 6))
    apply_theme(fig, [ax])

    bars = ax.bar(paradigmas, payloads, color=colores, width=0.55, edgecolor=BG,
                  linewidth=1.2)

    # Etiquetas sobre cada barra
    for bar, val in zip(bars, payloads):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 15,
                f"{val} B", ha="center", va="bottom", color=FG, fontsize=12,
                fontweight="bold")

    ax.set_ylabel("Bytes", fontsize=12)
    ax.set_title("Tamaño de payload por paradigma (misma operación)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_ylim(0, max(payloads) * 1.15)
    ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.5, axis="y")

    plt.tight_layout()
    save(fig, "bench_payload.png")


# ── 2. Latencia por paradigma ────────────────────────────────────────────────
def gen_bench_latencia():
    print("Generando bench_latencia.png ...")

    paradigmas = ["REST", "GraphQL", "gRPC", "WebSocket\n(mensaje)", "SSE\n(evento)", "SOAP"]
    latencias  = [50, 60, 5, 1, 5, 100]
    colores    = [ACCENT2, ACCENT5, ACCENT3, ACCENT4, ACCENT1, ACCENT6]

    fig, ax = plt.subplots(figsize=(10, 6))
    apply_theme(fig, [ax])

    bars = ax.barh(paradigmas, latencias, color=colores, height=0.55,
                   edgecolor=BG, linewidth=1.2)

    # Etiquetas al lado de cada barra
    for bar, val in zip(bars, latencias):
        ax.text(bar.get_width() + max(latencias) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{val} ms", ha="left", va="center", color=FG, fontsize=11,
                fontweight="bold")

    ax.set_xlabel("Latencia (ms)", fontsize=12)
    ax.set_title("Latencia típica por paradigma",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlim(0, max(latencias) * 1.25)
    ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.5, axis="x")
    ax.invert_yaxis()

    plt.tight_layout()
    save(fig, "bench_latencia.png")


# ── 3. Comparación multi-eje ─────────────────────────────────────────────────
def gen_comparacion_paradigmas():
    print("Generando comparacion_paradigmas.png ...")

    ejes = ["Simplicidad", "Rendimiento", "Flexibilidad", "Tiempo real"]
    paradigmas = {
        "REST":      [9, 6, 5, 3],
        "GraphQL":   [5, 5, 9, 3],
        "gRPC":      [4, 9, 4, 6],
        "WebSocket": [5, 8, 5, 10],
        "SOAP":      [2, 3, 6, 1],
    }

    x = np.arange(len(ejes))
    n = len(paradigmas)
    width = 0.15
    colores = [ACCENT2, ACCENT5, ACCENT3, ACCENT4, ACCENT6]

    fig, ax = plt.subplots(figsize=(10, 6))
    apply_theme(fig, [ax])

    for i, (nombre, valores) in enumerate(paradigmas.items()):
        offset = (i - n / 2 + 0.5) * width
        bars = ax.bar(x + offset, valores, width, label=nombre,
                      color=colores[i], edgecolor=BG, linewidth=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(ejes, fontsize=11)
    ax.set_ylabel("Puntuación (1–10)", fontsize=12)
    ax.set_title("Comparación de paradigmas API",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_ylim(0, 11)
    ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.5, axis="y")
    ax.legend(loc="upper right", fontsize=9, facecolor=BG, edgecolor=GRID_CLR,
              labelcolor=FG)

    plt.tight_layout()
    save(fig, "comparacion_paradigmas.png")


# ── 4. Timeline HTTP ─────────────────────────────────────────────────────────
def gen_timeline_http():
    print("Generando timeline_http.png ...")

    eventos = [
        (1991, "HTTP/0.9"),
        (1996, "HTTP/1.0"),
        (1997, "HTTP/1.1"),
        (1998, "XML-RPC"),
        (1999, "SOAP"),
        (2000, "REST\n(tesis Fielding)"),
        (2005, "AJAX / Web 2.0"),
        (2011, "WebSocket\n(RFC 6455)"),
        (2012, "GraphQL\n(Facebook interno)"),
        (2015, "HTTP/2, gRPC,\nGraphQL público"),
        (2022, "HTTP/3"),
    ]

    years  = [e[0] for e in eventos]
    labels = [e[1] for e in eventos]

    fig, ax = plt.subplots(figsize=(12, 4))
    apply_theme(fig, [ax])

    # Linea base
    ax.plot([min(years) - 1, max(years) + 1], [0, 0], color=GRID_CLR,
            linewidth=2, zorder=1)

    # Alternar etiquetas arriba y abajo para evitar solapamiento
    offsets = [1, -1] * (len(eventos) // 2) + [1] * (len(eventos) % 2)

    for i, (year, label) in enumerate(eventos):
        direction = offsets[i]
        color = PALETTE[i % len(PALETTE)]

        # Marcador
        ax.scatter(year, 0, s=60, color=color, zorder=3, edgecolors=FG,
                   linewidths=0.8)
        # Linea vertical
        ax.plot([year, year], [0, direction * 0.4], color=color,
                linewidth=1.2, zorder=2)
        # Texto
        ax.text(year, direction * 0.55, f"{year}\n{label}",
                ha="center", va="bottom" if direction > 0 else "top",
                fontsize=8, color=FG, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=BG,
                          edgecolor=color, alpha=0.9))

    ax.set_title("Evolución de protocolos y paradigmas web",
                 fontsize=14, fontweight="bold", pad=15)

    # Limpiar ejes
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlim(min(years) - 3, max(years) + 3)
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    save(fig, "timeline_http.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"Directorio de imágenes: {IMAGES_DIR}\n")
    gen_bench_payload()
    gen_bench_latencia()
    gen_comparacion_paradigmas()
    gen_timeline_http()
    print("\nTodas las imágenes generadas correctamente.")


if __name__ == "__main__":
    main()
