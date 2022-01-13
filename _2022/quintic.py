from manim_imports_ext import *


def roots_to_coefficients(roots):
    n = len(list(roots))
    return [
        ((-1)**(n - k)) * sum(
            np.prod(tup)
            for tup in it.combinations(roots, n - k)
        )
        for k in range(n)
    ] + [1]


def poly(x, coefs):
    return sum(coefs[k] * x**k for k in range(len(coefs)))


def dpoly(x, coefs):
    return sum(k * coefs[k] * x**(k - 1) for k in range(1, len(coefs)))


def find_root(func, dfunc, seed=complex(1, 1), tol=1e-8, max_steps=100):
    # Use newton's method
    last_seed = np.inf
    for n in range(max_steps):
        if abs(seed - last_seed) < tol:
            break
        last_seed = seed
        seed = seed - func(seed) / dfunc(seed)
    return seed


def coefficients_to_roots(coefs):
    # Find a root, divide out by (x - root), repeat
    roots = []
    for i in range(len(coefs) - 1):
        root = find_root(
            lambda x: poly(x, coefs),
            lambda x: dpoly(x, coefs),
        )
        roots.append(root)
        new_reversed_coefs, rem = np.polydiv(coefs[::-1], [1, -root])
        coefs = new_reversed_coefs[::-1]
    return roots


def get_nth_roots(z, n):
    base_root = z**(1 / n)
    return [
        base_root * np.exp(complex(0, k * TAU / n))
        for k in range(n)
    ]


def sort_to_minimize_distances(unordered_points, reference_points):
    """
    Sort the initial list of points in R^n so that the sum
    of the distances between corresponding points in both lists
    is smallest
    """
    ordered_points = []
    unused_points = list(unordered_points)

    for ref_point in reference_points:
        distances = [get_norm(ref_point - up) for up in unused_points]
        index = np.argmin(distances)
        ordered_points.append(unused_points.pop(index))
    return ordered_points


def optimal_transport(dots, target_points):
    """
    Move the dots to the target points such that each dot moves a minimal distance
    """
    points = sort_to_minimize_distances(target_points, [d.get_center() for d in dots])
    for dot, point in zip(dots, points):
        dot.move_to(point)
    return dots


def x_power_tex(power, base="x"):
    if power == 0:
        return ""
    elif power == 1:
        return base
    else:
        return f"{base}^{{{power}}}"


def poly_tex(coefs, prefix="P(x) = ", coef_color=MAROON_B):
    n = len(coefs) - 1
    coefs = [f"{{{coef}}}" for coef in coefs]
    terms = [prefix, x_power_tex(n)]
    for k in range(n - 1, -1, -1):
        coef = coefs[k]
        if not coef[1] == "-":
            terms.append("+")
        terms.append(str(coef))
        terms.append(x_power_tex(k))
    t2c = dict([(coef, coef_color) for coef in coefs])
    return Tex(*terms, tex_to_color_map=t2c)


def factored_poly_tex(roots, prefix="P(x) = ", root_colors=[YELLOW, YELLOW]):
    roots = list(roots)
    root_colors = color_gradient(root_colors, len(roots))
    root_texs = [str(r) for r in roots]
    parts = []
    if prefix:
        parts.append(prefix)
    for root_tex in root_texs:
        parts.extend(["(", "x", "-", root_tex, ")"])
    t2c = dict((
        (rt, root_color)
        for rt, root_color in zip(root_texs, root_colors)
    ))
    return Tex(*parts, tex_to_color_map=t2c)


def sym_poly_tex_args(roots, k, abbreviate=False):
    result = []
    subsets = list(it.combinations(roots, k))
    if k in [1, len(roots)]:
        abbreviate = False
    if abbreviate:
        subsets = [*subsets[:2], subsets[-1]]
    for subset in subsets:
        if abbreviate and subset is subsets[-1]:
            result.append(" \\cdots ")
            result.append("+")
        for r in subset:
            result.append(str(r))
            result.append(" \\cdot ")
        result.pop()
        result.append("+")
    result.pop()
    return result


def expanded_poly_tex(roots, vertical=True, root_colors=[YELLOW, YELLOW], abbreviate=False):
    roots = list(roots)
    root_colors = color_gradient(root_colors, len(roots))
    n = len(roots)
    kw = dict(
        tex_to_color_map=dict((
            (str(r), root_color)
            for r, root_color in zip(roots, root_colors)
        )),
        arg_separator=" "
    )
    result = VGroup()
    result.add(Tex(f"x^{{{n}}}"))
    for k in range(1, n + 1):
        sym_poly = sym_poly_tex_args(
            roots, k,
            abbreviate=abbreviate
        )
        line = Tex(
            "+" if k % 2 == 0 else "-",
            "\\big(", *sym_poly, "\\big)",
            x_power_tex(n - k),
            **kw,
        )
        result.add(line)
    for line in result:
        line[-1].set_color(WHITE)
    if vertical:
        result.arrange(DOWN, aligned_edge=LEFT)
    else:
        result.arrange(RIGHT, buff=SMALL_BUFF)
        result[0].shift(result[0].get_height() * UP / 4)
    return result


def get_symmetric_system(lhss, roots=None, root_colors=[YELLOW, YELLOW], lhs_color=MAROON_B, abbreviate=False):
    lhss = [f"{{{lhs}}}" for lhs in lhss]
    if roots is None:
        roots = [f"r_{{{i}}}" for i in range(len(lhss))]
    root_colors = color_gradient(root_colors, len(roots))
    t2c = dict([
        (root, root_color)
        for root, root_color in zip(roots, root_colors)
    ])
    t2c.update(dict([
        (str(lhs), lhs_color)
        for lhs in lhss
    ]))
    kw = dict(tex_to_color_map=t2c)
    equations = VGroup(*(
        Tex(
            lhs, "=",
            *sym_poly_tex_args(roots, k, abbreviate=abbreviate),
            **kw
        )
        for k, lhs in zip(it.count(1), lhss)
    ))
    equations.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
    for eq in equations:
        eq.shift((equations[0][1].get_x() - eq[1].get_x()) * RIGHT)
    return equations


