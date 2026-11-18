# Provided by QTrans: aluminum superconductivity tutorial plotting script.
# Updated: 2026-11-10
# Read a2f.dat and write a2f_lambda.png in the current working directory.

"""Plot the Eliashberg spectrum and cumulative electron-phonon coupling."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


INPUT_FILE = Path("a2f.dat")
OUTPUT_FILE = Path("a2f_lambda.png")
FIGURE_SIZE = (6, 6)
OUTPUT_DPI = 900


def main():
    """Load the spectrum, integrate the coupling, and save the figure."""
    # The nonmagnetic output contains phonon energy (meV) and alpha^2 F.
    spectrum = np.loadtxt(INPUT_FILE)
    omega = spectrum[:, 0]
    a2f = spectrum[:, 1]

    # lambda(omega) = 2 * integral[alpha^2 F(omega') / omega'] d omega'.
    # Treat the zero-energy contribution as zero to avoid division by zero.
    integrand = np.divide(a2f, omega, out=np.zeros_like(a2f), where=omega > 0)
    lambda_cumulative = 2.0 * np.cumsum(integrand * np.gradient(omega))

    # Use the same axes for the spectrum and the dimensionless coupling.
    with plt.rc_context({"axes.linewidth": 1}):
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        ax.plot(
            omega,
            a2f,
            color="blue",
            linewidth=2,
            alpha=0.75,
            label=r"$\mathregular{\alpha^2 F(\omega)}$",
        )
        ax.plot(
            omega,
            lambda_cumulative,
            color="black",
            linewidth=2,
            linestyle="--",
            label=r"$\mathregular{\lambda(\omega)}$",
        )

        # Match the energy window and styling of the aluminum tutorial.
        ax.set_xlim(0, 50)
        ax.set_ylim(0, 1.0)
        ax.set_xlabel(r"$\omega$ (meV)", fontsize=16)
        ax.tick_params(axis="both", labelsize=16)
        ax.legend(loc="upper left", fontsize=14)
        ax.grid(True)
        fig.tight_layout()
        fig.savefig(OUTPUT_FILE, dpi=OUTPUT_DPI)
        plt.close(fig)

    print(f"Saved figure to {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
