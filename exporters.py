def chart_to_png(fig):
    return fig.to_image(format="png", scale=2)

def chart_to_svg(fig):
    return fig.to_image(format="svg")