class RootCoefScene(Scene):
    coefs = [3, 2, 1, 0, -1, 1]
    root_plane_config = {
        "x_range": (-2.0, 2.0),
        "y_range": (-2.0, 2.0),
        "background_line_style": {
            "stroke_color": BLUE_E,
        }
    }
    coef_plane_config = {
        "x_range": (-4, 4),
        "y_range": (-4, 4),
        "background_line_style": {
            "stroke_color": GREY,
        }
    }
    plane_height = 5.5
    plane_buff = 1.5
    planes_center = ORIGIN
    plane_arrangement = LEFT

    root_color = YELLOW
    coef_color = RED_B

    dot_style = {
        "radius": 0.05,
        "stroke_color": BLACK,
        "stroke_width": 3,
        "draw_stroke_behind_fill": True,
    }
    include_tracers = True
    include_labels = True
    label_font_size = 30
    coord_label_font_size = 18

    def setup(self):
        self.add_planes()
        self.add_dots()
        self.prepare_cycle_interaction()
        if self.include_tracers:
            self.add_all_tracers()
        if self.include_labels:
            self.add_r_labels()
            self.add_c_labels()

    def add_planes(self):
        # Planes
        planes = VGroup(
            ComplexPlane(**self.root_plane_config),
            ComplexPlane(**self.coef_plane_config),
        )
        for plane in planes:
            plane.set_height(self.plane_height)
        planes.arrange(self.plane_arrangement, buff=self.plane_buff)
        planes.move_to(self.planes_center)

        for plane in planes:
            plane.add_coordinate_labels(font_size=self.coord_label_font_size)
            plane.coordinate_labels.set_opacity(0.8)

        root_plane, coef_plane = planes

        # Lower labels
        root_plane_label = Text("Roots")
        coef_plane_label = Text("Coefficients")

        root_plane_label.next_to(root_plane, DOWN)
        coef_plane_label.next_to(coef_plane, DOWN)

        # Upper labels
        root_poly = self.get_root_poly()
        self.get_r_symbols(root_poly).set_color(self.root_color)
        root_poly.next_to(root_plane, UP)
        root_poly.set_max_width(root_plane.get_width())

        coef_poly = self.get_coef_poly()
        self.get_c_symbols(coef_poly).set_color(self.coef_color)
        coef_poly.set_max_width(coef_plane.get_width())
        coef_poly.next_to(coef_plane, UP)
        coef_poly.match_y(root_poly)

        equals = Tex("=")
        equals.move_to(midpoint(root_poly.get_right(), coef_poly.get_left()))

        self.add(planes)
        self.add(root_plane_label, coef_plane_label)
        self.add(root_poly, coef_poly)
        self.add(equals)

        self.root_plane = root_plane
        self.coef_plane = coef_plane
        self.root_plane_label = root_plane_label
        self.coef_plane_label = coef_plane_label
        self.root_poly = root_poly
        self.coef_poly = coef_poly
        self.poly_equal_sign = equals

    def get_degree(self):
        return len(self.coefs) - 1

    def get_coef_poly(self):
        degree = self.get_degree()
        return Tex(
            f"x^{degree}",
            *(
                f" + c_{n} x^{n}"
                for n in range(degree - 1, 1, -1)
            ),
            " + c_{1} x",
            " + c_{0}",
        )

    def get_root_poly(self):
        return Tex(*(
            f"(x - r_{i})"
            for i in range(self.get_degree())
        ))

    def add_dots(self):
        self.root_dots = VGroup()
        self.coef_dots = VGroup()
        roots = coefficients_to_roots(self.coefs)
        self.add_root_dots(roots)
        self.add_coef_dots(self.coefs)

    #
    def get_all_dots(self):
        return (*self.root_dots, *self.coef_dots)

    def get_r_symbols(self, root_poly):
        return VGroup(*(part[3:5] for part in root_poly))

    def get_c_symbols(self, coef_poly):
        return VGroup(*(part[1:3] for part in coef_poly[:0:-1]))

    def get_random_root(self):
        return complex(
            interpolate(*self.root_plane.x_range[:2], random.random()),
            interpolate(*self.root_plane.y_range[:2], random.random()),
        )

    def get_random_roots(self):
        return [self.get_random_root() for x in range(self.degree)]

    def get_roots_of_unity(self):
        return [np.exp(complex(0, TAU * n / self.degree)) for n in range(self.degree)]

    def set_roots(self, roots):
        self.root_dots.set_submobjects(
            Dot(
                self.root_plane.n2p(root),
                color=self.root_color,
                **self.dot_style,
            )
            for root in roots
        )

    def set_coefs(self, coefs):
        self.coef_dots.set_submobjects(
            Dot(
                self.coef_plane.n2p(coef),
                color=self.coef_color,
                **self.dot_style,
            )
            for coef in coefs[:-1]  # Exclude highest term
        )

    def add_root_dots(self, roots=None):
        if roots is None:
            roots = self.get_roots_of_unity()
        self.set_roots(roots)
        self.add(self.root_dots)

    def add_coef_dots(self, coefs=None):
        if coefs is None:
            coefs = [0] * self.degree + [1]
        self.set_coefs(coefs)
        self.add(self.coef_dots)

    def get_roots(self):
        return [
            self.root_plane.p2n(root_dot.get_center())
            for root_dot in self.root_dots
        ]

    def get_coefs(self):
        return [
            self.coef_plane.p2n(coef_dot.get_center())
            for coef_dot in self.coef_dots
        ] + [1.0]

    def tie_coefs_to_roots(self, clear_updaters=True):
        if clear_updaters:
            self.root_dots.clear_updaters()
            self.coef_dots.clear_updaters()

        def update_coef_dots(cdots):
            coefs = roots_to_coefficients(self.get_roots())
            for dot, coef in zip(cdots, coefs):
                dot.move_to(self.coef_plane.n2p(coef))

        self.coef_dots.add_updater(update_coef_dots)
        self.add(self.coef_dots)
        self.add(*self.root_dots)

    def tie_roots_to_coefs(self, clear_updaters=True):
        if clear_updaters:
            self.root_dots.clear_updaters()
            self.coef_dots.clear_updaters()

        def update_root_dots(rdots):
            new_roots = coefficients_to_roots(self.get_coefs())
            optimal_transport(rdots, map(self.root_plane.n2p, new_roots))

        self.root_dots.add_updater(update_root_dots)
        self.add(self.root_dots)
        self.add(*self.coef_dots)

    def get_tracers(self, dots, time_traced=2.0, **kwargs):
        return VGroup(*(
            TracingTail(
                dot,
                stroke_color=dot.get_fill_color(),
                time_traced=time_traced,
                **kwargs
            )
            for dot in dots
        ))

    def add_all_tracers(self, **kwargs):
        self.tracers = self.get_tracers(self.get_all_dots())
        self.add(self.tracers)

    def get_tracking_lines(self, dots, syms, stroke_width=1, stroke_opacity=0.5):
        lines = VGroup(*(
            Line(
                stroke_color=root.get_fill_color(),
                stroke_width=stroke_width,
                stroke_opacity=stroke_opacity,
            )
            for root in dots
        ))

        def update_lines(lines):
            for sym, dot, line in zip(syms, dots, lines):
                line.put_start_and_end_on(
                    sym.get_bottom(),
                    dot.get_center()
                )

        lines.add_updater(update_lines)
        return lines

    def add_root_lines(self, **kwargs):
        self.root_lines = self.get_tracking_lines(
            self.root_dots,
            self.get_r_symbols(self.root_poly),
            **kwargs
        )
        self.add(self.root_lines)

    def add_coef_lines(self, **kwargs):
        self.coef_lines = self.get_tracking_lines(
            self.coef_dots,
            self.get_c_symbols(self.coef_poly),
            **kwargs
        )
        self.add(self.coef_lines)

    def add_dot_labels(self, labels, dots, buff=0.05):
        for label, dot in zip(labels, dots):
            label.scale(self.label_font_size / label.font_size)
            label.set_fill(dot.get_fill_color())
            label.set_stroke(BLACK, 3, background=True)
            label.dot = dot
            label.add_updater(lambda m: m.next_to(m.dot, UR, buff=buff))
        self.add(*labels)
        return labels

    def add_r_labels(self):
        self.r_dot_labels = self.add_dot_labels(
            VGroup(*(
                Tex(f"r_{i}")
                for i in range(self.get_degree())
            )),
            self.root_dots
        )

    def add_c_labels(self):
        self.c_dot_labels = self.add_dot_labels(
            VGroup(*(
                Tex(f"c_{i}")
                for i in range(self.get_degree())
            )),
            self.coef_dots
        )

    def add_value_label(self):
        pass  # TODO

    # Animations
    def play(self, *anims, **kwargs):
        movers = list(it.chain(*(anim.mobject.get_family() for anim in anims)))
        roots_move = any(rd in movers for rd in self.root_dots)
        coefs_move = any(cd in movers for cd in self.coef_dots)
        if roots_move and not coefs_move:
            self.tie_coefs_to_roots()
        elif coefs_move and not roots_move:
            self.tie_roots_to_coefs()
        super().play(*anims, **kwargs)

    def get_root_swap_arrows(self, i, j,
                             path_arc=90 * DEGREES,
                             stroke_width=5,
                             stroke_opacity=0.7,
                             buff=0.3,
                             **kwargs):
        di = self.root_dots[i].get_center()
        dj = self.root_dots[j].get_center()
        kwargs["path_arc"] = path_arc
        kwargs["stroke_width"] = stroke_width
        kwargs["stroke_opacity"] = stroke_opacity
        kwargs["buff"] = buff
        return VGroup(
            Arrow(di, dj, **kwargs),
            Arrow(dj, di, **kwargs),
        )

    def swap_roots(self, *indices, run_time=2, wait_time=1, **kwargs):
        self.play(CyclicReplace(
            *(
                self.root_dots[i]
                for i in indices
            ),
            run_time=run_time,
            **kwargs
        ))
        self.wait(wait_time)

    def rotate_coefs(self, indicies, center_z=0, run_time=5, wait_time=1, **kwargs):
        self.play(*(
            Rotate(
                self.coef_dots[i], TAU,
                about_point=self.coef_plane.n2p(center_z),
                run_time=run_time,
                **kwargs
            )
            for i in indicies
        ))
        self.wait(wait_time)

    def rotate_coef(self, i, **kwargs):
        self.rotate_coefs([i], **kwargs)

    # Interaction
    def prepare_cycle_interaction(self):
        self.dots_awaiting_cycle = []
        self.dot_awaiting_loop = None
        self.cycle_glow = Group()
        self.add(self.cycle_glow)

    def handle_cycle_preparation(self, dot):
        glow_dot = GlowDot(color=WHITE)
        always(glow_dot.move_to, dot)
        self.cycle_glow.add(glow_dot)
        if dot in self.root_dots and dot not in self.dots_awaiting_cycle:
            self.dots_awaiting_cycle.append(dot)
        if dot in self.coef_dots and dot is not self.dot_awaiting_loop:
            self.dot_awaiting_loop = dot
        self.add(dot)
        self.refresh_locked_data()

    def carry_out_cycle(self):
        if self.dots_awaiting_cycle:
            self.tie_coefs_to_roots()
            self.unlock_mobject_data()
            self.play(CyclicReplace(*self.dots_awaiting_cycle, run_time=5))
        if self.dot_awaiting_loop is not None:
            self.tie_roots_to_coefs()
            self.unlock_mobject_data()
            self.play(Rotate(
                self.dot_awaiting_loop,
                angle=TAU,
                about_point=self.mouse_point.get_center().copy(),
                run_time=8
            ))
        self.play(FadeOut(self.cycle_glow))
        self.prepare_cycle_interaction()

    def on_mouse_release(self, point, button, mods):
        super().on_mouse_release(point, button, mods)
        if self.root_dots.has_updaters or self.coef_dots.has_updaters:
            # End the interaction where a dot is tied to the mouse
            self.root_dots.clear_updaters()
            self.coef_dots.clear_updaters()
            return
        dot = self.point_to_mobject(point, search_set=self.get_all_dots(), buff=0.1)
        if dot is None:
            return
        if self.window.is_key_pressed(ord("c")):
            self.handle_cycle_preparation(dot)
            return
        # Otherwise, have this dot track with the mouse
        if dot in self.root_dots:
            self.tie_coefs_to_roots()
        elif dot in self.coef_dots:
            self.tie_roots_to_coefs()
        self.mouse_point.move_to(point)
        dot.add_updater(lambda m: m.move_to(self.mouse_point))
        self.refresh_locked_data()

    def on_key_release(self, symbol, modifiers):
        super().on_key_release(symbol, modifiers)
        char = chr(symbol)
        if char == "c":
            self.carry_out_cycle()


