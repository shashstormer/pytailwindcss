import re

__version__ = '0.0.3'


class Tailwind:
    def __init__(self):
        self.colors = {
            "inherit": 'inherit',
            "current": 'currentColor',
            "transparent": 'transparent',
            "black": '#000',
            "white": '#fff',
            "slate": {
                "50": '#f8fafc',
                "100": '#f1f5f9',
                "200": '#e2e8f0',
                "300": '#cbd5e1',
                "400": '#94a3b8',
                "500": '#64748b',
                "600": '#475569',
                "700": '#334155',
                "800": '#1e293b',
                "900": '#0f172a',
                "950": '#020617',
            },
            "gray": {
                "50": '#f9fafb',
                "100": '#f3f4f6',
                "200": '#e5e7eb',
                "300": '#d1d5db',
                "400": '#9ca3af',
                "500": '#6b7280',
                "600": '#4b5563',
                "700": '#374151',
                "800": '#1f2937',
                "900": '#111827',
                "950": '#030712',
            },
            "zinc": {
                "50": '#fafafa',
                "100": '#f4f4f5',
                "200": '#e4e4e7',
                "300": '#d4d4d8',
                "400": '#a1a1aa',
                "500": '#71717a',
                "600": '#52525b',
                "700": '#3f3f46',
                "800": '#27272a',
                "900": '#18181b',
                "950": '#09090b',
            },
            "neutral": {
                "50": '#fafafa',
                "100": '#f5f5f5',
                "200": '#e5e5e5',
                "300": '#d4d4d4',
                "400": '#a3a3a3',
                "500": '#737373',
                "600": '#525252',
                "700": '#404040',
                "800": '#262626',
                "900": '#171717',
                "950": '#0a0a0a',
            },
            "stone": {
                "50": '#fafaf9',
                "100": '#f5f5f4',
                "200": '#e7e5e4',
                "300": '#d6d3d1',
                "400": '#a8a29e',
                "500": '#78716c',
                "600": '#57534e',
                "700": '#44403c',
                "800": '#292524',
                "900": '#1c1917',
                "950": '#0c0a09',
            },
            "red": {
                "50": '#fef2f2',
                "100": '#fee2e2',
                "200": '#fecaca',
                "300": '#fca5a5',
                "400": '#f87171',
                "500": '#ef4444',
                "600": '#dc2626',
                "700": '#b91c1c',
                "800": '#991b1b',
                "900": '#7f1d1d',
                "950": '#450a0a',
            },
            "orange": {
                "50": '#fff7ed',
                "100": '#ffedd5',
                "200": '#fed7aa',
                "300": '#fdba74',
                "400": '#fb923c',
                "500": '#f97316',
                "600": '#ea580c',
                "700": '#c2410c',
                "800": '#9a3412',
                "900": '#7c2d12',
                "950": '#431407',
            },
            "amber": {
                "50": '#fffbeb',
                "100": '#fef3c7',
                "200": '#fde68a',
                "300": '#fcd34d',
                "400": '#fbbf24',
                "500": '#f59e0b',
                "600": '#d97706',
                "700": '#b45309',
                "800": '#92400e',
                "900": '#78350f',
                "950": '#451a03',
            },
            "yellow": {
                "50": '#fefce8',
                "100": '#fef9c3',
                "200": '#fef08a',
                "300": '#fde047',
                "400": '#facc15',
                "500": '#eab308',
                "600": '#ca8a04',
                "700": '#a16207',
                "800": '#854d0e',
                "900": '#713f12',
                "950": '#422006',
            },
            "lime": {
                "50": '#f7fee7',
                "100": '#ecfccb',
                "200": '#d9f99d',
                "300": '#bef264',
                "400": '#a3e635',
                "500": '#84cc16',
                "600": '#65a30d',
                "700": '#4d7c0f',
                "800": '#3f6212',
                "900": '#365314',
                "950": '#1a2e05',
            },
            "green": {
                "50": '#f0fdf4',
                "100": '#dcfce7',
                "200": '#bbf7d0',
                "300": '#86efac',
                "400": '#4ade80',
                "500": '#22c55e',
                "600": '#16a34a',
                "700": '#15803d',
                "800": '#166534',
                "900": '#14532d',
                "950": '#052e16',
            },
            "emerald": {
                "50": '#ecfdf5',
                "100": '#d1fae5',
                "200": '#a7f3d0',
                "300": '#6ee7b7',
                "400": '#34d399',
                "500": '#10b981',
                "600": '#059669',
                "700": '#047857',
                "800": '#065f46',
                "900": '#064e3b',
                "950": '#022c22',
            },
            "teal": {
                "50": '#f0fdfa',
                "100": '#ccfbf1',
                "200": '#99f6e4',
                "300": '#5eead4',
                "400": '#2dd4bf',
                "500": '#14b8a6',
                "600": '#0d9488',
                "700": '#0f766e',
                "800": '#115e59',
                "900": '#134e4a',
                "950": '#042f2e',
            },
            "cyan": {
                "50": '#ecfeff',
                "100": '#cffafe',
                "200": '#a5f3fc',
                "300": '#67e8f9',
                "400": '#22d3ee',
                "500": '#06b6d4',
                "600": '#0891b2',
                "700": '#0e7490',
                "800": '#155e75',
                "900": '#164e63',
                "950": '#083344',
            },
            "sky": {
                "50": '#f0f9ff',
                "100": '#e0f2fe',
                "200": '#bae6fd',
                "300": '#7dd3fc',
                "400": '#38bdf8',
                "500": '#0ea5e9',
                "600": '#0284c7',
                "700": '#0369a1',
                "800": '#075985',
                "900": '#0c4a6e',
                "950": '#082f49',
            },
            "blue": {
                "50": '#eff6ff',
                "100": '#dbeafe',
                "200": '#bfdbfe',
                "300": '#93c5fd',
                "400": '#60a5fa',
                "500": '#3b82f6',
                "600": '#2563eb',
                "700": '#1d4ed8',
                "800": '#1e40af',
                "900": '#1e3a8a',
                "950": '#172554',
            },
            "indigo": {
                "50": '#eef2ff',
                "100": '#e0e7ff',
                "200": '#c7d2fe',
                "300": '#a5b4fc',
                "400": '#818cf8',
                "500": '#6366f1',
                "600": '#4f46e5',
                "700": '#4338ca',
                "800": '#3730a3',
                "900": '#312e81',
                "950": '#1e1b4b',
            },
            "violet": {
                "50": '#f5f3ff',
                "100": '#ede9fe',
                "200": '#ddd6fe',
                "300": '#c4b5fd',
                "400": '#a78bfa',
                "500": '#8b5cf6',
                "600": '#7c3aed',
                "700": '#6d28d9',
                "800": '#5b21b6',
                "900": '#4c1d95',
                "950": '#2e1065',
            },
            "purple": {
                "50": '#faf5ff',
                "100": '#f3e8ff',
                "200": '#e9d5ff',
                "300": '#d8b4fe',
                "400": '#c084fc',
                "500": '#a855f7',
                "600": '#9333ea',
                "700": '#7e22ce',
                "800": '#6b21a8',
                "900": '#581c87',
                "950": '#3b0764',
            },
            "fuchsia": {
                "50": '#fdf4ff',
                "100": '#fae8ff',
                "200": '#f5d0fe',
                "300": '#f0abfc',
                "400": '#e879f9',
                "500": '#d946ef',
                "600": '#c026d3',
                "700": '#a21caf',
                "800": '#86198f',
                "900": '#701a75',
                "950": '#4a044e',
            },
            "pink": {
                "50": '#fdf2f8',
                "100": '#fce7f3',
                "200": '#fbcfe8',
                "300": '#f9a8d4',
                "400": '#f472b6',
                "500": '#ec4899',
                "600": '#db2777',
                "700": '#be185d',
                "800": '#9d174d',
                "900": '#831843',
                "950": '#500724',
            },
            "rose": {
                "50": '#fff1f2',
                "100": '#ffe4e6',
                "200": '#fecdd3',
                "300": '#fda4af',
                "400": '#fb7185',
                "500": '#f43f5e',
                "600": '#e11d48',
                "700": '#be123c',
                "800": '#9f1239',
                "900": '#881337',
                "950": '#4c0519',
            }
        }
        self.spacing = {
            "px": '1px',
            "0": '0px',
            "0.5": '0.125rem',
            "1": '0.25rem',
            "1.5": '0.375rem',
            "2": '0.5rem',
            "2.5": '0.625rem',
            "3": '0.75rem',
            "3.5": '0.875rem',
            "4": '1rem',
            "5": '1.25rem',
            "6": '1.5rem',
            "7": '1.75rem',
            "8": '2rem',
            "9": '2.25rem',
            "10": '2.5rem',
            "11": '2.75rem',
            "12": '3rem',
            "14": '3.5rem',
            "16": '4rem',
            "20": '5rem',
            "24": '6rem',
            "28": '7rem',
            "32": '8rem',
            "36": '9rem',
            "40": '10rem',
            "44": '11rem',
            "48": '12rem',
            "52": '13rem',
            "56": '14rem',
            "60": '15rem',
            "64": '16rem',
            "72": '18rem',
            "80": '20rem',
            "96": '24rem',
        }
        self.classes = {
            "accentColor": {
                "auto": 'auto',
            },
            "animationNames": {
                "none": 'none',
                "spin": 'spin 1s linear var(--tw-animation-count, infinite)',
                "ping": 'ping 1s cubic-bezier(0, 0, 0.2, 1) var(--tw-animation-count, infinite)',
                "pulse": 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) var(--tw-animation-count, infinite)',
                "bounce": 'bounce 1s var(--tw-animation-count, infinite)',
            },
            # "animationDuration": {
            #     "seconds": "s",  # Duration in seconds
            #     "milliseconds": "ms"  # Duration in milliseconds
            # },
            "animationTimingFunction": {
                "ease": "ease",
                "linear": "linear",
                "easein": "ease-in",
                "easeout": "ease-out",
                "easeinout": "ease-in-out",
                "stepstart": "step-start",
                "stepend": "step-end",
                # "steps": "steps(int, start|end)",  # Custom steps
                # "cubicBezier": "cubic-bezier(n,n,n,n)"  # Custom cubic-bezier
            },
            # "animationDelay": {
            #     "seconds": "s",  # Delay in seconds
            #     "milliseconds": "ms"  # Delay in milliseconds
            # },
            "animationIterationCount": {
                "infinite": "infinite",
                # "number": "number"  # Specific number of iterations
            },
            "animationDirection": {
                "normal": "normal",
                "reverse": "reverse",
                "alternate": "alternate",
                "alternateReverse": "alternate-reverse"
            },
            "animationFillMode": {
                "none": "none",
                "forwards": "forwards",
                "backwards": "backwards",
                "both": "both"
            },
            "animationPlayState": {
                "running": "running",
                "paused": "paused"
            },
            "aria": {
                "busy": 'busy="true"',
                "checked": 'checked="true"',
                "disabled": 'disabled="true"',
                "expanded": 'expanded="true"',
                "hidden": 'hidden="true"',
                "pressed": 'pressed="true"',
                "readonly": 'readonly="true"',
                "required": 'required="true"',
                "selected": 'selected="true"',
            },
            "aspectRatio": {
                "auto": 'auto',
                "square": '1 / 1',
                "video": '16 / 9',
            },
            "backdrop-filter": {
                "blur": {
                    "sm": "blur(4px)",
                    "DEFAULT": "blur(8px)",
                    "md": "blur(12px)",
                    "lg": "blur(16px)",
                    "xl": "blur(24px)",
                    "2xl": "blur(40px)",
                    "3xl": "blur(64px)"
                },
                "brightness": {
                    "0": "brightness(0)",
                    "50": "brightness(.5)",
                    "75": "brightness(.75)",
                    "90": "brightness(.9)",
                    "95": "brightness(.95)",
                    "100": "brightness(1)",
                    "105": "brightness(1.05)",
                    "110": "brightness(1.1)",
                    "125": "brightness(1.25)",
                    "150": "brightness(1.5)",
                    "200": "brightness(2)"
                },
                "contrast": {
                    "0": "contrast(0)",
                    "50": "contrast(.5)",
                    "75": "contrast(.75)",
                    "100": "contrast(1)",
                    "125": "contrast(1.25)",
                    "150": "contrast(1.5)",
                    "200": "contrast(2)"
                },
                "grayscale": {
                    "0": "grayscale(0)",
                    "DEFAULT": "grayscale(1)"
                },
                "hue-rotate": {
                    "0": "hue-rotate(0deg)",
                    "15": "hue-rotate(15deg)",
                    "30": "hue-rotate(30deg)",
                    "60": "hue-rotate(60deg)",
                    "90": "hue-rotate(90deg)",
                    "180": "hue-rotate(180deg)"
                },
                "invert": {
                    "0": "invert(0)",
                    "DEFAULT": "invert(1)"
                },
                "opacity": {
                    "0": "opacity(0)",
                    "5": "opacity(.05)",
                    "10": "opacity(.1)",
                    "20": "opacity(.2)",
                    "25": "opacity(.25)",
                    "30": "opacity(.3)",
                    "40": "opacity(.4)",
                    "50": "opacity(.5)",
                    "60": "opacity(.6)",
                    "70": "opacity(.7)",
                    "75": "opacity(.75)",
                    "80": "opacity(.8)",
                    "90": "opacity(.9)",
                    "95": "opacity(.95)",
                    "100": "opacity(1)"
                },
                "saturate": {
                    "0": "saturate(0)",
                    "50": "saturate(.5)",
                    "100": "saturate(1)",
                    "150": "saturate(1.5)",
                    "200": "saturate(2)"
                },
                "sepia": {
                    "0": "sepia(0)",
                    "DEFAULT": "sepia(1)"
                }
            },
            "backgroundImage": {
                "none": 'none',
                "gradient": {
                    "to": {
                        "t": "linear-gradient(to top, var(--tw-gradient-stops))",
                        "tr": "linear-gradient(to top right, var(--tw-gradient-stops))",
                        "r": "linear-gradient(to right, var(--tw-gradient-stops))",
                        "br": "linear-gradient(to bottom right, var(--tw-gradient-stops))",
                        "b": "linear-gradient(to bottom, var(--tw-gradient-stops))",
                        "bl": "linear-gradient(to bottom left, var(--tw-gradient-stops))",
                        "l": "linear-gradient(to left, var(--tw-gradient-stops))",
                        "tl": "linear-gradient(to top left, var(--tw-gradient-stops))"
                    }
                }
            },
            "backgroundPosition": {
                "bottom": 'bottom',
                "center": 'center',
                "left": 'left',
                'left-bottom': 'left bottom',
                'left-top': 'left top',
                "right": 'right',
                'right-bottom': 'right bottom',
                'right-top': 'right top',
                "top": 'top',
            },
            "backgroundSize": {
                "auto": 'auto',
                "cover": 'cover',
                "contain": 'contain',
            },
            "break": {
                "normal": [{"word-break": "normal", "overflow-wrap": "normal"}],
                "words": [{"overflow-wrap": "break-word"}],
                "all": [{"word-break": "break-all"}],
                "keep": [{"word-break": "keep-all"}],
            },
            "borderRadius": {
                "none": '0px',
                "sm": '0.125rem',
                "DEFAULT": '0.25rem',
                "md": '0.375rem',
                "lg": '0.5rem',
                "xl": '0.75rem',
                '2xl': '1rem',
                '3xl': '1.5rem',
                "full": '9999px',
            },
            "borderWidth": {
                "DEFAULT": '1px',
                "0": '0px',
                "2": '2px',
                "4": '4px',
                "8": '8px',
                "x": {
                    "0": [{"border-left-width": "0px", "border-right-width": "0px"}],
                    "2": [{"border-left-width": "2px", "border-right-width": "2px"}],
                    "4": [{"border-left-width": "4px", "border-right-width": "4px"}],
                    "8": [{"border-left-width": "8px", "border-right-width": "8px"}],
                    "DEFAULT": [{"border-left-width": "1px", "border-right-width": "1px"}],
                },
                "y": {
                    "0": [{"border-top-width": "0px", "border-bottom-width": "0px"}],
                    "2": [{"border-top-width": "2px", "border-bottom-width": "2px"}],
                    "4": [{"border-top-width": "4px", "border-bottom-width": "4px"}],
                    "8": [{"border-top-width": "8px", "border-bottom-width": "8px"}],
                    "DEFAULT": [{"border-top-width": "1px", "border-bottom-width": "1px"}]
                },
                "s": {
                    "0": [{"border-inline-start-width": "0px"}],
                    "2": [{"border-inline-start-width": "2px"}],
                    "4": [{"border-inline-start-width": "4px"}],
                    "8": [{"border-inline-start-width": "8px"}],
                    "DEFAULT": [{"border-inline-start-width": "1px"}]
                },
                "e": {
                    "0": [{"border-inline-end-width": "0px"}],
                    "2": [{"border-inline-end-width": "2px"}],
                    "4": [{"border-inline-end-width": "4px"}],
                    "8": [{"border-inline-end-width": "8px"}],
                    "DEFAULT": [{"border-inline-end-width": "1px"}]
                },
                "t": {
                    "0": [{"border-top-width": "0px"}],
                    "2": [{"border-top-width": "2px"}],
                    "4": [{"border-top-width": "4px"}],
                    "8": [{"border-top-width": "8px"}],
                    "DEFAULT": [{"border-top-width": "1px"}]
                },
                "r": {
                    "0": [{"border-right-width": "0px"}],
                    "2": [{"border-right-width": "2px"}],
                    "4": [{"border-right-width": "4px"}],
                    "8": [{"border-right-width": "8px"}],
                    "DEFAULT": [{"border-right-width": "1px"}]
                },
                "b": {
                    "0": [{"border-bottom-width": "0px"}],
                    "2": [{"border-bottom-width": "2px"}],
                    "4": [{"border-bottom-width": "4px"}],
                    "8": [{"border-bottom-width": "8px"}],
                    "DEFAULT": [{"border-bottom-width": "1px"}]
                },
                "l": {
                    "0": [{"border-left-width": "0px"}],
                    "2": [{"border-left-width": "2px"}],
                    "4": [{"border-left-width": "4px"}],
                    "8": [{"border-left-width": "8px"}],
                    "DEFAULT": [{"border-left-width": "1px"}]
                }

            },
            "boxShadow": {
                "sm": '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                "DEFAULT": '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
                "md": '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
                "lg": '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
                "xl": '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
                '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
                "inner": 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
                "none": 'none',
            },
            "brightness": {
                "0": '0',
                '50': '.5',
                "75": '.75',
                "90": '.9',
                "95": '.95',
                "100": '1',
                "105": '1.05',
                "110": '1.1',
                "125": '1.25',
                "150": '1.5',
                "200": '2',
            },
            "colors": self.colors,
            "columns": {
                "auto": 'auto',
                "1": '1',
                "2": '2',
                "3": '3',
                "4": '4',
                "5": '5',
                "6": '6',
                "7": '7',
                "8": '8',
                "9": '9',
                "10": '10',
                "11": '11',
                "12": '12',
                '3xs': '16rem',
                '2xs': '18rem',
                "xs": '20rem',
                "sm": '24rem',
                "md": '28rem',
                "lg": '32rem',
                "xl": '36rem',
                '2xl': '42rem',
                '3xl': '48rem',
                '4xl': '56rem',
                '5xl': '64rem',
                '6xl': '72rem',
                '7xl': '80rem',
            },
            'container': {},
            'content': {
                'none': 'none',
            },
            'contrast': {
                '0': '0',
                '50': '.5',
                '75': '.75',
                '100': '1',
                '125': '1.25',
                '150': '1.5',
                '200': '2',
            },
            'cursor': {
                'auto': 'auto',
                'default': 'default',
                'DEFAULT': 'default',
                'pointer': 'pointer',
                'wait': 'wait',
                'text': 'text',
                'move': 'move',
                'help': 'help',
                'not-allowed': 'not-allowed',
                'none': 'none',
                'context-menu': 'context-menu',
                'progress': 'progress',
                'cell': 'cell',
                'crosshair': 'crosshair',
                'vertical-text': 'vertical-text',
                'alias': 'alias',
                'copy': 'copy',
                'no-drop': 'no-drop',
                'grab': 'grab',
                'grabbing': 'grabbing',
                'all-scroll': 'all-scroll',
                'col-resize': 'col-resize',
                'row-resize': 'row-resize',
                'n-resize': 'n-resize',
                'e-resize': 'e-resize',
                's-resize': 's-resize',
                'w-resize': 'w-resize',
                'ne-resize': 'ne-resize',
                'nw-resize': 'nw-resize',
                'se-resize': 'se-resize',
                'sw-resize': 'sw-resize',
                'ew-resize': 'ew-resize',
                'ns-resize': 'ns-resize',
                'nesw-resize': 'nesw-resize',
                'nwse-resize': 'nwse-resize',
                'zoom-in': 'zoom-in',
                'zoom-out': 'zoom-out',
            },
            "dropShadow": {
                "sm": '0 1px 1px rgb(0 0 0 / 0.05)',
                "DEFAULT": ['0 1px 2px rgb(0 0 0 / 0.1)', '0 1px 1px rgb(0 0 0 / 0.06)'],
                "md": ['0 4px 3px rgb(0 0 0 / 0.07)', '0 2px 2px rgb(0 0 0 / 0.06)'],
                "lg": ['0 10px 8px rgb(0 0 0 / 0.04)', '0 4px 3px rgb(0 0 0 / 0.1)'],
                "xl": ['0 20px 13px rgb(0 0 0 / 0.03)', '0 8px 5px rgb(0 0 0 / 0.08)'],
                '2xl': '0 25px 25px rgb(0 0 0 / 0.15)',
                "none": '0 0 #0000',
            },
            "display": {
                "block": "block",
                "inline": "inline",
                "inline-block": "inline-block",
                "flex": "flex",
                "inline-flex": "inline-flex",
                "grid": "grid",
                "inline-grid": "inline-grid",
                "table": "table",
                "inline-table": "inline-table",
                "table-row": "table-row",
                "table-cell": "table-cell",
                "none": "none",
                "hidden": "none"
            },
            "fill": self.colors,
            "filter": {
                "blur": {
                    "sm": "blur(4px)",
                    "DEFAULT": "blur(8px)",
                    "md": "blur(12px)",
                    "lg": "blur(16px)",
                    "xl": "blur(24px)",
                    "2xl": "blur(40px)",
                    "3xl": "blur(64px)"
                },
                "brightness": {
                    "0": "brightness(0)",
                    "50": "brightness(.5)",
                    "75": "brightness(.75)",
                    "90": "brightness(.9)",
                    "95": "brightness(.95)",
                    "100": "brightness(1)",
                    "105": "brightness(1.05)",
                    "110": "brightness(1.1)",
                    "125": "brightness(1.25)",
                    "150": "brightness(1.5)",
                    "200": "brightness(2)"
                },
                "contrast": {
                    "0": "contrast(0)",
                    "50": "contrast(.5)",
                    "75": "contrast(.75)",
                    "100": "contrast(1)",
                    "125": "contrast(1.25)",
                    "150": "contrast(1.5)",
                    "200": "contrast(2)"
                },
                "drop-shadow": {
                    "sm": "drop-shadow(0 1px 1px rgba(0,0,0,0.05))",
                    "DEFAULT": "drop-shadow(0 1px 2px rgba(0,0,0,0.1))",
                    "md": "drop-shadow(0 4px 3px rgba(0,0,0,0.07))",
                    "lg": "drop-shadow(0 10px 8px rgba(0,0,0,0.04))",
                    "xl": "drop-shadow(0 20px 13px rgba(0,0,0,0.03))",
                    "2xl": "drop-shadow(0 25px 25px rgba(0,0,0,0.15))",
                    "none": "drop-shadow(0 0 #0000)"
                },
                "grayscale": {
                    "0": "grayscale(0)",
                    "DEFAULT": "grayscale(1)"
                },
                "hue-rotate": {
                    "0": "hue-rotate(0deg)",
                    "15": "hue-rotate(15deg)",
                    "30": "hue-rotate(30deg)",
                    "60": "hue-rotate(60deg)",
                    "90": "hue-rotate(90deg)",
                    "180": "hue-rotate(180deg)"
                },
                "invert": {
                    "0": "invert(0)",
                    "DEFAULT": "invert(1)"
                },
                "saturate": {
                    "0": "saturate(0)",
                    "50": "saturate(.5)",
                    "100": "saturate(1)",
                    "150": "saturate(1.5)",
                    "200": "saturate(2)"
                },
                "sepia": {
                    "0": "sepia(0)",
                    "DEFAULT": "sepia(1)"
                }
            },
            "flex": {
                "1": '1 1 0%',
                "auto": '1 1 auto',
                "initial": '0 1 auto',
                "none": 'none',
            },
            "flexBasis": {
                "auto": 'auto',
                '1/2': '50%',
                '1/3': '33.333333%',
                '2/3': '66.666667%',
                '1/4': '25%',
                '2/4': '50%',
                '3/4': '75%',
                '1/5': '20%',
                '2/5': '40%',
                '3/5': '60%',
                '4/5': '80%',
                '1/6': '16.666667%',
                '2/6': '33.333333%',
                '3/6': '50%',
                '4/6': '66.666667%',
                '5/6': '83.333333%',
                '1/12': '8.333333%',
                '2/12': '16.666667%',
                '3/12': '25%',
                '4/12': '33.333333%',
                '5/12': '41.666667%',
                '6/12': '50%',
                '7/12': '58.333333%',
                '8/12': '66.666667%',
                '9/12': '75%',
                '10/12': '83.333333%',
                '11/12': '91.666667%',
                "full": '100%',
            },
            "flexGrow": {
                "0": '0',
                "DEFAULT": '1',
            },
            "flexShrink": {
                "0": '0',
                "DEFAULT": '1',
            },
            "fontFamily": {
                "sans": [
                    'ui-sans-serif',
                    'system-ui',
                    'sans-serif',
                    '"Apple Color Emoji"',
                    '"Segoe UI Emoji"',
                    '"Segoe UI Symbol"',
                    '"Noto Color Emoji"',
                ],
                "serif": ['ui-serif', 'Georgia', 'Cambria', '"Times New Roman"', 'Times', 'serif'],
                "mono": [
                    'ui-monospace',
                    'SFMono-Regular',
                    'Menlo',
                    'Monaco',
                    'Consolas',
                    '"Liberation Mono"',
                    '"Courier New"',
                    'monospace',
                ],
            },
            "fontSize": {
                "xs": ['0.75rem', {"lineHeight": '1rem'}],
                "sm": ['0.875rem', {"lineHeight": '1.25rem'}],
                "base": ['1rem', {"lineHeight": '1.5rem'}],
                "lg": ['1.125rem', {"lineHeight": '1.75rem'}],
                "xl": ['1.25rem', {"lineHeight": '1.75rem'}],
                '2xl': ['1.5rem', {"lineHeight": '2rem'}],
                '3xl': ['1.875rem', {"lineHeight": '2.25rem'}],
                '4xl': ['2.25rem', {"lineHeight": '2.5rem'}],
                '5xl': ['3rem', {"lineHeight": '1'}],
                '6xl': ['3.75rem', {"lineHeight": '1'}],
                '7xl': ['4.5rem', {"lineHeight": '1'}],
                '8xl': ['6rem', {"lineHeight": '1'}],
                '9xl': ['8rem', {"lineHeight": '1'}],
            },
            "fontSmoothing": {
                "antialiased": {
                    "-webkit-font-smoothing": "antialiased",
                    "-moz-osx-font-smoothing": "grayscale"
                },
                "subpixel-antialiased": {
                    "-webkit-font-smoothing": "auto",
                    "-moz-osx-font-smoothing": "auto"
                }
            },
            "fontStyle": {
                "italic": "italic",
                'oblique': "oblique",
                "not-italic": "normal"
            },
            "fontWeight": {
                "thin": '100',
                "extralight": '200',
                "light": '300',
                "normal": '400',
                "medium": '500',
                "semibold": '600',
                "bold": '700',
                "extrabold": '800',
                "black": '900',
            },
            "gradientColorStopPositions": {
                '0%': '0%',
                '5%': '5%',
                '10%': '10%',
                '15%': '15%',
                '20%': '20%',
                '25%': '25%',
                '30%': '30%',
                '35%': '35%',
                '40%': '40%',
                '45%': '45%',
                '50%': '50%',
                '55%': '55%',
                '60%': '60%',
                '65%': '65%',
                '70%': '70%',
                '75%': '75%',
                '80%': '80%',
                '85%': '85%',
                '90%': '90%',
                '95%': '95%',
                '100%': '100%',
            },
            "grayscale": {
                "0": '0',
                "DEFAULT": '100%',
            },
            "gridAutoColumns": {
                "auto": 'auto',
                "min": 'min-content',
                "max": 'max-content',
                "fr": 'minmax(0, 1fr)',
            },
            "gridAutoRows": {
                "auto": 'auto',
                "min": 'min-content',
                "max": 'max-content',
                "fr": 'minmax(0, 1fr)',
            },
            "gridColumn": {
                "auto": 'auto',
                'span-1': 'span 1 / span 1',
                'span-2': 'span 2 / span 2',
                'span-3': 'span 3 / span 3',
                'span-4': 'span 4 / span 4',
                'span-5': 'span 5 / span 5',
                'span-6': 'span 6 / span 6',
                'span-7': 'span 7 / span 7',
                'span-8': 'span 8 / span 8',
                'span-9': 'span 9 / span 9',
                'span-10': 'span 10 / span 10',
                'span-11': 'span 11 / span 11',
                'span-12': 'span 12 / span 12',
                'span-full': '1 / -1',
            },
            "gridColumnEnd": {
                "auto": 'auto',
                "1": '1',
                "2": '2',
                "3": '3',
                "4": '4',
                "5": '5',
                "6": '6',
                "7": '7',
                "8": '8',
                "9": '9',
                "10": '10',
                "11": '11',
                "12": '12',
                "13": '13',
            },
            "gridColumnStart": {
                "auto": 'auto',
                "1": '1',
                "2": '2',
                "3": '3',
                "4": '4',
                "5": '5',
                "6": '6',
                "7": '7',
                "8": '8',
                "9": '9',
                "10": '10',
                "11": '11',
                "12": '12',
                "13": '13',
            },
            "gridRow": {
                "auto": 'auto',
                'span-1': 'span 1 / span 1',
                'span-2': 'span 2 / span 2',
                'span-3': 'span 3 / span 3',
                'span-4': 'span 4 / span 4',
                'span-5': 'span 5 / span 5',
                'span-6': 'span 6 / span 6',
                'span-7': 'span 7 / span 7',
                'span-8': 'span 8 / span 8',
                'span-9': 'span 9 / span 9',
                'span-10': 'span 10 / span 10',
                'span-11': 'span 11 / span 11',
                'span-12': 'span 12 / span 12',
                'span-full': '1 / -1',
            },
            "gridRowEnd": {
                "auto": 'auto',
                "1": '1',
                "2": '2',
                "3": '3',
                "4": '4',
                "5": '5',
                "6": '6',
                "7": '7',
                "8": '8',
                "9": '9',
                "10": '10',
                "11": '11',
                "12": '12',
                "13": '13',
            },
            "gridRowStart": {
                "auto": 'auto',
                "1": '1',
                "2": '2',
                "3": '3',
                "4": '4',
                "5": '5',
                "6": '6',
                "7": '7',
                "8": '8',
                "9": '9',
                "10": '10',
                "11": '11',
                "12": '12',
                "13": '13',
            },
            "gridTemplateColumns": {
                "none": 'none',
                "subgrid": 'subgrid',
                "1": 'repeat(1, minmax(0, 1fr))',
                "2": 'repeat(2, minmax(0, 1fr))',
                "3": 'repeat(3, minmax(0, 1fr))',
                "4": 'repeat(4, minmax(0, 1fr))',
                "5": 'repeat(5, minmax(0, 1fr))',
                "6": 'repeat(6, minmax(0, 1fr))',
                "7": 'repeat(7, minmax(0, 1fr))',
                "8": 'repeat(8, minmax(0, 1fr))',
                "9": 'repeat(9, minmax(0, 1fr))',
                "10": 'repeat(10, minmax(0, 1fr))',
                "11": 'repeat(11, minmax(0, 1fr))',
                "12": 'repeat(12, minmax(0, 1fr))',
            },
            "gridTemplateRows": {
                "none": 'none',
                "subgrid": 'subgrid',
                "1": 'repeat(1, minmax(0, 1fr))',
                "2": 'repeat(2, minmax(0, 1fr))',
                "3": 'repeat(3, minmax(0, 1fr))',
                "4": 'repeat(4, minmax(0, 1fr))',
                "5": 'repeat(5, minmax(0, 1fr))',
                "6": 'repeat(6, minmax(0, 1fr))',
                "7": 'repeat(7, minmax(0, 1fr))',
                "8": 'repeat(8, minmax(0, 1fr))',
                "9": 'repeat(9, minmax(0, 1fr))',
                "10": 'repeat(10, minmax(0, 1fr))',
                "11": 'repeat(11, minmax(0, 1fr))',
                "12": 'repeat(12, minmax(0, 1fr))',
            },
            "height": {
                "auto": 'auto',
                '1/2': '50%',
                '1/3': '33.333333%',
                '2/3': '66.666667%',
                '1/4': '25%',
                '2/4': '50%',
                '3/4': '75%',
                '1/5': '20%',
                '2/5': '40%',
                '3/5': '60%',
                '4/5': '80%',
                '1/6': '16.666667%',
                '2/6': '33.333333%',
                '3/6': '50%',
                '4/6': '66.666667%',
                '5/6': '83.333333%',
                "full": '100%',
                "screen": '100vh',
                "svh": '100svh',
                "lvh": '100lvh',
                "dvh": '100dvh',
                "min": 'min-content',
                "max": 'max-content',
                "fit": 'fit-content',
            },
            "hueRotate": {
                "0": '0deg',
                "15": '15deg',
                "30": '30deg',
                "60": '60deg',
                "90": '90deg',
                "180": '180deg',
            },
            "inset": {
                "auto": 'auto',
                '1/2': '50%',
                '1/3': '33.333333%',
                '2/3': '66.666667%',
                '1/4': '25%',
                '2/4': '50%',
                '3/4': '75%',
                "full": '100%',
            },
            "invert": {
                "0": '0',
                "DEFAULT": '100%',
            },
            "keyframes": {
                "spin": {
                    "to": {
                        "transform": 'rotate(360deg)',
                    },
                },
                "ping": {
                    '75%, 100%': {
                        "transform": 'scale(2)',
                        "opacity": '0',
                    },
                },
                "pulse": {
                    '50%': {
                        "opacity": '.5',
                    },
                },
                "bounce": {
                    '0%, 100%': {
                        "transform": 'translateY(-25%)',
                        "animationTimingFunction": 'cubic-bezier(0.8,0,1,1)',
                    },
                    '50%': {
                        "transform": 'none',
                        "animationTimingFunction": 'cubic-bezier(0,0,0.2,1)',
                    },
                },
            },
            "letterSpacing": {
                "tighter": '-0.05em',
                "tight": '-0.025em',
                "normal": '0em',
                "wide": '0.025em',
                "wider": '0.05em',
                "widest": '0.1em',
            },
            "leading": {
                "3": ".75rem",
                "4": "1rem",
                "5": "1.25rem",
                "6": "1.5rem",
                "7": "1.75rem",
                "8": "2rem",
                "9": "2.25rem",
                "10": "2.5rem",
                "none": "1",
                "tight": "1.25",
                "snug": "1.375",
                "normal": "1.5",
                "relaxed": "1.625",
                "loose": "2"
            },
            "lineHeight": {
                "none": '1',
                "tight": '1.25',
                "snug": '1.375',
                "normal": '1.5',
                "relaxed": '1.625',
                "loose": '2',
                "3": '.75rem',
                "4": '1rem',
                "5": '1.25rem',
                "6": '1.5rem',
                "7": '1.75rem',
                "8": '2rem',
                "9": '2.25rem',
                "10": '2.5rem',
            },
            "listStyleType": {
                "none": 'none',
                "disc": 'disc',
                "decimal": 'decimal',
            },
            "listStyleImage": {
                "none": 'none',
            },
            "margin": {
                "auto": 'auto',
            },
            "lineClamp": {
                "1": '1',
                "2": '2',
                "3": '3',
                "4": '4',
                "5": '5',
                "6": '6',
            },
            "maxHeight": {
                "none": 'none',
                "full": '100%',
                "screen": '100vh',
                "svh": '100svh',
                "lvh": '100lvh',
                "dvh": '100dvh',
                "min": 'min-content',
                "max": 'max-content',
                "fit": 'fit-content',
            },
            "maxWidth": {
                "none": 'none',
                "xs": '20rem',
                "sm": '24rem',
                "md": '28rem',
                "lg": '32rem',
                "xl": '36rem',
                '2xl': '42rem',
                '3xl': '48rem',
                '4xl': '56rem',
                '5xl': '64rem',
                '6xl': '72rem',
                '7xl': '80rem',
                "full": '100%',
                "min": 'min-content',
                "max": 'max-content',
                "fit": 'fit-content',
                "prose": '65ch',
                # ...
                # breakpoints(theme('screens')),
            },
            "minHeight": {
                "full": '100%',
                "screen": '100vh',
                "svh": '100svh',
                "lvh": '100lvh',
                "dvh": '100dvh',
                "min": 'min-content',
                "max": 'max-content',
                "fit": 'fit-content',
            },
            "minWidth": {
                "full": '100%',
                "min": 'min-content',
                "max": 'max-content',
                "fit": 'fit-content',
            },
            "objectPosition": {
                "bottom": 'bottom',
                "center": 'center',
                "left": 'left',
                'left-bottom': 'left bottom',
                'left-top': 'left top',
                "right": 'right',
                'right-bottom': 'right bottom',
                'right-top': 'right top',
                "top": 'top',
            },
            "opacity": {
                "0": '0',
                "5": '0.05',
                "10": '0.1',
                "15": '0.15',
                "20": '0.2',
                "25": '0.25',
                "30": '0.3',
                "35": '0.35',
                "40": '0.4',
                "45": '0.45',
                "50": '0.5',
                "55": '0.55',
                "60": '0.6',
                "65": '0.65',
                "70": '0.7',
                "75": '0.75',
                "80": '0.8',
                "85": '0.85',
                "90": '0.9',
                "95": '0.95',
                "100": '1',
            },
            "order": {
                "first": '-9999',
                "last": '9999',
                "none": '0',
                "1": '1',
                "2": '2',
                "3": '3',
                "4": '4',
                "5": '5',
                "6": '6',
                "7": '7',
                "8": '8',
                "9": '9',
                "10": '10',
                "11": '11',
                "12": '12',
            },
            "overflow": {
                "auto": "auto",
                "hidden": "hidden",
                "clip": "clip",
                "visible": "visible",
                "scroll": "scroll",
                "x": {
                    "auto": "auto",
                    "hidden": "hidden",
                    "clip": "clip",
                    "visible": "visible",
                    "scroll": "scroll"
                },
                "y": {
                    "auto": "auto",
                    "hidden": "hidden",
                    "clip": "clip",
                    "visible": "visible",
                    "scroll": "scroll"
                }
            },
            "outlineOffset": {
                "0": '0px',
                "1": '1px',
                "2": '2px',
                "4": '4px',
                "8": '8px',
            },
            "outlineWidth": {
                "0": '0px',
                "1": '1px',
                "2": '2px',
                "4": '4px',
                "8": '8px',
            },
            "position": {
                'static': 'static',
                'relative': 'relative',
                'absolute': 'absolute',
                'fixed': 'fixed',
                'sticky': 'sticky'
            },
            "ringColor": {
                "DEFAULT": '#3b82f6'  # theme('colors.blue.500', '#3b82f6'),
            },
            "ringOffsetWidth": {
                "0": '0px',
                "1": '1px',
                "2": '2px',
                "4": '4px',
                "8": '8px',
            },
            "ringOpacity": {
                "DEFAULT": '0.5',
            },
            "ringWidth": {
                "DEFAULT": '3px',
                "0": '0px',
                "1": '1px',
                "2": '2px',
                "4": '4px',
                "8": '8px',
            },
            "rotate": {
                "0": '0deg',
                "1": '1deg',
                "2": '2deg',
                "3": '3deg',
                "6": '6deg',
                "12": '12deg',
                "45": '45deg',
                "90": '90deg',
                "180": '180deg',
            },
            "saturate": {
                "0": '0',
                "50": '.5',
                "100": '1',
                "150": '1.5',
                "200": '2',
            },
            "scale": {
                "0": '0',
                "50": '.5',
                "75": '.75',
                "90": '.9',
                "95": '.95',
                "100": '1',
                "105": '1.05',
                "110": '1.1',
                "125": '1.25',
                "150": '1.5',
            },
            "screens": {
                "sm": '640px',
                "md": '768px',
                "lg": '1024px',
                "xl": '1280px',
                '2xl': '1536px',
            },
            "scroll": {
                "auto": "auto",
                "smooth": "smooth",
            },
            "sepia": {
                "0": '0',
                "DEFAULT": '100%',
            },
            "skew": {
                "0": '0deg',
                "1": '1deg',
                "2": '2deg',
                "3": '3deg',
                "6": '6deg',
                "12": '12deg',
            },
            "spacing": {
                "px": '1px',
                "0": '0px',
                "0.5": '0.125rem',
                "1": '0.25rem',
                "1.5": '0.375rem',
                "2": '0.5rem',
                "2.5": '0.625rem',
                "3": '0.75rem',
                "3.5": '0.875rem',
                "4": '1rem',
                "5": '1.25rem',
                "6": '1.5rem',
                "7": '1.75rem',
                "8": '2rem',
                "9": '2.25rem',
                "10": '2.5rem',
                "11": '2.75rem',
                "12": '3rem',
                "14": '3.5rem',
                "16": '4rem',
                "20": '5rem',
                "24": '6rem',
                "28": '7rem',
                "32": '8rem',
                "36": '9rem',
                "40": '10rem',
                "44": '11rem',
                "48": '12rem',
                "52": '13rem',
                "56": '14rem',
                "60": '15rem',
                "64": '16rem',
                "72": '18rem',
                "80": '20rem',
                "96": '24rem',
            },
            "srOnly": {
                "DEFAULT": {
                    "position": "absolute",
                    "width": "1px",
                    "height": "1px",
                    "padding": "0",
                    "margin": "-1px",
                    "overflow": "hidden",
                    "clip": "rect(0, 0, 0, 0)",
                    "white-space": "nowrap",
                    "border-width": "0"
                },
            },
            "stroke": {
                "none": 'none',
            },
            "strokeWidth": {
                "0": '0',
                "1": '1',
                "2": '2',
            },
            "supports": {},
            "data": {},
            "textAlign": {
                "left": "left",  # Align text to the left
                "right": "right",  # Align text to the right
                "center": "center",  # Center-align text
                "justify": "justify",  # Justify text
                "initial": "initial",  # Sets the text-align property to its DEFAULT value
                "inherit": "inherit"  # Inherits the text-align property from its parent element
            },
            "textDecorationThickness": {
                "auto": 'auto',
                'from-font': 'from-font',
                "0": '0px',
                "1": '1px',
                "2": '2px',
                "4": '4px',
                "8": '8px',
            },
            "textDecoration": {
                "none": "none",
                "underline": "underline",
                "overline": "overline",
                "line-through": "line-through",
                "blink": "blink",  # Note: Blink is not widely supported
            },
            "textTransform": {
                "uppercase": "uppercase",
                "lowercase": "lowercase",
                "capitalize": "capitalize",
                "normal-case": "none"
            },
            "textWrap": {
                "wrap": "wrap",
                "nowrap": "nowrap",
                "balance": "balance",
                "pretty": "pretty"
            },
            "textUnderlineOffset": {
                "auto": 'auto',
                "0": '0px',
                "1": '1px',
                "2": '2px',
                "4": '4px',
                "8": '8px',
            },
            "transformOrigin": {
                "center": 'center',
                "top": 'top',
                'top-right': 'top right',
                "right": 'right',
                'bottom-right': 'bottom right',
                "bottom": 'bottom',
                'bottom-left': 'bottom left',
                "left": 'left',
                'top-left': 'top left',
            },
            "transitionDelay": {
                "0": '0s',
                "75": '75ms',
                "100": '100ms',
                "150": '150ms',
                "200": '200ms',
                "300": '300ms',
                "500": '500ms',
                "700": '700ms',
                "1000": '1000ms',
            },
            "transitionDuration": {
                "DEFAULT": '150ms',
                "0": '0s',
                "75": '75ms',
                "100": '100ms',
                "150": '150ms',
                "200": '200ms',
                "300": '300ms',
                "500": '500ms',
                "700": '700ms',
                "1000": '1000ms',
            },
            "transitionProperty": {
                "none": [{"transition-property": "none"}],
                "all": [{"transition-property": "all"}],
                "timingFunction": [{"transition-timing-function": "cubic-bezier(0.4, 0, 0.2, 1)"}],
                "duration": [{"transition-duration": "150ms"}],
                "transition": [{
                    "transition-property": "color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter",
                    "transition-timing-function": "cubic-bezier(0.4, 0, 0.2, 1)",
                    "transition-duration": "150ms"
                }],
                "colors": [{
                    "transition-property": "color, background-color, border-color, text-decoration-color, fill, stroke",
                    "transition-timing-function": "cubic-bezier(0.4, 0, 0.2, 1)",
                    "transition-duration": "150ms"
                }],
                "opacity": [{
                    "transition-property": "opacity",
                    "transition-timing-function": "cubic-bezier(0.4, 0, 0.2, 1)",
                    "transition-duration": "150ms"
                }],
                "shadow": [{
                    "transition-property": "box-shadow",
                    "transition-timing-function": "cubic-bezier(0.4, 0, 0.2, 1)",
                    "transition-duration": "150ms"
                }],
                "transform": [{
                    "transition-property": "transform",
                    "transition-timing-function": "cubic-bezier(0.4, 0, 0.2, 1)",
                    "transition-duration": "150ms"
                }],
            },
            "transitionTimingFunction": {
                "DEFAULT": 'cubic-bezier(0.4, 0, 0.2, 1)',
                "linear": 'linear',
                "in": 'cubic-bezier(0.4, 0, 1, 1)',
                "out": 'cubic-bezier(0, 0, 0.2, 1)',
                'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
            },
            "translate": {
                '1/2': '50%',
                '1/3': '33.333333%',
                '2/3': '66.666667%',
                '1/4': '25%',
                '2/4': '50%',
                '3/4': '75%',
                "full": '100%',
            },
            "size": {
                "auto": 'auto',
                '1/2': '50%',
                '1/3': '33.333333%',
                '2/3': '66.666667%',
                '1/4': '25%',
                '2/4': '50%',
                '3/4': '75%',
                '1/5': '20%',
                '2/5': '40%',
                '3/5': '60%',
                '4/5': '80%',
                '1/6': '16.666667%',
                '2/6': '33.333333%',
                '3/6': '50%',
                '4/6': '66.666667%',
                '5/6': '83.333333%',
                '1/12': '8.333333%',
                '2/12': '16.666667%',
                '3/12': '25%',
                '4/12': '33.333333%',
                '5/12': '41.666667%',
                '6/12': '50%',
                '7/12': '58.333333%',
                '8/12': '66.666667%',
                '9/12': '75%',
                '10/12': '83.333333%',
                '11/12': '91.666667%',
                "full": '100%',
                "min": 'min-content',
                "max": 'max-content',
                "fit": 'fit-content',
            },
            "width": {
                "auto": 'auto',
                '1/2': '50%',
                '1/3': '33.333333%',
                '2/3': '66.666667%',
                '1/4': '25%',
                '2/4': '50%',
                '3/4': '75%',
                '1/5': '20%',
                '2/5': '40%',
                '3/5': '60%',
                '4/5': '80%',
                '1/6': '16.666667%',
                '2/6': '33.333333%',
                '3/6': '50%',
                '4/6': '66.666667%',
                '5/6': '83.333333%',
                '1/12': '8.333333%',
                '2/12': '16.666667%',
                '3/12': '25%',
                '4/12': '33.333333%',
                '5/12': '41.666667%',
                '6/12': '50%',
                '7/12': '58.333333%',
                '8/12': '66.666667%',
                '9/12': '75%',
                '10/12': '83.333333%',
                '11/12': '91.666667%',
                "full": '100%',
                "screen": '100vw',
                "svw": '100svw',
                "lvw": '100lvw',
                "dvw": '100dvw',
                "min": 'min-content',
                "max": 'max-content',
                "fit": 'fit-content',
            },
            "willChange": {
                "auto": 'auto',
                "scroll": 'scroll-position',
                "contents": 'contents',
                "transform": 'transform',
            },
            "zIndex": {
                "auto": 'auto',
                "0": '0',
                "10": '10',
                "20": '20',
                "30": '30',
                "40": '40',
                "50": '50',
            },
        }
        self.copy_classes = [
            ["backgroundColor", "colors"],
            ["backgroundOpacity", "opacity"],
            ["borderColor", "colors"],
            ["borderOpacity", "opacity"],
            ["borderSpacing", "spacing"],
            ["boxShadowColor", "colors"],
            ["caretColor", "colors"],
            ["divideColor", "borderColor"],
            ["divideOpacity", "borderOpacity"],
            ["divideWidth", "borderWidth"],
            ["gap", "spacing"],
            ["gradientColorStops", "colors"],
            ["inset", "spacing"],
            ["outlineColor", "colors"],
            ["padding", "spacing"],
            ["placeholderColor", "colors"],
            ["placeholderOpacity", "opacity"],
            ["ringOffsetColor", "colors"],
            ["scrollMargin", "spacing"],
            ["scrollPadding", "spacing"],
            ["space", "spacing"],
            ["textColor", "colors"],
            ["textDecorationColor", "colors"],
            ["textIndent", "spacing"],
            ["textOpacity", "opacity"],
            # ["", ""],
        ]
        self.extend_classes = [
            ["flexBasis", "spacing"],
            ["margin", "spacing"],
            ["maxHeight", "spacing"],
            ["maxWidth", "spacing"],
            ["minHeight", "spacing"],
            ["minWidth", "spacing"],
            ["ringColor", "colors"],
            ["ringOpacity", "opacity"],
            ["stroke", "colors"],
            ["translate", "spacing"],
            ["size", "spacing"],
            ["width", "spacing"],
            ["accentColor", "colors"],
            ["height", "spacing"],
            # ["", ""],
        ]
        for c1, c2 in self.extend_classes:
            self.classes[c1].update(self.classes[c2])
        for c1, c2 in self.copy_classes:
            self.classes[c1] = self.classes[c2]
        self.classes["from"] = {}
        self.classes["to"] = {}
        self.classes["via"] = {}
        self.classes["fromPosition"] = self.classes["toPosition"] = self.classes["viaPosition"] = {}
        for color in self.colors:
            val = self.colors[color]
            if isinstance(val, str):
                self.classes["from"][
                    color] = f"""--tw-gradient-from: {val} var(--tw-gradient-from-position);--tw-gradient-to: {val + "00" if val.startswith('#') else val} var(--tw-gradient-to-position);--tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);"""
                self.classes["via"][
                    color] = f"""--tw-gradient-to: {val + "00" if val.startswith('#') else val}  var(--tw-gradient-to-position);--tw-gradient-stops: var(--tw-gradient-from), {val} var(--tw-gradient-via-position), var(--tw-gradient-to);"""
                self.classes["to"][color] = f"""--tw-gradient-to: {val} var(--tw-gradient-to-position);"""
                continue
            clr_nos = val
            for clr_no in clr_nos:
                val = self.colors[color][clr_no]
                if color not in self.classes['from']:
                    self.classes["from"][color] = {}
                    self.classes["to"][color] = {}
                    self.classes["via"][color] = {}
                self.classes["from"][color][
                    clr_no] = f"""--tw-gradient-from: {val} var(--tw-gradient-from-position);--tw-gradient-to: {val + "00" if val.startswith('#') else val} var(--tw-gradient-to-position);--tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);"""
                self.classes["via"][color][
                    clr_no] = f"""--tw-gradient-to: {val + "00" if val.startswith('#') else val}  var(--tw-gradient-to-position);--tw-gradient-stops: var(--tw-gradient-from), {val} var(--tw-gradient-via-position), var(--tw-gradient-to);"""
                self.classes["to"][color][clr_no] = f"""--tw-gradient-to: {val} var(--tw-gradient-to-position);"""
        self.classes["fromPosition"] = {}
        self.classes["viaPosition"] = {}
        self.classes["toPosition"] = {}
        for i in range(0, 101, 5):
            # --tw-gradient-from-position
            # --tw-gradient-via-position
            # --tw-gradient-to-position
            self.classes["fromPosition"][str(i)] = f"{i}%"
            self.classes["fromPosition"][str(i) + "%"] = f"{i}%"
            self.classes["viaPosition"][str(i)] = f"{i}%"
            self.classes["viaPosition"][str(i) + "%"] = f"{i}%"
            self.classes["toPosition"][str(i)] = f"{i}%"
            self.classes["toPosition"][str(i) + "%"] = f"{i}%"
        self.dynamic_value = {
            "text": "color",
            "w": "width",
            "h": "height",
            "z": "zIndex",
            "py": "paddingTopBottom",
            "px": "paddingLeftRight",
            "m": "margin",
            "mt": "marginTop",
            "mr": "marginRight",
            "mb": "marginBottom",
            "ml": "marginLeft",
            "mx": "marginLeftRight",
            "my": "marginTopBottom",
            "p": "padding",
            "pt": "paddingTop",
            "pr": "paddingRight",
            "pb": "paddingBottom",
            "pl": "paddingLeft",
            "leading": "lineHeight",
            "tracking": "letterSpacing",
            "bg": "backgroundColor",
            "border": "borderColor",
            "rounded": "borderRadius",
            "shadow": "boxShadow",
            "basis": "flexBasis",
            "grid-cols": "gridTemplateColumns",
            "grid-rows": "gridTemplateRows",
            "order": "order",
            "duration": "transitionDuration",
            "delay": "transitionDelay",
            "ease": "transitionTimingFunction",
            "rotate": "rotate",
            "scale": "scale",
            "translate-x": "translateX",
            "translate-y": "translateY",
            "skew-x": "skewX",
            "skew-y": "skewY",
        }
        for i, j in [["m", "margin"], ["p", "padding"]]:
            for x, y in [["t", "top"], ["r", "right"], ["l", "left"], ["b", "bottom"]]:
                self.classes[j + y.capitalize()] = self.classes[j]
                self.dynamic_value[i + x] = j + "-" + y
        self.multi_requirement = {
            "marginLeftRight": ["marginRight"],
            "marginTopBottom": ["marginBottom"],
            "paddingLeftRight": ["paddingRight"],
            "paddingTopBottom": ["paddingBottom"],
            "rounded": ["borderTopLeftRadius", "borderTopRightRadius", "borderBottomRightRadius",
                        "borderBottomLeftRadius"],
            "roundedTop": ["borderTopLeftRadius", "borderTopRightRadius"],
            "roundedRight": ["borderTopRightRadius", "borderBottomRightRadius"],
            "roundedBottom": ["borderBottomLeftRadius", "borderBottomRightRadius"],
            "roundedLeft": ["borderTopLeftRadius", "borderBottomLeftRadius"],
            "roundedTopLeft": ["borderTopLeftRadius"],
            "roundedTopRight": ["borderTopRightRadius"],
            "roundedBottomRight": ["borderBottomRightRadius"],
            "roundedBottomLeft": ["borderBottomLeftRadius"],
            "border": ["borderWidth"],
            "itemsCenter": ["alignItems"],
            "justifyCenter": ["justifyContent"],
            "contentCenter": ["alignContent"],
            "placeContentCenter": ["alignContent", "justifyContent"],
            "gridCols": ["gridTemplateColumns"],
            "gridRows": ["gridTemplateRows"],
            "text": ["color"],
            "font": ["fontFamily"],
            "leading": ["lineHeight"],
        }
        for i, j in self.multi_requirement.items():
            self.classes[i] = {}
            for key in self.classes["margin"]:
                value = self.classes["margin"][key]
                for k in j:
                    self.classes[i][key] = [value, {k: value}]

        self.to_css_name = {
            "animation": "animation",
            "animationDuration": "animation-duration",
            "animationTimingFunction": "animation-timing-function",
            "animationDelay": "animation-delay",
            "animationIterationCount": "animation-iteration-count",
            "animationDirection": "animation-direction",
            "animationFillMode": "animation-fill-mode",
            "animationPlayState": "animation-play-state",
            "aria": "aria",
            "aspectRatio": "aspect-ratio",
            "backgroundImage": "background-image",
            "backgroundPosition": "background-position",
            "backgroundSize": "background-size",
            "borderRadius": "border-radius",
            "borderWidth": "border-width",
            "boxShadow": "box-shadow",
            "brightness": "brightness",
            "colors": "color",
            "columns": "columns",
            "container": "container",
            "content": "content",
            "contrast": "contrast",
            "cursor": "cursor",
            "dropShadow": "drop-shadow",
            "fill": "fill",
            "flex": "flex",
            "flexBasis": "flex-basis",
            "flexGrow": "flex-grow",
            "flexShrink": "flex-shrink",
            "fontFamily": "font-family",
            "fontSize": "font-size",
            "fontWeight": "font-weight",
            "fontStyle": "font-style",
            "fromPosition": "--tw-gradient-from-position",
            "gradientColorStopPositions": "gradient-color-stop-positions",
            "grayscale": "grayscale",
            "gridAutoColumns": "grid-auto-columns",
            "gridAutoRows": "grid-auto-rows",
            "gridColumn": "grid-column",
            "gridColumnEnd": "grid-column-end",
            "gridColumnStart": "grid-column-start",
            "gridRow": "grid-row",
            "gridRowEnd": "grid-row-end",
            "gridRowStart": "grid-row-start",
            "gridTemplateColumns": "grid-template-columns",
            "gridTemplateRows": "grid-template-rows",
            "height": "height",
            "hueRotate": "hue-rotate",
            "inset": "inset",
            "invert": "invert",
            "keyframes": "keyframes",
            "leading": "line-height",
            "letterSpacing": "letter-spacing",
            "lineHeight": "line-height",
            "listStyleType": "list-style-type",
            "listStyleImage": "list-style-image",
            "margin": "margin",
            "marginRight": "margin-right",
            "marginLeft": "margin-left",
            "marginTop": "margin-top",
            "marginBottom": "margin-bottom",
            "lineClamp": "line-clamp",
            "maxHeight": "max-height",
            "maxWidth": "max-width",
            "marginLeftRight": "margin-left",
            "marginTopBottom": "margin-top",
            "minHeight": "min-height",
            "minWidth": "min-width",
            "objectPosition": "object-position",
            "opacity": "opacity",
            "order": "order",
            "outlineOffset": "outline-offset",
            "outlineWidth": "outline-width",
            "paddingTop": "padding-top",
            "paddingBottom": "padding-bottom",
            "paddingRight": "padding-right",
            "paddingLeft": "padding-left",
            "ringColor": "ring-color",
            "ringOffsetWidth": "ring-offset-width",
            "ringOpacity": "ring-opacity",
            "ringWidth": "ring-width",
            "rotate": "rotate",
            "saturate": "saturate",
            "scale": "scale",
            "screens": "screens",
            "sepia": "sepia",
            "skew": "skew",
            "spacing": "spacing",
            "stroke": "stroke",
            "strokeWidth": "stroke-width",
            "supports": "supports",
            "data": "data",
            "toPosition": "--tw-gradient-to-position",
            "to": "--tw-gradient-to",
            "textAlign": "text-align",
            "textDecorationThickness": "text-decoration-thickness",
            "textUnderlineOffset": "text-underline-offset",
            "textTransform": "text-transform",
            "textWrap": "text-wrap",
            "transformOrigin": "transform-origin",
            "transitionDelay": "transition-delay",
            "transitionDuration": "transition-duration",
            "transitionProperty": "transition-property",
            "transitionTimingFunction": "transition-timing-function",
            "translate": "translate",
            "size": "size",
            "viaPosition": "--tw-gradient-via-position",
            "width": "width",
            "willChange": "will-change",
            "zIndex": "z-index",
            "backgroundColor": "background-color",
            "backgroundOpacity": "background-opacity",
            "borderColor": "border-color",
            "borderOpacity": "border-opacity",
            "borderSpacing": "border-spacing",
            "boxShadowColor": "box-shadow-color",
            "caretColor": "caret-color",
            "divideColor": "divide-color",
            "divideOpacity": "divide-opacity",
            "divideWidth": "divide-width",
            "gap": "gap",
            "gradientColorStops": "gradient-color-stops",
            "outlineColor": "outline-color",
            "padding": "padding",
            "paddingLeftRight": "padding-left",
            "paddingTopBottom": "padding-top",
            "placeholderColor": "placeholder-color",
            "placeholderOpacity": "placeholder-opacity",
            "ringOffsetColor": "ring-offset-color",
            "scrollMargin": "scroll-margin",
            "scrollPadding": "scroll-padding",
            "space": "space",
            "textColor": "color",
            "textDecorationColor": "text-decoration-color",
            "textIndent": "text-indent",
            "textOpacity": "text-opacity",
            "textDecoration": "text-decoration",
        }
        self.to_tailwind_name = {
            "animationNames": "animate",
            "animationTimingFunction": ["animate", "animation-timing-function"],
            "animationIterationCount": ["animate", "animation-direction"],
            "animationDirection": ["animate", "animation-direction"],
            "animationFillMode": ["animate", "animation-fill"],
            "animationPlayState": ["animate", "animation-play-state"],
            "aria": "aria",
            "aspectRatio": "aspect",
            "backgroundImage": "bg",
            "backgroundPosition": "bg",
            "backgroundSize": "bg",
            "borderRadius": "rounded",
            "borderWidth": "border",
            "boxShadow": "shadow",
            "brightness": "brightness",
            "colors": "colors",
            "columns": "columns",
            "container": "container",
            "content": "content",
            "contrast": "contrast",
            "cursor": "cursor",
            "display": [
                "block",
                "inline",
                "inline-block",
                "flex",
                "inline-flex",
                "grid",
                "inline-grid",
                "table",
                "inline-table",
                "table-row",
                "table-cell",
                "none",
                "hidden"
            ],
            "from": "from",
            "fromPosition": "from",
            "fill": "fill",
            "flex": "flex",
            "flexBasis": "basis",
            "flexGrow": "grow",
            "flexShrink": "shrink",
            "fontSmoothing": ["antialiased", "subpixel-antialiased"],
            "filter": [
                "blur",
                "brightness",
                "contrast",
                "drop-shadow",
                "grayscale",
                "hue-rotate",
                "invert",
                "saturate",
                "sepia"
            ],
            "backdrop-filter": ["backdrop"],
            "fontFamily": "font",
            "fontSize": "text",
            "fontWeight": "font",
            "fontStyle": [
                'italic',
                "not-italic",
            ],
            "gradientColorStopPositions": "gradient",
            "grayscale": "grayscale",
            "gridAutoColumns": "auto-cols",
            "gridAutoRows": "auto-rows",
            "gridColumn": "col",
            "gridColumnEnd": "col-end",
            "gridColumnStart": "col-start",
            "gridRow": "row",
            "gridRowEnd": "row-end",
            "gridRowStart": "row-start",
            "gridTemplateColumns": "grid-cols",
            "gridTemplateRows": "grid-rows",
            "height": "h",
            "hueRotate": "hue-rotate",
            "inset": "inset",
            "invert": "invert",
            "keyframes": "keyframes",
            "leading": "leading",
            "letterSpacing": "tracking",
            "lineHeight": "leading",
            "listStyleType": "list",
            "listStyleImage": "list",
            "margin": "m",
            "marginLeft": ["ml", "space-x"],
            "marginRight": "mr",
            "marginTop": ["mt", 'space-y'],
            "marginBottom": "mb",
            "lineClamp": "line-clamp",
            "maxHeight": "max-h",
            "maxWidth": "max-w",
            "minHeight": "min-h",
            "minWidth": "min-w",
            "marginLeftRight": "mx",
            "marginTopBottom": "my",
            "objectPosition": "object",
            "opacity": "opacity",
            "order": "order",
            "outlineOffset": "outline-offset",
            "outlineWidth": "outline",
            "position": [
                "static",
                "relative",
                "absolute",
                "fixed",
                "sticky"
            ],
            "ringColor": "ring",
            "ringOffsetWidth": "ring-offset",
            "ringOpacity": "ring-opacity",
            "ringWidth": "ring",
            "rotate": "rotate",
            "saturate": "saturate",
            "scale": "scale",
            "screens": "screens",
            "sepia": "sepia",
            "skew": "skew",
            "srOnly": "sr-only",
            "stroke": "stroke",
            "strokeWidth": "stroke",
            "supports": "supports",
            "data": "data",
            "to": "to",
            "toPosition": "to",
            "textAlign": "text",
            "textDecorationThickness": "decoration",
            "textUnderlineOffset": "underline-offset",
            "textTransform": [
                "uppercase",
                "lowercase",
                "capitalize",
                "normal-case",
            ],
            "textWrap": "text",
            "transformOrigin": "origin",
            "transitionDelay": "delay",
            "transitionDuration": "duration",
            "transitionProperty": "transition",
            "transitionTimingFunction": "ease",
            "translate": "translate",
            "via": "via",
            "viaPosition": "via",
            "size": "size",
            "width": "w",
            "willChange": "will-change",
            "zIndex": "z",

            "backgroundColor": "bg",
            "backgroundOpacity": "bg-opacity",
            "borderColor": "border",
            "borderOpacity": "border-opacity",
            "borderSpacing": "border-spacing",
            "boxShadowColor": "shadow",
            "caretColor": "caret",
            "divideColor": "divide",
            "divideOpacity": "divide-opacity",
            "divideWidth": "divide",
            "gap": "gap",
            "gradientColorStops": "gradient",
            "outlineColor": "outline",
            "overflow": "overflow",
            "padding": "p",
            "paddingLeft": "pl",
            "paddingRight": "pr",
            "paddingTop": "pt",
            "paddingBottom": "pb",
            "paddingLeftRight": "px",
            "paddingTopBottom": "py",
            "placeholderColor": "placeholder",
            "placeholderOpacity": "placeholder-opacity",
            "ringOffsetColor": "ring-offset",
            "scrollMargin": "scroll-m",
            "scrollPadding": "scroll-p",
            "space": "space",
            "textColor": "text",
            "textDecorationColor": "decoration",
            "textIndent": "indent",
            "textOpacity": "text-opacity",
            "textDecoration": [
                "none",  # No decoration
                "underline",  # Underline
                "overline",  # Overline
                "line-through",  # Line through
                "blink",  # Blink (not widely supported),
            ]
        }

    def _tailwind_gps_matched(self, first):
        matches = []
        for i in self.to_tailwind_name:
            gp = self.to_tailwind_name[i]
            if gp == first:
                matches.append(i)
            if isinstance(gp, list):
                if first in gp:
                    matches.append(i)
        return matches

    def merge_first_term(self, class_hyphen_list):
        possible = []
        class_hyphen_list = class_hyphen_list.copy()
        popped = []
        while class_hyphen_list:
            j = "-".join(class_hyphen_list)
            for i in self.to_tailwind_name:
                gp = self.to_tailwind_name[i]
                to_append = ["-".join(class_hyphen_list), popped[::-1]]
                if gp == j:
                    possible.append(to_append)
                if isinstance(gp, list):
                    if j in gp:
                        possible.append(to_append)
            popped.append(class_hyphen_list.pop())
        lis = []
        for i in possible:
            if i not in lis:
                lis.append(i)
        return lis

    def generate(self, page_content):
        match_classes = re.compile('class\s*=\s*["\']([^"\']+)["\']')
        classes = match_classes.findall(page_content)
        classes_list = []
        result_css = {}
        for i in classes:
            i = i.split(" ")
            for j in i:
                if j not in classes_list:
                    classes_list.append(j)
        for i in classes_list:
            ori_i = i
            opacity = i.split("/", 1)
            opacity_text = ""
            if len(opacity) == 2:
                try:
                    ori_op = opacity
                    opacity = int(opacity[-1])
                    i = ori_op[0]
                    opacity_text = f"/{opacity}"
                except Exception as e:
                    opacity = 100
            else:
                opacity = 100
            j = i.split("-")
            processors = []
            if ":" in j[0]:
                k = j[0].split(":")
                j[0] = k[-1]
                k.pop()
                processors = k
            jz = self.merge_first_term(j)
            for j2, j3 in jz:
                j = [j2]
                j.extend(j3)
                gps = self._tailwind_gps_matched(j[0])
                for gp in gps:
                    res = ""
                    gp_res = ""
                    if len(j) == 1:
                        res = self.classes[gp].get(j[0], "")
                        if not res:
                            res = self.classes[gp].get("DEFAULT", "")
                        if res:
                            gp_res = gp
                    if len(j) == 2:
                        if gp == "filter":
                            if "filter" not in j:
                                j.insert(0, "filter")
                        res = self.classes[gp].get(j[1], "")
                        if isinstance(res, dict):
                            res = res.get("DEFAULT", "")
                        if j[-1].startswith("["):
                            gp_res = self.dynamic_value.get(j[0], "")
                            if gp_res:
                                res = j[-1].replace("[", "").replace("]", "")
                                if gp_res in self.multi_requirement:
                                    res = [res]
                                    for z in self.multi_requirement[gp_res]:
                                        res.append({z: res[0]})
                            else:
                                if not res:
                                    res = j[-1].replace("[", "").replace("]", "")
                        if res:
                            gp_res = gp
                    if len(j) == 3:
                        res = self.classes[gp].get(j[1], {}).get(j[2], "")
                        if j[-1].startswith("["):
                            if not res:
                                res = j[-1].replace("[", "").replace("]", "")
                        if res:
                            gp_res = gp
                    if len(j) == 4:
                        res = self.classes[gp].get(j[1], {}).get(j[2], {}).get(j[3], "")
                        if j[-1].startswith("["):
                            if not res:
                                res = j[-1].replace("[", "").replace("]", "")
                        if res:
                            gp_res = gp
                    if res:
                        if (isinstance(res, str) or (isinstance(res, list) and isinstance(res[0], str))) and gp not in [
                                "from", "to", "via"]:
                            result_css_to_add = (".%s {%s: %s;}" %
                                                 (
                                                     self.sanitize_class_name(ori_i),
                                                     self.to_css_name.get(gp_res, gp_res),
                                                     self.normalize_property_value(res)
                                                 )
                                                 )
                        else:
                            result_css_to_add = ".%s {%s}" % (
                                self.sanitize_class_name(ori_i), self.normalize_property_value(res))
                        result_css_to_add = self.process_result_value(result_css_to_add, processors)
                        if opacity < 100:
                            result_css_to_add = self.process_opacity(result_css_to_add, opacity)
                        result_css[self.sanitize_class_name(ori_i)] = result_css_to_add
        from_vals = [result_css[k] for k in result_css if "from-" in k]
        via_vals = [result_css[k] for k in result_css if "via-" in k]
        to_vals = [result_css[k] for k in result_css if "to-" in k]
        vals = []
        for key in list(result_css.keys()):
            if "from-" in key or "via-" in key or "to-" in key:
                del result_css[key]
                continue
            vals.append(result_css[key])
            del result_css[key]
        vals = vals + from_vals + via_vals + to_vals
        return "".join(vals)

    def process_opacity(self, css_class, opacity):
        hex_regex = re.compile(r"[ '\"]#[0-9a-fA-F]{3,8}")
        hexes = hex_regex.findall(css_class)
        hexes = sorted(hexes, key=len, reverse=True)
        for _hex in hexes:
            char1 = _hex[0]
            rgba = self.hex_to_rgb(_hex[1:])
            if rgba[3] == 1:
                rgba[3] = opacity / 100
            rgba = f"rgba({', '.join([str(i) for i in rgba])})"
            css_class = css_class.replace(_hex, char1 + rgba)
        return css_class

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        if len(hex_color) == 8:
            a = int(hex_color[6:8], 16) / 255.0
        else:
            a = 1.0
        return [r, g, b, a]

    @staticmethod
    def process_result_value(result, processors):
        fin = ""
        # List of Media Query Processors
        media_query_processors = [
            "sm",  # min-width: 640px
            "md",  # min-width: 768px
            "lg",  # min-width: 1024px
            "xl",  # min-width: 1280px
            "2xl",  # min-width: 1536px
            "print",  # applies to print media
            "dark",  # prefers-color-scheme: dark
            "motion-safe",  # prefers-reduced-motion: no-preference
            "motion-reduce"  # prefers-reduced-motion: reduce
            "max-sm",
            "max-md",
            "max-lg",
            "max-xl",
            "max-2xl",
        ]

        # List of Pseudo-class Processors
        pseudo_class_processors = [
            "hover",  # :hover
            "focus",  # :focus
            "active",  # :active
            "visited",  # :visited
            "first",  # :first-child
            "last",  # :last-child
            "odd",  # :nth-child(odd)
            "even",  # :nth-child(even)
            "disabled",  # :disabled
            "group-hover",  # .group:hover .element
            "focus-within",  # :focus-within
            "focus-visible",  # :focus-visible
            "checked",  # :checked
            "required",  # :required
            "invalid",  # :invalid
            "before",  # ::before
            "after",  # ::after
            "first-of-type",  # :first-of-type
            "last-of-type",  # :last-of-type
            "only-child",  # :only-child
            "only-of-type",  # :only-of-type
            "empty",  # :empty
            "read-only",  # :read-only
            "placeholder-shown",  # :placeholder-shown
            "not-first",  # :not(:first-child)
            "not-last",  # :not(:last-child)
            "not-disabled",  # :not(:disabled)
            "not-checked",  # :not(:checked)
            "not-odd",  # :not(:nth-child(odd))
            "not-even",  # :not(:nth-child(even))
            "peer-hover",  # :hover on a sibling with the class 'peer'
            "peer-focus",  # :focus on a sibling with the class 'peer'
            "peer-active",  # :active on a sibling with the class 'peer'
            "peer-checked",  # :checked on a sibling with the class 'peer'
            "peer-required",  # :required on a sibling with the class 'peer'
            "peer-invalid",  # :invalid on a sibling with the class 'peer'
            "peer-placeholder-shown",  # :placeholder-shown on a sibling with the class 'peer'
        ]

        # List of Pseudo-element Processors
        pseudo_element_processors = [
            "before",  # ::before
            "after",  # ::after
            "first-letter",  # ::first-letter
            "first-line",  # ::first-line
            "marker",  # ::marker
            "selection",  # ::selection
            "backdrop",  # ::backdrop
            "placeholder"  # ::placeholder
        ]

        # Order processors
        ordered_processors_list = []
        ordered_processors_list.extend(pseudo_element_processors)
        ordered_processors_list.extend(pseudo_class_processors)
        ordered_processors_list.extend(media_query_processors)

        processors_ordered = []
        for processor in ordered_processors_list:
            if processor in processors:
                processors_ordered.append(processor)

        # Process the result based on the ordered processors
        for processor in processors_ordered:
            if processor == "dark":
                fin = "@media (prefers-color-scheme: dark) {%s}" % result
            elif processor == "light":
                fin = "@media (prefers-color-scheme: light) {%s}" % result
            elif processor == "hover":
                result = result.split(" {", 1)
                fin = result[0] + ":hover {" + result[1]
            elif processor == "focus":
                result = result.split(" {", 1)
                fin = result[0] + ":focus {" + result[1]
            elif processor == "active":
                result = result.split(" {", 1)
                fin = result[0] + ":active {" + result[1]
            elif processor == "visited":
                result = result.split(" {", 1)
                fin = result[0] + ":visited {" + result[1]
            elif processor == "first":
                result = result.split(" {", 1)
                fin = result[0] + ":first-child {" + result[1]
            elif processor == "last":
                result = result.split(" {", 1)
                fin = result[0] + ":last-child {" + result[1]
            elif processor == "odd":
                result = result.split(" {", 1)
                fin = result[0] + ":nth-child(odd) {" + result[1]
            elif processor == "even":
                result = result.split(" {", 1)
                fin = result[0] + ":nth-child(even) {" + result[1]
            elif processor == "disabled":
                result = result.split(" {", 1)
                fin = result[0] + ":disabled {" + result[1]
            elif processor == "group-hover":
                result = result.split(" {", 1)
                fin = ".group:hover " + result[0] + " {" + result[1]
            elif processor == "focus-within":
                result = result.split(" {", 1)
                fin = result[0] + ":focus-within {" + result[1]
            elif processor == "focus-visible":
                result = result.split(" {", 1)
                fin = result[0] + ":focus-visible {" + result[1]
            elif processor == "checked":
                result = result.split(" {", 1)
                fin = result[0] + ":checked {" + result[1]
            elif processor == "required":
                result = result.split(" {", 1)
                fin = result[0] + ":required {" + result[1]
            elif processor == "invalid":
                result = result.split(" {", 1)
                fin = result[0] + ":invalid {" + result[1]
            elif processor == "before":
                result = result.split(" {", 1)
                fin = result[0] + "::before {" + result[1]
            elif processor == "after":
                result = result.split(" {", 1)
                fin = result[0] + "::after {" + result[1]
            elif processor == "first-of-type":
                result = result.split(" {", 1)
                fin = result[0] + ":first-of-type {" + result[1]
            elif processor == "last-of-type":
                result = result.split(" {", 1)
                fin = result[0] + ":last-of-type {" + result[1]
            elif processor == "only-child":
                result = result.split(" {", 1)
                fin = result[0] + ":only-child {" + result[1]
            elif processor == "only-of-type":
                result = result.split(" {", 1)
                fin = result[0] + ":only-of-type {" + result[1]
            elif processor == "empty":
                result = result.split(" {", 1)
                fin = result[0] + ":empty {" + result[1]
            elif processor == "read-only":
                result = result.split(" {", 1)
                fin = result[0] + ":read-only {" + result[1]
            elif processor == "placeholder-shown":
                result = result.split(" {", 1)
                fin = result[0] + ":placeholder-shown {" + result[1]
            elif processor == "not-first":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:first-child) {" + result[1]
            elif processor == "not-last":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:last-child) {" + result[1]
            elif processor == "not-disabled":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:disabled) {" + result[1]
            elif processor == "not-checked":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:checked) {" + result[1]
            elif processor == "not-odd":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:nth-child(odd)) {" + result[1]
            elif processor == "not-even":
                result = result.split(" {", 1)
                fin = result[0] + ":not(:nth-child(even)) {" + result[1]
            elif processor == "peer-hover":
                result = result.split(" {", 1)
                fin = ".peer:hover ~ " + result[0] + " {" + result[1]
            elif processor == "peer-focus":
                result = result.split(" {", 1)
                fin = ".peer:focus ~ " + result[0] + " {" + result[1]
            elif processor == "peer-active":
                result = result.split(" {", 1)
                fin = ".peer:active ~ " + result[0] + " {" + result[1]
            elif processor == "peer-checked":
                result = result.split(" {", 1)
                fin = ".peer:checked ~ " + result[0] + " {" + result[1]
            elif processor == "peer-required":
                result = result.split(" {", 1)
                fin = ".peer:required ~ " + result[0] + " {" + result[1]
            elif processor == "peer-invalid":
                result = result.split(" {", 1)
                fin = ".peer:invalid ~ " + result[0] + " {" + result[1]
            elif processor == "peer-placeholder-shown":
                result = result.split(" {", 1)
                fin = ".peer:placeholder-shown ~ " + result[0] + " {" + result[1]
            elif processor in ["sm", "md", "lg", "xl", "2xl"]:
                media_queries = {
                    "xs": "(min-width: 425px)",
                    "sm": "(min-width: 640px)",
                    "md": "(min-width: 768px)",
                    "lg": "(min-width: 1024px)",
                    "xl": "(min-width: 1280px)",
                    "2xl": "(min-width: 1536px)",
                    "max-xs": "(max-width: 425px)",
                    "max-sm": "(max-width: 640px)",
                    "max-md": "(max-width: 768px)",
                    "max-lg": "(max-width: 1024px)",
                    "max-xl": "(max-width: 1280px)",
                    "max-2xl": "(max-width: 1536px)",
                }
                fin = "@media %s {%s}" % (media_queries[processor], result)
            elif processor == "motion-safe":
                fin = "@media (prefers-reduced-motion: no-preference) {%s}" % result
            elif processor == "motion-reduce":
                fin = "@media (prefers-reduced-motion: reduce) {%s}" % result
            elif processor == "print":
                fin = "@media print {%s}" % result
            else:
                print("UNDEFINED PROCESSSOR :", processor)
                return ""
            if fin:
                result = fin
        if not fin and not processors:
            return result
        return fin.replace(";;", ";")

    @staticmethod
    def sanitize_class_name(name):
        name = (name.replace("[", "\\[").replace("]", "\\]").replace("%", "\\%").replace(":", "\\:")
                .replace("/", "\\/").replace("(", "\\(").replace(")", "\\)").replace("#", "\\#").replace(",", "\\,"))
        if name.startswith("space-x") or name.startswith("space-y"):
            name += " > * + *"
        return name

    def normalize_property_value(self, value):
        result = ""
        if isinstance(value, list):
            if len(value) == 2:
                if isinstance(value[0], str) and isinstance(value[1], dict):
                    result += value[0] + ";"
                    for key in value[1]:
                        result += self.to_css_name.get(key, key) + ":" + value[1][key] + ";"
            elif isinstance(value[0], dict):
                for key in value[0]:
                    result += self.to_css_name.get(key, key) + ":" + value[0][key] + ";"
            else:
                for i in value:
                    if not isinstance(i, str):
                        break
                else:
                    result = ", ".join(value)
        elif isinstance(value, dict):
            for key, val in value.items():
                result += f"{key}:{val};"
        else:
            result = value
        return result
