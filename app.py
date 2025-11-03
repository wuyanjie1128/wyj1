import streamlit as st
import matplotlib.pyplot as plt
import random
import numpy as np

# ----------------------------------------------------------
# 1) Color palette
# ----------------------------------------------------------
def mixed_palette(k=10, seed=None,
                  pastel_ratio=0.65,
                  hue_spread_pastel=0.09, s_pastel=(0.18, 0.35), v_pastel=(0.90, 0.98),
                  hue_spread_vivid=1.00, s_vivid=(0.70, 1.00), v_vivid=(0.85, 1.00)):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    def hsv_to_rgb(h, s, v):
        i = int(h * 6) % 6
        f = h * 6 - int(h * 6)
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        if i == 0: r, g, b = v, t, p
        elif i == 1: r, g, b = q, v, p
        elif i == 2: r, g, b = p, v, t
        elif i == 3: r, g, b = p, q, v
        elif i == 4: r, g, b = t, p, v
        else:        r, g, b = v, p, q
        return (r, g, b)

    colors = []
    base_h = random.random()
    n_pastel = max(1, int(round(k * pastel_ratio)))
    for _ in range(n_pastel):
        h = (base_h + random.uniform(-hue_spread_pastel, hue_spread_pastel)) % 1.0
        s = random.uniform(*s_pastel)
        v = random.uniform(*v_pastel)
        colors.append(hsv_to_rgb(h, s, v))

    n_vivid = k - n_pastel
    for _ in range(n_vivid):
        h = random.random()
        if random.random() < 0.35:
            h = (base_h + 0.5 + random.uniform(-0.08, 0.08)) % 1.0
        s = random.uniform(*s_vivid)
        v = random.uniform(*v_vivid)
        colors.append(hsv_to_rgb(h, s, v))

    random.shuffle(colors)
    return colors

# ----------------------------------------------------------
# 2) Blob geometry
# ----------------------------------------------------------
def make_blob_outline(center=(0, 0), radius=1.0, wobble=0.2, points=220):
    cx, cy = center
    theta = np.linspace(0, 2*np.pi, points, endpoint=False)
    coarse_step = 10
    coarse_idx = np.arange(0, points, coarse_step)
    coarse_vals = np.random.uniform(-1, 1, size=len(coarse_idx) + 1)
    coarse_idx = np.append(coarse_idx, points)
    noise = np.interp(np.arange(points), coarse_idx, coarse_vals)
    r = radius * (1 + wobble * 0.5 * noise)
    x = cx + r * np.cos(theta)
    y = cy + r * np.sin(theta)
    return x, y

# ----------------------------------------------------------
# 3) Draw one blob
# ----------------------------------------------------------
def draw_blob_with_style(ax, center, radius, wobble, fill_rgba,
                         soft_edge=True, edge=True, inner_lines=True,
                         halo_layers=3, halo_spread=0.10, halo_alpha=0.16,
                         edge_color=(0,0,0,0.25), edge_width=0.9,
                         line_count=4, line_gap=0.14, line_alpha=0.25, line_width=0.8):
    if soft_edge:
        for i in range(halo_layers, 0, -1):
            t = i / halo_layers
            rr = radius * (1 + halo_spread * t)
            xh, yh = make_blob_outline(center=center, radius=rr, wobble=wobble*0.85)
            ax.fill(xh, yh, color=(fill_rgba[0], fill_rgba[1], fill_rgba[2], halo_alpha * (t*0.7)),
                    edgecolor=(0,0,0,0))
    xb, yb = make_blob_outline(center=center, radius=radius, wobble=wobble)
    ax.fill(xb, yb, color=fill_rgba, edgecolor=(0,0,0,0))
    if edge:
        ax.plot(xb, yb, color=edge_color, linewidth=edge_width)
    if inner_lines and line_count > 0:
        for k in range(1, line_count + 1):
            rr = radius * (1 - line_gap * k)
            if rr <= radius * 0.25:
                break
            xi, yi = make_blob_outline(center=center, radius=rr, wobble=wobble*0.9)
            ax.plot(xi, yi, color=(0,0,0,line_alpha), linewidth=line_width)

# ----------------------------------------------------------
# 4) Main poster generation
# ----------------------------------------------------------
def generate_poster(seed=42, n_layers=9, wobble_min=0.12, wobble_max=0.28):
    random.seed(seed)
    np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(7, 10), dpi=200)
    ax.axis('off')
    ax.set_aspect('equal')
    ax.set_facecolor((0.98, 0.98, 0.97))

    x_range = (-1.0, 3.0)
    y_range = (-0.5, 2.5)
    ax.set_xlim(*x_range)
    ax.set_ylim(*y_range)
    SAFE = dict(xmin=-1.0, xmax=0.8, ymin=1.6, ymax=2.5)
    def in_safe(cx, cy, r):
        pad = r * 1.05
        return (SAFE['xmin']-pad <= cx <= SAFE['xmax']+pad) and \
               (SAFE['ymin']-pad <= cy <= SAFE['ymax']+pad)

    palette = mixed_palette(k=max(12, n_layers+3), seed=seed)
    alphas = np.linspace(0.50, 0.85, n_layers)
    radius_min, radius_max = 0.38, 0.56
    centers = []
    for _ in range(n_layers):
        for _ in range(60):
            cx = random.uniform(*x_range)
            cy = random.uniform(*y_range)
            r  = random.uniform(radius_min, radius_max)
            if not in_safe(cx, cy, r):
                centers.append((cx, cy, r))
                break

    for i, (cx, cy, rad) in enumerate(centers):
        wobble = random.uniform(wobble_min, wobble_max)
        r, g, b = palette[i % len(palette)]
        fill_rgba = (r, g, b, float(alphas[i]))
        outline_col = (0, 0, 0, 0.28)
        line_alpha = 0.22
        draw_blob_with_style(ax, center=(cx, cy), radius=rad, wobble=wobble, fill_rgba=fill_rgba,
                             soft_edge=True, edge=True, inner_lines=True,
                             halo_layers=2, halo_spread=0.08, halo_alpha=0.14,
                             edge_color=outline_col, edge_width=0.9,
                             line_count=4, line_gap=0.15, line_alpha=line_alpha, line_width=0.8)

    ax.text(0.05, 0.95, "Generative Poster", fontsize=16, weight='bold',
            transform=ax.transAxes, color=(0.10, 0.10, 0.12))
    ax.text(0.05, 0.91, "Week 2 • Arts & Advanced Big Data", fontsize=10,
            transform=ax.transAxes, color=(0.22, 0.22, 0.28))
    return fig

# ----------------------------------------------------------
# 5) Streamlit UI
# ----------------------------------------------------------
st.set_page_config(page_title="🎨 Generative Abstract Poster", layout="centered")
st.title("🎨 Generative Abstract Poster")
st.write("使用滑块与输入调整参数，然后生成具有线条感与丰富色彩的抽象艺术海报。")

col1, col2 = st.columns(2)
with col1:
    seed = st.number_input("Seed (随机种子)", min_value=0, max_value=9999, value=42, step=1)
    n_layers = st.slider("层数 (n_layers)", 3, 15, 9)
with col2:
    wobble_min = st.slider("最小波动 (wobble_min)", 0.05, 0.25, 0.12)
    wobble_max = st.slider("最大波动 (wobble_max)", 0.15, 0.45, 0.28)

if st.button("生成海报"):
    fig = generate_poster(seed=seed, n_layers=n_layers,
                          wobble_min=wobble_min, wobble_max=wobble_max)
    st.pyplot(fig)
    st.success("✅ 海报已生成！可右键保存或截图。")