class QuadraticFormula(RootCoefScene):
    coefs = [-1, 0, 1]
    coef_plane_config = {
        "x_range": (-2.0, 2.0),
        "y_range": (-2.0, 2.0),
        "background_line_style": {
            "stroke_color": GREY_B,
            "stroke_width": 1.0,
        }
    }
    sqrt_plane_config = {
        "x_range": (-2.0, 2.0),
        "y_range": (-2.0, 2.0),
        "background_line_style": {
            "stroke_color": BLUE_D,
            "stroke_width": 1.0,
        }
    }
    plane_height = 3.5
    plane_arrangement = RIGHT
    plane_buff = 1.0
    planes_center = 2 * LEFT + DOWN

    def add_planes(self):
        super().add_planes()
        self.coef_plane_label.match_y(self.root_plane_label)
        self.add_sqrt_plane()

    def add_sqrt_plane(self):
        plane = ComplexPlane(**self.sqrt_plane_config)
        plane.next_to(self.coef_plane, self.plane_arrangement, self.plane_buff)
        plane.set_height(self.plane_height)
        plane.add_coordinate_labels(font_size=24)

        label = Tex(
            "-{b \\over 2} \\pm \\sqrt{{b^2 \\over 4} - c}",
            font_size=30,
        )[0]
        for i in [1, 7, 12]:
            label[i].set_color(self.coef_color)
        label.next_to(plane, UP)

        self.sqrt_plane = plane
        self.sqrt_label = label
        self.add(plane)
        self.add(label)

    def add_dots(self):
        super().add_dots()
        dots = self.root_dots.copy().clear_updaters()
        dots.set_color(GREEN)

        def update_dots(dots):
            for dot, root in zip(dots, self.get_roots()):
                dot.move_to(self.sqrt_plane.n2p(root))
            return dots

        dots.add_updater(update_dots)

        self.sqrt_dots = dots
        self.add(dots)
        self.add(self.get_tracers(dots))

    def get_coef_poly(self):
        return Tex(
            "x^2", "+ b x", "+ c"
        )

    def add_c_labels(self):
        self.c_dot_labels = self.add_dot_labels(
            VGroup(Tex("c"), Tex("b")),
            self.coef_dots
        )

    def get_c_symbols(self, coef_poly):
        return VGroup(*(part[1] for part in coef_poly[:0:-1]))


