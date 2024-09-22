from .designations import legend, except_icons

def use_special_rules(icon: str) -> str:
    if icon == "7-":
        return f"{icon} "
    else:
        return icon

async def get_legend(text: str = "") -> str:
    points = []
    if not text:
        for icon, description in legend.items():
            icon=use_special_rules(icon)
            points.append(f"{icon} — {description}")
    else:
        for icon in legend.keys():
            if icon in text and not (icon in except_icons):
                description = legend.get(icon, "❌")
            else:
                continue
            icon=use_special_rules(icon)
            points.append(f"{icon} — {description}")

    points_str = "\n".join(points)
    return f"<b>Обозначения</b>\n\n{points_str}"