class CubicFormula(RootCoefScene):
    coefs = [1, -1, 0, 1]
    coef_plane_config = {
        "x_range": (-2.0, 2.0),
        "y_range": (-2.0, 2.0),
        "background_line_style": {
            "stroke_color": GREY,
            "stroke_width": 1.0,
        }
    }
    root_plane_config = {
        "x_range": (-2.0, 2.0),
        "y_range": (-2.0, 2.0),
        "background_line_style": {
            "stroke_color": BLUE_E,
            "stroke_width": 1.0,
        }
    }
    sqrt_plane_config = {
        "x_range": (-1.0, 1.0),
        "y_range": (-1.0, 1.0),
        "background_line_style": {
            "stroke_color": GREY_B,
            "stroke_width": 1.0,
        },
        "height": 3.0,
        "width": 3.0,
    }
    crt_plane_config = {
        "x_range": (-2.0, 2.0),
        "y_range": (-2.0, 2.0),
        "background_line_style": {
            "stroke_color": BLUE_E,
            "stroke_width": 1.0,
        },
        "height": 3.0,
        "width": 3.0,
    }
    cf_plane_config = {
        "x_range": (-2.0, 2.0),
        "y_range": (-2.0, 2.0),
        "background_line_style": {
            "stroke_color": BLUE_E,
            "stroke_width": 1.0,
        },
        "height": 3.0,
        "width": 3.0,
    }
    plane_height = 3.0
    plane_buff = 1.0
    planes_center = 1.6 * UP
    lower_planes_height = 2.75
    lower_planes_buff = 2.0

    sqrt_dot_color = GREEN
    crt_dot_colors = (RED, BLUE)
    cf_dot_color = YELLOW

    def add_planes(self):
        super().add_planes()
        self.root_plane_label.next_to(self.root_plane, -self.plane_arrangement)
        self.coef_plane_label.next_to(self.coef_plane, self.plane_arrangement)
        self.add_lower_planes()

    def add_lower_planes(self):
        sqrt_plane = ComplexPlane(**self.sqrt_plane_config)
        crt_plane = ComplexPlane(**self.crt_plane_config)
        cf_plane = ComplexPlane(**self.cf_plane_config)

        planes = VGroup(sqrt_plane, crt_plane, cf_plane)
        for plane in planes:
            plane.add_coordinate_labels(font_size=16)
        planes.set_height(self.lower_planes_height)
        planes.arrange(RIGHT, buff=self.lower_planes_buff)
        planes.to_edge(DOWN, buff=SMALL_BUFF)

        kw = dict(
            font_size=24,
            tex_to_color_map={
                "\\delta_1": GREEN,
                "\\delta_2": GREEN,
            },
            background_stroke_width=3,
            background_stroke_color=3,
        )

        sqrt_label = Tex(
            "\\delta_1, \\delta_2 = \\sqrt{ \\frac{q^2}{4} + \\frac{p^3}{27}}",
            **kw
        )
        sqrt_label.set_backstroke()
        sqrt_label.next_to(sqrt_plane, UP, SMALL_BUFF)

        crt_labels = VGroup(
            Tex("\\cdot", "= \\sqrt[3]{-\\frac{q}{2} + \\delta_1}", **kw),
            Tex("\\cdot", "= \\sqrt[3]{-\\frac{q}{2} + \\delta_2}", **kw),
        )
        for label, color in zip(crt_labels, self.crt_dot_colors):
            label[0].scale(4, about_edge=RIGHT)
            label[0].set_color(color)
            label.set_backstroke()
        crt_labels.arrange(RIGHT, buff=MED_LARGE_BUFF)
        crt_labels.next_to(crt_plane, UP, SMALL_BUFF)

        cf_label = Tex(
            "\\sqrt[3]{-\\frac{q}{2} + \\delta_1} +",
            "\\sqrt[3]{-\\frac{q}{2} + \\delta_2}",
            **kw
        )
        cf_label.set_backstroke()
        cf_label.next_to(cf_plane, UP, SMALL_BUFF)

        self.add(planes)
        self.add(sqrt_label)
        self.add(crt_labels)
        self.add(cf_label)

        self.sqrt_plane = sqrt_plane
        self.crt_plane = crt_plane
        self.cf_plane = cf_plane
        self.sqrt_label = sqrt_label
        self.crt_labels = crt_labels
        self.cf_label = cf_label

    def get_coef_poly(self):
        return Tex(
            "x^3 + {0}x^2 + {p}x + {q}",
            tex_to_color_map={
                "{0}": self.coef_color,
                "{p}": self.coef_color,
                "{q}": self.coef_color,
            }
        )

    def add_c_labels(self):
        self.c_dot_labels = self.add_dot_labels(
            VGroup(*map(Tex, ["q", "p", "0"])),
            self.coef_dots
        )

    def get_c_symbols(self, coef_poly):
        return VGroup(*(
            coef_poly.get_part_by_tex(tex)
            for tex in ["q", "p", "0"]
        ))

    #
    def add_dots(self):
        super().add_dots()
        self.add_sqrt_dots()
        self.add_crt_dots()
        self.add_cf_dots()

    def add_sqrt_dots(self):
        sqrt_dots = Dot(**self.dot_style).replicate(2)
        sqrt_dots.set_color(self.sqrt_dot_color)

        def update_sqrt_dots(dots):
            q, p, zero, one = self.get_coefs()
            disc = (q**2 / 4) + (p**3 / 27)
            roots = get_nth_roots(disc, 2)
            optimal_transport(dots, map(self.sqrt_plane.n2p, roots))
            return dots

        sqrt_dots.add_updater(update_sqrt_dots)

        self.sqrt_dots = sqrt_dots
        self.add(sqrt_dots)
        self.add(self.get_tracers(sqrt_dots))

        # Labels
        self.delta_labels = self.add_dot_labels(
            VGroup(Tex("\\delta_1"), Tex("\\delta_2")),
            sqrt_dots
        )

    def get_deltas(self):
        return list(map(self.sqrt_plane.p2n, (d.get_center() for d in self.sqrt_dots)))

    def add_crt_dots(self):
        crt_dots = Dot(**self.dot_style).replicate(3).replicate(2)
        for dots, color in zip(crt_dots, self.crt_dot_colors):
            dots.set_color(color)

        def update_crt_dots(dot_triples):
            q, p, zero, one = self.get_coefs()
            deltas = self.get_deltas()

            for delta, triple in zip(deltas, dot_triples):
                roots = get_nth_roots(-q / 2 + delta, 3)
                optimal_transport(triple, map(self.crt_plane.n2p, roots))
            return dot_triples

        crt_dots.add_updater(update_crt_dots)

        self.add(crt_dots)
        self.add(*(self.get_tracers(triple) for triple in crt_dots))

        self.crt_dots = crt_dots

    def get_cube_root_values(self):
        return [
            [
                self.crt_plane.p2n(d.get_center())
                for d in triple
            ]
            for triple in self.crt_dots
        ]

    def add_crt_lines(self):
        crt_lines = VGroup(*(
            Line(stroke_color=color, stroke_width=1).replicate(3)
            for color in self.crt_dot_colors
        ))

        def update_crt_lines(crt_lines):
            cube_root_values = self.get_cube_root_values()
            origin = self.crt_plane.n2p(0)
            for lines, triple in zip(crt_lines, cube_root_values):
                for line, value in zip(lines, triple):
                    line.put_start_and_end_on(origin, self.crt_plane.n2p(value))

        crt_lines.add_updater(update_crt_lines)

        self.add(crt_lines)
        self.crt_lines = crt_lines

    def add_cf_dots(self):
        cf_dots = Dot(**self.dot_style).replicate(9)
        cf_dots.set_fill(self.root_color, opacity=0.5)

        def update_cf_dots(dots):
            cube_root_values = self.get_cube_root_values()
            for dot, (z1, z2) in zip(dots, it.product(*cube_root_values)):
                dot.move_to(self.cf_plane.n2p(z1 + z2))
            return dots

        cf_dots.add_updater(update_cf_dots)

        alt_root_dots = GlowDot()
        alt_root_dots.add_updater(lambda m: m.set_points(
            list(map(self.cf_plane.n2p, self.get_roots()))
        ))

        self.cf_dots = cf_dots
        self.alt_root_dots = alt_root_dots

        self.add(cf_dots)
        self.add(self.get_tracers(cf_dots, stroke_width=0.5))
        self.add(alt_root_dots)

    def add_cf_lines(self):
        cf_lines = VGroup(
            Line(stroke_color=self.crt_dot_colors[0]).replicate(9),
            Line(stroke_color=self.crt_dot_colors[1]).replicate(3),
        )
        cf_lines.set_stroke(width=1)

        def update_cf_lines(cf_lines):
            cube_root_values = self.get_cube_root_values()
            for z1, line in zip(cube_root_values[1], cf_lines[1]):
                line.put_start_and_end_on(
                    self.cf_plane.n2p(0),
                    self.cf_plane.n2p(z1),
                )
            for line, (z1, z2) in zip(cf_lines[0], it.product(*cube_root_values)):
                line.put_start_and_end_on(
                    self.cf_plane.n2p(z2),
                    self.cf_plane.n2p(z1 + z2),
                )

        cf_lines.add_updater(update_cf_lines)

        self.cf_lines = cf_lines
        self.add(cf_lines)


# Scenes

class ConstructPolynomialWithGivenRoots(Scene):
    root_color = YELLOW

    def construct(self):
        # Add axes
        axes = self.add_axes()

        # Add challenge
        challenge = VGroup(
            Text("Can you construct a cubic polynomial"),
            Tex(
                "P(x) = x^3 + c_2 x^2 + c_1 x + c_0",
                tex_to_color_map={
                    "c_2": MAROON_B,
                    "c_1": MAROON_B,
                    "c_0": MAROON_B,
                }
            ),
            TexText(
                "with roots at $x = 1$, $x = 2$, and $x = 4$?",
                tex_to_color_map={
                    "$x = 1$": self.root_color,
                    "$x = 2$": self.root_color,
                    "$x = 4$": self.root_color,
                }
            )
        )
        challenge.scale(0.7)
        challenge.arrange(DOWN, buff=MED_LARGE_BUFF)
        challenge.to_corner(UL)

        self.add(challenge)

        # Add graph
        roots = [1, 2, 4]
        coefs = roots_to_coefficients(roots)
        graph = axes.get_graph(lambda x: poly(x, coefs))
        graph.set_color(BLUE)

        root_dots = Group(*(GlowDot(axes.c2p(x, 0)) for x in roots))
        root_dots.set_color(self.root_color)

        x_terms = challenge[2].get_parts_by_tex("x = ")

        self.wait()
        self.play(
            LaggedStart(*(
                FadeTransform(x_term.copy(), dot)
                for x_term, dot in zip(x_terms, root_dots)
            ), lag_ratio=0.7, run_time=3)
        )
        self.add(graph, root_dots)
        self.play(ShowCreation(graph, run_time=3, rate_func=linear))
        self.wait()

        # Show factored solution
        factored = factored_poly_tex(roots)
        factored.match_height(challenge[1])
        factored.next_to(challenge, DOWN, LARGE_BUFF)

        rects = VGroup(*(
            SurroundingRectangle(
                factored[i:i + 5],
                stroke_width=1,
                stroke_color=BLUE,
                buff=0.05
            )
            for i in range(1, 12, 5)
        ))
        arrows = VGroup(*(
            Vector(DOWN).next_to(dot, UP, buff=0)
            for dot in root_dots
        ))
        zeros_eqs = VGroup(*(
            Tex(
                f"P({r}) = 0",
                font_size=24
            ).next_to(rect, UP, SMALL_BUFF)
            for r, rect in zip(roots, rects)
        ))

        self.play(FadeIn(factored, DOWN))
        self.wait()
        to_fade = VGroup()
        for rect, arrow, eq in zip(rects, arrows, zeros_eqs):
            self.play(
                ShowCreation(rect),
                FadeIn(eq),
                ShowCreation(arrow),
                FadeOut(to_fade)
            )
            self.wait(2)
            to_fade = VGroup(rect, arrow, eq)
        self.play(FadeOut(to_fade))

        # Expand solution
        x_terms = factored[2::5]
        root_terms = VGroup(*(
            VGroup(m1, m2)
            for m1, m2 in zip(factored[3::5], factored[4::5])
        ))

        expanded = Tex(
            "&x^3 ",
            "-1x^2", "-2x^2", "-4x^2 \\\\",
            "&+(-1)(-2)x", "+(-1)(-4)x", "+(-2)(-4)x\\\\",
            "&+(-1)(-2)(-4)",
        )
        for i, part in enumerate(expanded):
            if i in [1, 2, 3]:
                part[:2].set_color(self.root_color)
            elif i in [4, 5, 6, 7]:
                part[2:4].set_color(self.root_color)
                part[6:8].set_color(self.root_color)
            if i == 7:
                part[10:12].set_color(self.root_color)

        expanded.scale(0.7)
        expanded.next_to(factored[1], DOWN, MED_LARGE_BUFF, aligned_edge=LEFT)
        equals = factored[0][-1].copy()
        equals.match_y(expanded[0][0])

        self.add(equals)
        expanded_iter = iter(expanded)
        for k in range(4):
            for tup in it.combinations(range(3), k):
                factored[1:].set_opacity(0.5)
                rects = VGroup()
                for i in range(3):
                    mob = root_terms[i] if (i in tup) else x_terms[i]
                    mob.set_opacity(1)
                    rect = SurroundingRectangle(mob, buff=SMALL_BUFF)
                    rect.set_min_height(0.45, about_edge=DOWN)
                    rects.add(rect)
                rects.set_stroke(BLUE, 2)
                expanded_term = next(expanded_iter)
                expanded_rect = SurroundingRectangle(
                    expanded_term, buff=SMALL_BUFF
                )
                expanded_rect.match_style(rects)

                self.add(rects, expanded_rect)
                self.add(expanded_term)
                self.wait()
                self.remove(rects, expanded_rect)
        factored.set_opacity(1)
        self.add(expanded)
        self.wait()

        # Cleaner expansion
        cleaner_expanded = expanded_poly_tex(roots, vertical=False)
        cleaner_expanded.scale(0.7)
        cleaner_expanded.shift(expanded[0][0].get_center() - cleaner_expanded[0][0][0].get_center())

        self.play(
            FadeTransform(expanded[0], cleaner_expanded[0]),
            TransformMatchingShapes(
                expanded[1:4],
                cleaner_expanded[1],
            ),
            expanded[4:].animate.next_to(cleaner_expanded[1], DOWN, aligned_edge=LEFT)
        )
        self.wait()
        self.play(
            TransformMatchingShapes(
                expanded[4:7],
                cleaner_expanded[2],
            )
        )
        self.wait()
        self.play(
            TransformMatchingShapes(
                expanded[7],
                cleaner_expanded[3],
            )
        )
        back_rect = BackgroundRectangle(cleaner_expanded, buff=SMALL_BUFF)
        self.add(back_rect, cleaner_expanded)
        self.play(FadeIn(back_rect))
        self.wait()

        # Evaluate
        answer = Tex(
            "= x^3 -7x^2 + 14x -8",
            tex_to_color_map={
                "-7": MAROON_B,
                "14": MAROON_B,
                "-8": MAROON_B,
            }
        )
        answer.scale(0.7)
        answer.next_to(equals, DOWN, MED_LARGE_BUFF, aligned_edge=LEFT)

        self.play(FadeIn(answer, DOWN))
        self.wait()

        # Show general expansion
        rs = [f"r_{i}" for i in range(3)]
        gen_factored = factored_poly_tex(rs)
        gen_expanded = expanded_poly_tex(rs, vertical=False)
        for gen, old in (gen_factored, factored), (gen_expanded, cleaner_expanded):
            gen.match_height(old)
            gen.move_to(old, LEFT)

        self.play(FadeTransformPieces(factored, gen_factored))
        self.wait()
        for i in range(1, 4):
            self.play(
                FadeTransformPieces(cleaner_expanded[i], gen_expanded[i]),
                cleaner_expanded[i + 1:].animate.next_to(gen_expanded[i], RIGHT, SMALL_BUFF)
            )
            self.wait()
        self.remove(cleaner_expanded)
        self.add(gen_expanded)

        # Reverse question
        top_lhs = Tex("P(x)").match_height(factored)
        top_lhs.next_to(answer, LEFT).align_to(factored, LEFT)
        top_lhs.set_opacity(0)
        coef_poly = VGroup(top_lhs, answer)

        self.play(
            FadeOut(challenge, UP),
            coef_poly.animate.set_opacity(1).to_edge(UP),
        )

        new_challenge = Text("Find the roots!")
        new_challenge.add_background_rectangle(buff=0.1)
        arrow = Vector(LEFT)
        arrow.next_to(coef_poly, RIGHT)
        new_challenge.next_to(arrow, RIGHT)

        self.play(
            ShowCreation(arrow),
            FadeIn(new_challenge, 0.5 * RIGHT),
        )
        self.wait()

        full_factored = VGroup(back_rect, gen_factored, equals, gen_expanded)
        self.play(
            full_factored.animate.next_to(
                coef_poly, DOWN, MED_LARGE_BUFF, aligned_edge=LEFT,
            )
        )
        self.wait()

        # Show system of equations
        system = get_symmetric_system([7, 14, 8])
        system.next_to(full_factored, DOWN, LARGE_BUFF, aligned_edge=LEFT)

        coef_terms = answer[1::2]
        rhss = [term[2:-2] for term in gen_expanded[1:]]

        for coef, rhs, eq in zip(coef_terms, rhss, system):
            self.play(
                FadeTransform(coef.copy(), eq[0]),
                FadeIn(eq[1]),
                FadeTransform(rhs.copy(), eq[2:]),
            )
            self.wait()

        cubic_example = VGroup(coef_poly, full_factored, system)

        # Show quintic
        q_roots = [-1, 1, 2, 4, 6]
        q_coefs = roots_to_coefficients(q_roots)
        q_poly = poly_tex(q_coefs)
        q_poly_factored = factored_poly_tex(
            [f"r_{i}" for i in range(5)],
            root_colors=[YELLOW, GREEN]
        )
        VGroup(q_poly, q_poly_factored).scale(0.8)
        q_poly.to_corner(UL)
        q_poly_factored.next_to(q_poly, DOWN, MED_LARGE_BUFF, aligned_edge=LEFT)

        self.play(
            FadeOut(cubic_example, DOWN),
            FadeOut(VGroup(arrow, new_challenge), DOWN),
            FadeIn(q_poly, DOWN)
        )

        y_scale_factor = 0.1
        new_graph = axes.get_graph(
            lambda x: y_scale_factor * poly(x, q_coefs),
            x_range=(-1.2, 6.2)
        )
        new_root_dots = Group(*(
            GlowDot(axes.c2p(x, 0))
            for x in q_roots
        ))
        new_graph.match_style(graph)
        axes.save_state()
        graph.save_state()
        root_dots.save_state()
        self.play(
            Transform(graph, new_graph),
            Transform(root_dots, new_root_dots),
        )
        self.wait()

        root_terms = q_poly_factored.get_parts_by_tex("r_")
        self.play(
            FadeIn(q_poly_factored, lag_ratio=0.1, run_time=2),
            LaggedStart(*(
                FadeTransform(dot.copy(), term, remover=True)
                for dot, term in zip(root_dots, root_terms)
            ), lag_ratio=0.5, run_time=3)
        )
        self.wait()

        # Quintic system
        signed_coefs = [
            (-1)**k * c for
            k, c in zip(it.count(1), q_coefs[-2::-1])
        ]
        q_system, q_system_full = [
            get_symmetric_system(
                signed_coefs,
                abbreviate=abbrev,
                root_colors=[YELLOW, GREEN],
            )
            for abbrev in [True, False]
        ]
        for mob in q_system, q_system_full:
            mob.scale(0.8)
            mob.next_to(q_poly_factored, DOWN, LARGE_BUFF, aligned_edge=LEFT)

        root_tuple_groups = VGroup(*(
            VGroup(*(
                VGroup(*tup)
                for tup in it.combinations(root_terms, k)
            ))
            for k in range(1, 6)
        ))

        for equation, tuple_group in zip(q_system, root_tuple_groups):
            rects_group = VGroup(*(
                VGroup(*(
                    SurroundingRectangle(term).set_stroke(BLUE, 2)
                    for term in tup
                ))
                for tup in tuple_group
            ))
            terms_column = VGroup(*(
                VGroup(*tup).copy().arrange(RIGHT, buff=SMALL_BUFF)
                for tup in tuple_group
            ))
            terms_column.arrange(DOWN)
            terms_column.move_to(4 * RIGHT).to_edge(UP)

            anims = [
                FadeIn(equation),
                ShowSubmobjectsOneByOne(rects_group, rate_func=linear, run_time=3),
                ShowIncreasingSubsets(terms_column, rate_func=linear, run_time=3, int_func=np.ceil),
            ]
            if equation is q_system[2]:
                anims.append(
                    Group(axes, graph, root_dots).animate.scale(
                        0.5, about_point=axes.c2p(6, 0)
                    )
                )
            self.play(*anims)
            self.remove(rects_group)
            self.wait()
            self.play(FadeOut(terms_column))
            self.wait()
        self.wait()

        frame = self.camera.frame
        frame.save_state()
        self.play(
            frame.animate.replace(q_system_full, dim_to_match=0).scale(1.1),
            FadeIn(q_system_full, lag_ratio=0.1),
            FadeOut(q_system),
            Group(axes, graph, root_dots).animate.shift(2 * DOWN),
            run_time=2,
        )
        self.wait(2)

        # Back to cubic
        self.play(
            Restore(axes),
            Restore(graph),
            Restore(root_dots),
            FadeOut(q_system_full, 2 * DOWN),
            FadeOut(q_poly, 2 * DOWN),
            FadeOut(q_poly_factored, 2 * DOWN),
            FadeIn(cubic_example, 2 * DOWN),
            Restore(frame),
            run_time=2,
        )
        self.wait()

        # Can you always factor?
        question = Text("Is this always possible?")
        question.add_background_rectangle(buff=0.1)
        question.next_to(gen_factored, RIGHT, buff=2)
        question.to_edge(UP, buff=MED_SMALL_BUFF)
        arrow = Arrow(question.get_left(), gen_factored.get_corner(UR))

        self.play(
            FadeIn(question),
            ShowCreation(arrow),
            FlashAround(gen_factored, run_time=3)
        )
        self.wait()
        self.play(FadeOut(question), FadeOut(arrow))

        const_dec = DecimalNumber(8)
        top_const_dec = const_dec.copy()
        for dec, mob, vect in (const_dec, system[2][0], RIGHT), (top_const_dec, answer[-1][1], LEFT):
            dec.match_height(mob)
            dec.move_to(mob, vect)
            dec.set_color(RED)
            mob.set_opacity(0)
            self.add(dec)
        answer[-1][0].set_color(RED)

        top_const_dec.add_updater(lambda m: m.set_value(const_dec.get_value()))

        def get_coefs():
            return [-const_dec.get_value(), 14, -7, 1]

        def get_roots():
            return coefficients_to_roots(get_coefs())

        def update_graph(graph):
            graph.become(axes.get_graph(lambda x: poly(x, get_coefs())))
            graph.set_stroke(BLUE, 3)

        def update_root_dots(dots):
            roots = get_roots()
            for root, dot in zip(roots, dots):
                if abs(root.imag) > 1e-8:
                    dot.set_opacity(0)
                else:
                    dot.move_to(axes.c2p(root.real, 0))
                    dot.set_opacity(1)

        graph.add_updater(update_graph)
        self.remove(*root_dots, *new_root_dots)
        root_dots = root_dots[:3]
        root_dots.add_updater(update_root_dots)
        self.add(root_dots)

        example_constants = [5, 6, 9, 6.28]
        for const in example_constants:
            self.play(
                ChangeDecimalToValue(const_dec, const),
                run_time=3,
            )
            self.wait()

        # Show complex plane
        plane = ComplexPlane(
            (-1, 6), (-3, 3)
        )
        plane.replace(axes.x_axis.ticks, dim_to_match=0)
        plane.add_coordinate_labels(font_size=24)
        plane.save_state()
        plane.rotate(PI / 2, LEFT)
        plane.set_opacity(0)

        real_label = Text("Real numbers")
        real_label.next_to(root_dots, UP, SMALL_BUFF)
        complex_label = Text("Complex numbers")
        complex_label.set_backstroke()
        complex_label.next_to(plane.saved_state.get_corner(UR), DL, SMALL_BUFF)

        graph.clear_updaters()
        root_dots.clear_updaters()
        axes.generate_target(use_deepcopy=True)
        axes.target.y_axis.set_opacity(0)
        axes.target.x_axis.numbers.set_opacity(1)
        self.play(
            Uncreate(graph),
            Write(real_label),
            MoveToTarget(axes),
        )
        self.wait(2)
        self.add(plane, root_dots, real_label)
        self.play(
            Restore(plane),
            FadeOut(axes.x_axis),
            FadeTransform(real_label, complex_label),
            run_time=2,
        )
        self.wait(2)

        self.play(
            VGroup(coef_poly, top_const_dec).animate.next_to(plane, UP),
            gen_factored.animate.next_to(plane, UP, buff=1.2),
            FadeOut(equals),
            FadeOut(gen_expanded),
            frame.animate.shift(DOWN),
            run_time=2,
        )
        self.wait()

        eq_zero = Tex("= 0")
        eq_zero.scale(0.7)
        eq_zero.next_to(top_const_dec, RIGHT, SMALL_BUFF)
        eq_zero.shift(0.2 * LEFT)
        self.play(
            Write(eq_zero),
            VGroup(coef_poly, top_const_dec).animate.shift(0.2 * LEFT),
        )
        self.wait()

        # Show constant tweaking again
        def update_complex_roots(root_dots):
            for root, dot in zip(get_roots(), root_dots):
                dot.move_to(plane.n2p(root))

        root_dots.add_updater(update_complex_roots)

        self.play(
            FlashAround(const_dec),
            FlashAround(top_const_dec),
            run_time=2,
        )

        self.play(
            ChangeDecimalToValue(const_dec, 4),
            run_time=3,
        )
        self.wait()
        root_eqs = VGroup(*(
            VGroup(Tex(f"r_{i} ", "="), DecimalNumber(root, num_decimal_places=3)).arrange(RIGHT)
            for i, root in enumerate(get_roots())
        ))
        root_eqs.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        for eq in root_eqs:
            eq[0][0].set_color(YELLOW)
        root_eqs.next_to(system, UP)
        root_eqs.align_to(gen_factored, UP)
        self.play(
            FadeIn(root_eqs),
            VGroup(system, const_dec).animate.next_to(root_eqs, DOWN, LARGE_BUFF),
        )
        self.wait(2)
        self.play(FadeOut(root_eqs))

        example_constants = [4, 7, 9, 5]
        for const in example_constants:
            self.play(
                ChangeDecimalToValue(const_dec, const),
                run_time=3,
            )
            self.wait()

    def add_axes(self):
        x_range = (-1, 6)
        y_range = (-3, 11)
        axes = Axes(
            x_range, y_range,
            axis_config=dict(include_tip=False, numbers_to_exclude=[]),
            widith=abs(op.sub(*x_range)),
            height=abs(op.sub(*y_range)),
        )
        axes.set_height(FRAME_HEIGHT - 1)
        axes.to_edge(RIGHT)
        axes.x_axis.add_numbers(font_size=24)
        axes.x_axis.numbers[1].set_opacity(0)

        self.add(axes)
        return axes


class FactsAboutRootsToCoefficients(RootCoefScene):
    coefs = [-5, 14, -7, 1]
    coef_plane_config = {
        "x_range": (-10.0, 15.0, 5.0),
        "y_range": (-10.0, 1.0),
        "background_line_style": {
            "stroke_color": GREY,
            "stroke_width": 1.0,
        }
    }
    root_plane_config = {
        "x_range": (-1.0, 6.0),
        "y_range": (-3.0, 3.0),
        "background_line_style": {
            "stroke_color": BLUE_E,
            "stroke_width": 1.0,
        }
    }

    def construct(self):
        pass


class Cubic(RootCoefScene):
    coefs = [1, -1, 0, 1]

    def construct(self):
        pass


class AmbientRootSwapping(RootCoefScene):
    n_swaps = 0

    def construct(self):
        for x in range(self.n_swaps):
            k = random.randint(2, 5)
            indices = random.choice(list(it.combinations(range(5), k)))
            self.swap_roots(*indices)
            self.wait()

        self.embed()


class CubicFormulaTest(CubicFormula):
    def construct(self):
        pass
        # self.embed()